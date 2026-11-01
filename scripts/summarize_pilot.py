"""Summarize a generate.py JSONL: accuracy/energy/latency by dataset x language,
zero-energy rows, MGSM rows that hit the token cap, and sample wrong answers.

    python scripts/summarize_pilot.py results/pilot_m4.jsonl
"""
import json, sys
import pandas as pd

path = sys.argv[1]
df = pd.DataFrame([json.loads(l) for l in open(path) if l.strip()])
pd.set_option("display.width", 200)
print("rows", len(df), "hardware", df.hardware.unique(), "method", df.energy_method.unique())

g = df.groupby(["dataset", "language"]).agg(
    n=("accuracy", "size"),
    acc=("accuracy", "mean"),
    energy_J=("energy_consumption", "mean"),
    latency_s=("latency", "mean"),
    in_tok=("input_tokens", "mean"),
    out_tok=("output_tokens", "mean"),
    out_tok_max=("output_tokens", "max"),
).round(3)
print(g.to_string())
print("\nby language:\n", df.groupby("language")[["accuracy", "energy_consumption", "latency"]].mean().round(3).to_string())
print("\nJ per output token (mgsm):", (df[df.dataset == "mgsm"].energy_consumption / df[df.dataset == "mgsm"].output_tokens).describe().round(3).to_string())

zero = df[(df.energy_consumption <= 0) & (df.latency > 2)]
print("\nzero-energy long rows:", len(zero), zero.source_id.tolist())
# Newer runs record "truncated"; the first M4 pilot predates it and used a 512 cap
capped = df["truncated"].fillna(False).astype(bool) if "truncated" in df else df.output_tokens >= 512
hit = df[(df.dataset == "mgsm") & capped]
print("mgsm hit token cap:", len(hit), hit.source_id.tolist())
nostop = df[(df.dataset == "mgsm") & (~df.generated_output.str.contains("####"))]
print("mgsm without '####':", len(nostop), "of", (df.dataset == "mgsm").sum())

wrong = df[df.accuracy < 1]
for (ds, lang), sub in wrong.groupby(["dataset", "language"]):
    print(f"\n--- wrong {ds}/{lang}: {len(sub)}")
    for r in sub.head(4).itertuples():
        out = r.generated_output.replace("\n", " ")
        print(f"  {r.source_id} ref={r.reference!r} out_tail={out[-120:]!r}")
