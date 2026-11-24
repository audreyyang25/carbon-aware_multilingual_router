"""Sanity-check a data/generate.py output file before using it: accuracy, energy and latency per
model, truncation, zero-energy rows and sample wrong answers. Use it on the pilot before starting
the full run, and on the full run before simulating routing.

    python scripts/summarize_generations.py results/pilot_runpod.jsonl --project
    python scripts/summarize_generations.py results/generations_<gpu>.jsonl

--project estimates the full run's generation time from the file's mean latencies and the query
counts in data/preprocessed/combined.csv (useful for a pilot; meaningless for a full run).
"""
import argparse

import pandas as pd


def main():
    parser = argparse.ArgumentParser(description="Summarize a generate.py JSONL file per model")
    parser.add_argument("path", help="generate.py output (.jsonl or .jsonl.gz)")
    parser.add_argument("--project", action="store_true",
                        help="Estimate full-run hours per model from this file's latencies")
    parser.add_argument("--queries", default="data/preprocessed/combined.csv",
                        help="Full query set, for --project")
    args = parser.parse_args()

    df = pd.read_json(args.path, lines=True)  # compression inferred from the extension
    pd.set_option("display.width", 200)
    print("rows", len(df), "| hardware", df.hardware.unique().tolist(),
          "| energy method", df.energy_method.unique().tolist(),
          "| data center", df["datacenter"].unique().tolist() if "datacenter" in df else None)
    df["truncated"] = df["truncated"].fillna(False).astype(bool)

    g = df.groupby(["model_id", "dataset"]).agg(
        n=("accuracy", "size"),
        acc=("accuracy", "mean"),
        energy_J=("energy_consumption", "mean"),
        latency_s=("latency", "mean"),
        in_tok=("input_tokens", "mean"),
        out_tok=("output_tokens", "mean"),
        truncated=("truncated", "mean"),
    ).round(3)
    print("\nby model x dataset:\n" + g.to_string())
    by_lang = df.pivot_table(index="model_id", columns="language", values="accuracy").round(2)
    print("\naccuracy by model x language:\n" + by_lang.to_string())

    # A long generation that reads 0 J means the energy counter failed for that row
    zero = df[(df.energy_consumption <= 0) & (df.latency > 2)]
    print("\nzero-energy rows longer than 2 s:", len(zero), zero.source_id.tolist()[:10])
    hit = df[df.truncated]
    print("hit max_new_tokens:", len(hit), hit.groupby(["model_id", "dataset"]).size().to_dict())

    if args.project:
        full = pd.read_csv(args.queries, usecols=["dataset"]).groupby("dataset").size()
        hours = g["latency_s"].unstack("dataset").mul(full).sum(axis=1, min_count=1) / 3600
        print("\nprojected full-run hours per model (generation only; excludes downloads and model loading):")
        print(hours.round(1).to_string(), f"\ntotal ≈ {hours.sum():.1f} h")

    wrong = df[df.accuracy < 1]
    for (model, ds), sub in wrong.groupby(["model_id", "dataset"]):
        print(f"\n--- wrong {model} / {ds}: {len(sub)} of {((df.model_id == model) & (df.dataset == ds)).sum()}")
        for r in sub.head(2).itertuples():
            out = r.generated_output.replace("\n", " ")
            print(f"  {r.source_id} ref={r.reference!r} out_tail={out[-120:]!r}")


if __name__ == "__main__":
    main()
