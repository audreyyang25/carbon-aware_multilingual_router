"""Check a RunPod Pod is ready for the full data/generate.py run before committing hours of GPU time.

Run after scripts/runpod_setup.sh, from the repo root, before anything else touches the GPU:

    python scripts/preflight.py              # checks only
    python scripts/preflight.py --download   # also download every model's weights to the volume now

FAIL lines must be fixed before the run; WARN lines are worth a look. Exits 1 if anything fails.
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pandas as pd
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import load_config
from src.metrics.energy import EnergyMeasurement

GB = 1e9
WEIGHT_PATTERNS = ["*.json", "*.safetensors", "*.model", "*.txt", "*.jinja", "*.tiktoken"]
failures = []


def report(status, message):
    print(f"[{status}] {message}")
    if status == "FAIL":
        failures.append(message)


def nvidia_smi(query, kind="gpu"):
    flag = "--query-gpu" if kind == "gpu" else "--query-compute-apps"
    out = subprocess.run(["nvidia-smi", f"{flag}={query}", "--format=csv,noheader,nounits"],
                         capture_output=True, text=True)
    return [line.strip() for line in out.stdout.splitlines() if line.strip()]


def check_gpu_exclusive():
    """Nothing else may use the GPU: Zeus reads the whole GPU's energy counter."""
    if shutil.which("nvidia-smi") is None:
        report("FAIL", "nvidia-smi not found: not an NVIDIA GPU Pod")
        return
    gpus = nvidia_smi("name,memory.total")
    if len(gpus) != 1:
        report("WARN", f"{len(gpus)} GPUs visible; generate.py uses --device 0 only: {gpus}")
    apps = nvidia_smi("pid,process_name,used_memory", kind="apps")
    if apps:
        report("FAIL", f"Other processes are on the GPU (they would be counted in the energy): {apps}")
    else:
        report("OK", "No other processes on the GPU")
    utilization = []
    for _ in range(5):
        utilization.append(int(nvidia_smi("utilization.gpu")[0]))
        time.sleep(0.5)
    if max(utilization) > 5:
        report("FAIL", f"GPU busy while idle ({utilization}%): something else is running on it")
    else:
        report("OK", f"GPU idle ({max(utilization)}% utilization)")


def check_gpu_memory(model_sizes):
    if not torch.cuda.is_available():
        report("FAIL", "CUDA not available in PyTorch")
        return None
    name = torch.cuda.get_device_name(0)
    total = torch.cuda.get_device_properties(0).total_memory / GB
    largest = max(model_sizes.values())
    if total < largest + 8:
        report("FAIL", f"{name} has {total:.0f} GB; the largest model needs {largest:.0f} GB plus ~8 GB for activations")
    else:
        report("OK", f"{name}, {total:.0f} GB (largest model {largest:.0f} GB)")
    return name


def check_energy_counter():
    """Zeus must see real energy, and a matmul load should draw plausible power."""
    meter = EnergyMeasurement.create(method="zeus", device_id=0)
    x = torch.randn(8192, 8192, device="cuda", dtype=torch.bfloat16)
    torch.cuda.synchronize()
    meter.start()
    start = time.time()
    while time.time() - start < 3:
        x = (x @ x).clamp_(-1, 1)
    torch.cuda.synchronize()
    seconds = time.time() - start
    joules = meter.stop()
    del x
    torch.cuda.empty_cache()
    watts = joules / seconds if joules else 0
    if not joules:
        report("FAIL", "Zeus read 0 J under load: the GPU energy counter isn't available on this Pod")
    elif not 50 < watts < 1500:
        report("WARN", f"Zeus read {joules:.0f} J in {seconds:.1f} s ({watts:.0f} W): implausible power")
    else:
        report("OK", f"Energy counter works: {joules:.0f} J in {seconds:.1f} s under load ({watts:.0f} W)")


def check_hf_access(models, token):
    from huggingface_hub import HfApi, auth_check

    if not token:
        report("FAIL", "HF_TOKEN is not set (use a RunPod secret so it survives restarts)")
    sizes = {}
    api = HfApi()
    for model_id, config in models.items():
        repo = config["name"]
        try:
            auth_check(repo, token=token)
            info = api.model_info(repo, token=token, files_metadata=True)
            sizes[model_id] = sum(s.size or 0 for s in info.siblings if s.rfilename.endswith(".safetensors")) / GB
            report("OK", f"{model_id}: access to {repo} ({sizes[model_id]:.1f} GB)")
        except Exception as e:
            report("FAIL", f"{model_id}: no access to {repo} ({type(e).__name__}); accept its license on HF")
    return sizes


