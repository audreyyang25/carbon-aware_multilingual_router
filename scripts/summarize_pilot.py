"""Summarize a generate.py JSONL per model: accuracy/energy/latency by dataset and language,
truncation, zero-energy rows, sample wrong answers, and the projected time of the full run.

    python scripts/summarize_pilot.py results/pilot_runpod.jsonl
"""
import json, sys
import pandas as pd

FULL_QUERIES_PER_DATASET = 2000  # 250 items x 8 languages in the full run

path = sys.argv[1]
df = pd.DataFrame([json.loads(l) for l in open(path) if l.strip()])
pd.set_option("display.width", 200)
print("rows", len(df), "hardware", df.hardware.unique(), "method", df.energy_method.unique(),
      "datacenter", df.get("datacenter", pd.Series([None])).unique())
# Newer runs record "truncated"; the first M4 pilot predates it and used a 512 cap
df["capped"] = df["truncated"].fillna(False).astype(bool) if "truncated" in df else df.output_tokens >= 512

g = df.groupby(["model_id", "dataset"]).agg(
    n=("accuracy", "size"),
    acc=("accuracy", "mean"),
    energy_J=("energy_consumption", "mean"),
    latency_s=("latency", "mean"),
    in_tok=("input_tokens", "mean"),
    out_tok=("output_tokens", "mean"),
    truncated=("capped", "mean"),
).round(3)
print("\nby model x dataset:\n" + g.to_string())
print("\naccuracy by model x language:\n" + df.pivot_table(index="model_id", columns="language", values="accuracy").round(2).to_string())

zero = df[(df.energy_consumption <= 0) & (df.latency > 2)]
print("\nzero-energy long rows:", len(zero), zero.source_id.tolist()[:10])
hit = df[df.capped]
print("hit token cap:", len(hit), hit.groupby(["model_id", "dataset"]).size().to_dict())

# Full run time if the full set looks like the pilot (pilot items are the first N of each benchmark)
hours = g["latency_s"].unstack("dataset").mul(FULL_QUERIES_PER_DATASET).sum(axis=1) / 3600
print("\nprojected full-run hours per model (generation only, excludes downloads and loading):")
print(hours.round(1).to_string(), f"\ntotal ≈ {hours.sum():.1f} h")

wrong = df[df.accuracy < 1]
for (model, ds), sub in wrong.groupby(["model_id", "dataset"]):
    print(f"\n--- wrong {model} / {ds}: {len(sub)} of {((df.model_id == model) & (df.dataset == ds)).sum()}")
    for r in sub.head(2).itertuples():
        out = r.generated_output.replace("\n", " ")
        print(f"  {r.source_id} ref={r.reference!r} out_tail={out[-120:]!r}")
