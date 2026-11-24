"""Measure the router's own encoder energy per query, on the same GPU as the LLM results.

A deployed router embeds every incoming query before choosing a model, so routers that use an
encoder (GreenServ's semantic clusters, the multilingual embedding) are charged this energy in
experiments/run.py. Queries are embedded one at a time, as they would arrive in deployment, and
energy is read over the whole batch of queries (more precise than per-query readings).

    python scripts/measure_encoder_energy.py            # on the Pod, next to data/generate.py
    -> runpod_generations/encoder_energy_<gpu>.json
"""
import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import pandas as pd
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import load_config
from experiments.simulation.data import hardware_slug
from src.feature_extractor.language import MultilingualEmbeddingExtractor
from src.metrics.energy import EnergyMeasurement


def detect_device(device_id, energy_method):
    """Same GPU naming and energy defaults as data/generate.py."""
    if torch.cuda.is_available():
        return f"cuda:{device_id}", torch.cuda.get_device_name(device_id), energy_method or "zeus"
    if torch.backends.mps.is_available():
        name = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"],
                              capture_output=True, text=True).stdout.strip() or "Apple silicon"
        return "mps", name, energy_method or "apple"
    sys.exit("No CUDA or MPS device found: encoder energy can only be measured on a GPU.")


def main():
    parser = argparse.ArgumentParser(description="Measure router encoder energy per query")
    parser.add_argument("--input", default="data/preprocessed/combined.csv")
    parser.add_argument("--encoders", nargs="*", default=["multilingual_embedding", "english_embedding"])
    parser.add_argument("--queries", type=int, default=500, help="Queries per measurement")
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--energy-method", choices=["zeus", "pynvml", "apple"])
    parser.add_argument("--device", type=int, default=0)
    args = parser.parse_args()

    device, hardware, energy_method = detect_device(args.device, args.energy_method)
    feature_config = load_config("feature_extraction")["feature_extraction"]
    queries = pd.read_csv(args.input, keep_default_na=False)
    # Same mix of benchmarks and languages as the full set
    sample = queries.sample(n=min(args.queries, len(queries)), random_state=0)["processed_input"].tolist()
    meter = EnergyMeasurement.create(method=energy_method, device_id=args.device)

    out = {"hardware": hardware, "energy_method": energy_method, "device": device,
           "queries_per_measurement": len(sample), "repeats": args.repeats,
           "timestamp": datetime.now(timezone.utc).isoformat(), "encoders": {}}
    for section in args.encoders:
        config = feature_config[section]
        extractor = MultilingualEmbeddingExtractor({**config, "device": device})
        extractor.encode(sample[:20])  # warm-up: kernels, caches

        joules, seconds = [], []
        for _ in range(args.repeats):
            meter.start()
            start = time.time()
            for text in sample:
                extractor.encode([text])  # one query at a time, as in deployment
            seconds.append(time.time() - start)
            joules.append(meter.stop())
        j_per_query = sum(joules) / (args.repeats * len(sample))
        out["encoders"][section] = {
            "encoder": config["encoder"],
            "j_per_query": j_per_query,
            "ms_per_query": 1000 * sum(seconds) / (args.repeats * len(sample)),
            "j_per_repeat": joules,
        }
        print(f"{config['encoder']}: {j_per_query:.4f} J/query, "
              f"{out['encoders'][section]['ms_per_query']:.1f} ms/query on {hardware}")

    os.makedirs("runpod_generations", exist_ok=True)
    path = os.path.join("runpod_generations", f"encoder_energy_{hardware_slug(hardware)}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Saved {path}")


if __name__ == "__main__":
    main()
