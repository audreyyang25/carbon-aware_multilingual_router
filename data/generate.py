"""Run every model on every preprocessed query and record accuracy + GPU energy.

Runs directly on a GPU (no Redis/Postgres needed) and appends one JSON line per
(query, model) to --output. Re-running skips pairs that are already done, so it is
safe to resume after a crash or a Pod restart. Load the file locally afterwards with:

    python data/ingest.py --results-file results/generations_<gpu>.jsonl

Carbon is not computed here: energy (J) is stored and turned into gCO2 offline with
grid intensity at simulation time, so one GPU run serves every grid zone.

Pilot example:
    python data/generate.py --models qwen3.5-2b qwen3.5-9b gemma-4-e4b \\
        --languages en sw --items-per-dataset 30
"""
import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone

import pandas as pd
import torch

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import load_config
from src.services.evaluation_service import EvaluationService
from src.services.inference_service import InferenceService

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("generate")


def load_queries(path, datasets=None, languages=None, items_per_dataset=None):
    """Read preprocessed queries; optionally keep the first N items of each dataset (same items in every language)."""
    df = pd.read_csv(path, dtype={"reference": str}, keep_default_na=False)
    if datasets:
        df = df[df["dataset"].isin(datasets)]
    if languages:
        df = df[df["language"].isin(languages)]
    if items_per_dataset:
        keep = set()
        for _, items in df.groupby("dataset")["item_id"]:
            keep.update(sorted(items.unique())[:items_per_dataset])
        df = df[df["item_id"].isin(keep)]
    return df.reset_index(drop=True)


def completed_pairs(output_path):
    """(source_id, model_id) pairs already written to the output file."""
    done = set()
    if os.path.exists(output_path):
        with open(output_path) as f:
            for line in f:
                if line.strip():
                    row = json.loads(line)
                    done.add((row["source_id"], row["model_id"]))
    return done


def main():
    parser = argparse.ArgumentParser(description="Generate (query x model) results on a GPU")
    parser.add_argument("--input", default="data/preprocessed/combined.csv")
    parser.add_argument("--output", help="JSONL path (default: results/generations_<gpu>.jsonl)")
    parser.add_argument("--models", nargs="*", help="Model ids from config/models.yaml (default: all)")
    parser.add_argument("--datasets", nargs="*")
    parser.add_argument("--languages", nargs="*")
    parser.add_argument("--items-per-dataset", type=int, help="Pilot: first N items per dataset")
    parser.add_argument("--energy-method", default="zeus", choices=["zeus", "pynvml"])
    parser.add_argument("--device", type=int, default=0)
    args = parser.parse_args()

    if not torch.cuda.is_available():
        sys.exit("No CUDA device found: energy can only be measured on a GPU.")
    hardware = torch.cuda.get_device_name(args.device)
    output_path = args.output or os.path.join(
        "results", f"generations_{re.sub(r'[^A-Za-z0-9]+', '-', hardware).strip('-')}.jsonl"
    )
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

    model_configs = load_config("models")
    model_ids = args.models or list(model_configs)
    unknown = [m for m in model_ids if m not in model_configs]
    if unknown:
        sys.exit(f"Unknown model ids {unknown}; choose from {list(model_configs)}")
    # Smallest first, so problems show up before the long downloads
    model_ids.sort(key=lambda m: float(model_configs[m]["parameter_count"]))

    queries = load_queries(args.input, args.datasets, args.languages, args.items_per_dataset)
    done = completed_pairs(output_path)
    logger.info(
        f"{len(queries)} queries x {len(model_ids)} models on {hardware}; "
        f"{len(done)} pairs already in {output_path}"
    )

    service = InferenceService(
        redis_client=None,
        general_configs=load_config("general"),
        model_configs=model_configs,
        device_id=args.device,
        energy_method=args.energy_method,
    )
    evaluator = EvaluationService()

    with open(output_path, "a") as out:
        for model_id in model_ids:
            todo = queries[[(sid, model_id) not in done for sid in queries["id"]]]
            if todo.empty:
                logger.info(f"{model_id}: already complete")
                continue
            logger.info(f"{model_id}: {len(todo)} queries to run")
            start = time.time()
            scores, energies = [], []

            for i, q in enumerate(todo.itertuples(), 1):
                generation_parameters = {
                    "max_new_tokens": int(q.max_new_tokens),
                    "stop_sequence": q.stop_sequence,
                }
                try:
                    result = service.run_inference(q.processed_input, model_id, generation_parameters)
                except torch.cuda.OutOfMemoryError:
                    torch.cuda.empty_cache()
                    logger.error(f"{model_id} OOM on {q.id}; skipped (re-run to retry)")
                    continue

                metrics = result["metrics"]
                accuracy = evaluator.evaluate(
                    result["response"],
                    q.reference,
                    extraction_method=q.extraction_method,
                    evaluation_metric=q.evaluation_metric,
                )
                row = {
                    "source_id": q.id,
                    "item_id": q.item_id,
                    "dataset": q.dataset,
                    "language": q.language,
                    "model_id": model_id,
                    "generated_output": result["response"],
                    "reference": q.reference,
                    "accuracy": accuracy,
                    "energy_consumption": metrics["energy_consumption"],  # joules, GPU only
                    "latency": metrics["latency"],
                    "input_tokens": metrics["input_tokens"],
                    "output_tokens": metrics["output_tokens"],
                    "hardware": hardware,
                    "energy_method": args.energy_method,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
                out.write(json.dumps(row, ensure_ascii=False) + "\n")
                out.flush()
                scores.append(accuracy)
                energies.append(metrics["energy_consumption"])

                if i == 5 and not any(energies):
                    sys.exit("Energy reads 0 J for the first 5 queries; check the energy method on this Pod.")
                if i % 50 == 0 or i == len(todo):
                    logger.info(
                        f"{model_id} {i}/{len(todo)}: accuracy {sum(scores) / len(scores):.3f}, "
                        f"mean energy {sum(energies) / len(energies):.1f} J, "
                        f"{(time.time() - start) / i:.2f} s/query"
                    )


if __name__ == "__main__":
    main()
