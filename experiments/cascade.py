"""Agreement cascade, evaluated offline on the stored answers.

Ask two cheap models; if their extracted answers agree, return the first one's answer; otherwise
escalate to a larger model. Energy is the sum of every model that ran. The grid-aware variant
sends a query straight to the largest model when the grid is cleaner than --clean-ci g/kWh.

Every model answered every query once, so a cascade needs no new generations. Carbon is paired
with the routers: each test query is charged at the grid intensity it saw in an existing run
(same zones, runs, query order and hours), read from that run's steps.csv.gz.

    python -m experiments.cascade OUT_DIR --run-dir <run with steps.csv.gz> \
        --results <generations> [--queries <queries csv>] [--comparison <lambda_compare dir>]

Writes OUT_DIR/cascade.csv (one row per variant: accuracy, worst-language accuracy, gCO2 per 1k,
escalation rate, accuracy when the pair agrees) and cascade_by_language.csv. With --comparison,
cascade.csv also gets each router's accuracy at the cascade's carbon, read off its lambda curve.
"""
import argparse
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from experiments.shared.simulation_data import load_results
from src.metrics.carbon import carbon_g
from src.metrics.extractors import canonical_number, get_extractor
from src.metrics.text_utils import TextNormalizer

CHEAP = ["qwen3.5-2b", "tiny-aya-global", "gemma-4-e4b"]
TARGETS = ["qwen3.5-9b", "qwen3.5-27b", "gemma-4-31b"]
LARGEST = "gemma-4-31b"
COMPARE = ["greenserv", "carbon_pt", "carbon", "carbon_pt_floor", "best_fixed"]

parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
parser.add_argument("out_dir", type=Path)
parser.add_argument("--run-dir", type=Path, required=True, help="Run whose test streams to replay")
parser.add_argument("--results", nargs="+", required=True)
parser.add_argument("--queries", default="data/preprocessed/combined.csv")
parser.add_argument("--clean-ci", type=float, default=100.0,
                    help="Grid-aware variant: below this g/kWh, use the largest model directly")
parser.add_argument("--comparison", type=Path, help="lambda_compare output dir (lambda_headline.csv)")
args = parser.parse_args()
args.out_dir.mkdir(parents=True, exist_ok=True)

# 1. Extracted, normalized answer for every (query, model), the way the generation run scored it
normalizer = TextNormalizer()
res = load_results(args.results)
queries = pd.read_csv(args.queries).set_index("id")
res = res[res["source_id"].isin(queries.index)].copy()
res["method"] = res["source_id"].map(queries["extraction_method"])


def answer(row):
    extracted = get_extractor(row.method).extract(row.generated_output, {"allow_fallback": not row.truncated})
    if row.method == "numeric":
        return canonical_number(extracted) if extracted else None
    text = normalizer.normalize(extracted) if extracted else ""
    return text or None


res["answer"] = [answer(r) for r in res.itertuples()]
ref = res["source_id"].map(queries["reference"]).astype(str)
ref_norm = [canonical_number(r) or r if m == "numeric" else normalizer.normalize(r)
            for r, m in zip(ref, res["method"])]
rescored = (res["answer"].astype(str) == pd.Series(ref_norm, index=res.index).astype(str)).astype(float)
agree_with_stored = (rescored == res["accuracy"]).mean()
print(f"Re-scored answers match stored accuracy on {agree_with_stored:.1%} of rows")

ans = res.pivot(index="source_id", columns="model_id", values="answer")
acc = res.pivot(index="source_id", columns="model_id", values="accuracy")
energy = res.pivot(index="source_id", columns="model_id", values="energy_consumption")

# 2. Test streams from an existing run: (zone, run, source_id, ci) for every test query
cols = ["run", "strategy", "phase", "source_id", "language", "ci", "zone"]
streams = []
for chunk in pd.read_csv(args.run_dir / "steps.csv.gz", usecols=cols, chunksize=2_000_000):
    streams.append(chunk[(chunk["phase"] == "test") & (chunk["strategy"] == "largest")])