def check_storage(models, sizes):
    """Cache and results must live on the volume, with room for the weights still to download."""
    volume = Path(os.environ.get("VOLUME", "/workspace")).resolve()
    cache = Path(os.path.expanduser(load_config("general").get("cache_dir", "~/.cache/huggingface"))).resolve()
    repo = Path.cwd().resolve()
    for label, path in (("Model cache", cache), ("Repo and results", repo)):
        if volume in path.parents or path == volume:
            report("OK", f"{label} on the volume: {path}")
        else:
            report("FAIL", f"{label} at {path} is not on {volume}: it is lost when the Pod stops "
                           f"(run scripts/runpod_setup.sh / clone the repo under {volume})")

    def cached_gb(repo_name):
        # Same layout as from_pretrained(cache_dir=...) in src/services/inference_service.py
        path = cache / f"models--{repo_name.replace('/', '--')}"
        return sum(f.stat().st_size for f in path.rglob("*") if f.is_file()) / GB if path.exists() else 0.0

    remaining = sum(max(0.0, sizes[m] - cached_gb(models[m]["name"])) for m in sizes)
    free = shutil.disk_usage(cache if cache.exists() else volume).free / GB
    if free < remaining + 10:
        report("FAIL", f"{free:.0f} GB free, but {remaining:.0f} GB of weights are still to download (+10 GB margin)")
    else:
        report("OK", f"{free:.0f} GB free; {remaining:.0f} GB of weights still to download")


def check_data_and_resume(gpu_name):
    queries = pd.read_csv("data/preprocessed/combined.csv", keep_default_na=False)
    if len(queries) != 6000:
        report("WARN", f"combined.csv has {len(queries)} queries, expected 6,000")
    else:
        report("OK", "6,000 queries in data/preprocessed/combined.csv")

    # data/generate.py names its output after the GPU, so a different GPU type starts a new file
    from experiments.simulation.data import hardware_slug
    expected = Path("results") / f"generations_{hardware_slug(gpu_name)}.jsonl" if gpu_name else None
    others = [p for p in Path("results").glob("generations_*.jsonl") if p != expected]
    if expected and expected.exists():
        with open(expected) as f:
            done = sum(1 for line in f if line.strip())
        report("OK", f"Resuming {expected}: {done} of 36,000 rows already done")
    if others:
        report("WARN", f"Results from other GPUs exist: {[str(p) for p in others]}. Every model must run on "
                       f"one GPU type, so don't mix them; keep the GPU type the run started on")


def check_session():
    if not os.environ.get("TMUX"):
        report("WARN", "Not inside tmux: the run stops if your SSH connection drops (tmux new -s gen)")
    if not os.environ.get("RUNPOD_DC_ID"):
        report("WARN", "RUNPOD_DC_ID not set: results won't record the data center")


def download_all(models, token):
    from huggingface_hub import snapshot_download

    cache_dir = os.path.expanduser(load_config("general").get("cache_dir", "~/.cache/huggingface"))
    for model_id, config in models.items():
        print(f"Downloading {model_id} ({config['name']})...")
        snapshot_download(config["name"], token=token, cache_dir=cache_dir, allow_patterns=WEIGHT_PATTERNS)
    report("OK", "All model weights downloaded")


def main():
    parser = argparse.ArgumentParser(description="Check a Pod is ready for the full generation run")
    parser.add_argument("--download", action="store_true", help="Download every model's weights now")
    args = parser.parse_args()

    models = load_config("models")
    token = os.environ.get("HF_TOKEN")
    check_gpu_exclusive()  # before this process creates its own CUDA context
    sizes = check_hf_access(models, token)
    gpu_name = check_gpu_memory(sizes or {"none": 0})
    if gpu_name:
        check_energy_counter()
    if sizes:
        check_storage(models, sizes)
    check_data_and_resume(gpu_name)
    check_session()
    if args.download and not failures:
        download_all(models, token)

    print()
    if failures:
        print(f"{len(failures)} check(s) failed; fix them before the full run.")
        sys.exit(1)
    print("Ready for the full run.")


if __name__ == "__main__":
    main()