streams = pd.concat(streams).drop_duplicates(["zone", "run", "source_id"])[["zone", "run", "source_id", "language", "ci"]]
streams = streams[streams["source_id"].isin(acc.index)]


# 3. Variants
def run_cascade(a, b, target, grid_aware):
    sid = streams["source_id"].to_numpy()
    agree = (ans.loc[sid, a].to_numpy() == ans.loc[sid, b].to_numpy()) & ans.loc[sid, a].notna().to_numpy()
    e_pair = energy.loc[sid, a].to_numpy() + energy.loc[sid, b].to_numpy()
    escalate = ~agree
    accuracy = np.where(agree, acc.loc[sid, a].to_numpy(), acc.loc[sid, target].to_numpy())
    joules = np.where(agree, e_pair, e_pair + energy.loc[sid, target].to_numpy())
    if grid_aware:
        clean = streams["ci"].to_numpy() < args.clean_ci
        accuracy = np.where(clean, acc.loc[sid, LARGEST].to_numpy(), accuracy)
        joules = np.where(clean, energy.loc[sid, LARGEST].to_numpy(), joules)
        escalate = np.where(clean, False, escalate)
    return streams.assign(accuracy=accuracy, energy_j=joules, escalated=escalate, agree=agree,
                          pair_correct=acc.loc[sid, a].to_numpy(),
                          carbon_g=carbon_g(joules, streams["ci"].to_numpy()))


def summarize(s):
    """Per zone and run, then averaged over zones and runs, as in analyze.headline."""
    per = s.groupby(["zone", "run"]).agg(accuracy=("accuracy", "mean"),
                                         carbon_g_per_1k=("carbon_g", lambda c: c.mean() * 1000),
                                         energy_j=("energy_j", "mean"), escalation=("escalated", "mean"))
    per["worst_language_acc"] = s.groupby(["zone", "run", "language"])["accuracy"].mean().unstack().min(axis=1)
    out = per.mean().to_dict()
    agreed = s[s["agree"]]
    out["acc_when_agree"] = agreed["pair_correct"].mean() if len(agreed) else np.nan
    out["agree_rate"] = s["agree"].mean()
    return out


rows, by_lang = [], []
for a, b in combinations(CHEAP, 2):
    for target in TARGETS:
        for grid_aware in (False, True):
            name = f"{a}+{b}->{target}" + (" (grid)" if grid_aware else "")
            s = run_cascade(a, b, target, grid_aware)
            rows.append({"cascade": name, "pair": f"{a}+{b}", "target": target, "grid_aware": grid_aware,
                         **summarize(s)})
            by_lang.append(s.groupby("language")["accuracy"].mean().rename(name))
table = pd.DataFrame(rows)

# 4. Routers' accuracy at each cascade's carbon, from their lambda curves
if args.comparison:
    curves = pd.read_csv(args.comparison / "lambda_headline.csv")
    for router in COMPARE:
        g = curves[curves["strategy"] == router].sort_values("carbon_g_per_1k")
        if g.empty:
            continue
        x, y = g["carbon_g_per_1k"].to_numpy(), g["accuracy"].to_numpy()
        table[f"{router}_at_same_carbon"] = [
            float(np.interp(c, x, y)) if x.min() <= c <= x.max() else np.nan for c in table["carbon_g_per_1k"]]

table = table.sort_values("carbon_g_per_1k")
table.round(4).to_csv(args.out_dir / "cascade.csv", index=False)
pd.concat(by_lang, axis=1).round(4).to_csv(args.out_dir / "cascade_by_language.csv")
show = ["cascade", "accuracy", "worst_language_acc", "carbon_g_per_1k", "escalation", "acc_when_agree"]
show += [c for c in table.columns if c.endswith("_at_same_carbon")]
print(table[show].round(3).to_string(index=False))
print(f"\nSaved to {args.out_dir}")
