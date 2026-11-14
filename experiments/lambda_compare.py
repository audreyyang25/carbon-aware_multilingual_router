"""Compare routers across lambda: accuracy-vs-carbon curves and accuracy at matched carbon.

Each lambda gives every router one (carbon, accuracy) point: test-phase gCO2 per 1,000 queries
and accuracy, averaged over zones (analysis/headline.csv, zone == "all"). Sweeping lambda traces
each router's trade-off curve. "Accuracy at matched carbon" reads every curve at the same carbon
level by linear interpolation between the two nearest lambda runs, so routers that landed at
different carbon levels can be compared fairly. Run experiments.analyze on each sweep first.

    python -m experiments.lambda_compare OUT_DIR 0.3=<run_dir> 0.5=<run_dir> 0.7=<run_dir> 0.9=<run_dir>

Writes OUT_DIR/: lambda_headline.csv, by_lambda_<metric>.csv, matched_carbon.csv,
lambda_tradeoff.png.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser(description="Compare routers across lambda at matched carbon")
parser.add_argument("out_dir", type=Path)
parser.add_argument("runs", nargs="+", help="LAMBDA=RUN_DIR, one per lambda")
parser.add_argument("--levels", type=float, nargs="+",
                    help="gCO2 per 1k queries to compare at (default: 5 round levels inside "
                         "the routers' carbon range)")
args = parser.parse_args()

out = args.out_dir
out.mkdir(parents=True, exist_ok=True)
frames = []
for arg in args.runs:
    lam, path = arg.split("=", 1)
    h = pd.read_csv(Path(path) / "analysis" / "headline.csv")
    h = h[h["zone"] == "all"].copy()
    h["lambda"] = float(lam)
    frames.append(h)
df = pd.concat(frames)
cols = ["lambda", "strategy", "accuracy", "worst_language_acc", "carbon_g_per_1k", "energy_j"]
df = df[cols].sort_values(["strategy", "lambda"])
df.to_csv(out / "lambda_headline.csv", index=False)

routers = ["greenserv", "energy_pq", "carbon", "carbon_no_flesch", "carbon_en_emb",
           "carbon_onehot", "carbon_ml_emb", "lang_carbon", "best_fixed"]

# Wide tables: accuracy / carbon / worst-language per strategy x lambda
for metric in ["accuracy", "carbon_g_per_1k", "worst_language_acc"]:
    t = df.pivot(index="strategy", columns="lambda", values=metric)
    t = t.loc[[s for s in routers + ["random", "smallest", "largest", "oracle"] if s in t.index]]
    t.round(3).to_csv(out / f"by_lambda_{metric}.csv")
    print(f"\n{metric}\n{t.round(3).to_string()}")


def curve(strategy, y="accuracy"):
    """(carbon, y) points sorted by carbon, for interpolation."""
    g = df[df["strategy"] == strategy].sort_values("carbon_g_per_1k")
    return g["carbon_g_per_1k"].to_numpy(), g[y].to_numpy()


def at_carbon(strategy, c, y="accuracy"):
    x, v = curve(strategy, y)
    if c < x.min() - 1e-9 or c > x.max() + 1e-9:
        return np.nan  # outside the range this router reaches
    return float(np.interp(c, x, v))


def round_levels(lo, hi, n=5):
    """About n evenly spaced round numbers (step 1, 2 or 5 x 10^k) strictly inside (lo, hi)."""
    raw = (hi - lo) / (n + 1)
    magnitude = 10 ** np.floor(np.log10(raw))
    step = min((m * magnitude for m in (1, 2, 5, 10)), key=lambda s: abs(s - raw))
    first = np.floor(lo / step) * step + step
    return [round(float(c), 6) for c in np.arange(first, hi, step)]


# Matched carbon: accuracy of every router at a few common carbon levels
router_carbon = df[df["strategy"].isin(routers)]["carbon_g_per_1k"]
levels = sorted(args.levels) if args.levels else round_levels(router_carbon.min(), router_carbon.max())
rows = []
for c in levels:
    row = {"carbon_g_per_1k": c}
    for s in routers:
        row[s] = at_carbon(s, c)
        row[s + "_worst"] = at_carbon(s, c, "worst_language_acc")
    rows.append(row)
matched = pd.DataFrame(rows)
matched.round(3).to_csv(out / "matched_carbon.csv", index=False)
print("\nAccuracy at matched carbon (NaN = router never reaches that carbon level)")
print(matched[["carbon_g_per_1k"] + routers].round(3).to_string(index=False))
print("\nWorst-language accuracy at matched carbon")
print(matched[["carbon_g_per_1k"] + [s + "_worst" for s in routers]].round(3).to_string(index=False))

# Chart: accuracy vs carbon, a few highlighted series, the rest recessive
highlight = {"lang_carbon": "#2a78d6", "best_fixed": "#eb6834",
             "greenserv": "#1baf7a", "carbon_no_flesch": "#eda100"}
muted = "#c3c2b7"
fig, ax = plt.subplots(figsize=(8, 5.2), dpi=150)
for s in routers:
    if s in highlight:
        continue
    x, v = curve(s)
    ax.plot(x, v, color=muted, lw=1.5, marker="o", ms=4, zorder=1)
for s, color in highlight.items():
    g = df[df["strategy"] == s].sort_values("lambda")
    ax.plot(g["carbon_g_per_1k"], g["accuracy"], color=color, lw=2, marker="o", ms=7,
            markeredgecolor="white", markeredgewidth=1.5, label=s, zorder=3)
for s, mk in [("largest", "s"), ("smallest", "v"), ("oracle", "*")]:
    g = df[df["strategy"] == s].iloc[0]
    ax.scatter(g["carbon_g_per_1k"], g["accuracy"], color="#73726c", marker=mk, s=60, zorder=2)
    ax.annotate(s, (g["carbon_g_per_1k"], g["accuracy"]), textcoords="offset points",
                xytext=(6, 2), fontsize=8, color="#73726c")
ax.plot([], [], color=muted, lw=1.5, marker="o", ms=4, label="other routers")
ax.set_xlabel("gCO₂ per 1,000 queries (test, averaged over zones)")
ax.set_ylabel("Test accuracy")
ax.set_title("Accuracy vs carbon as λ goes 0.3 → 0.9 (more weight on carbon)", fontsize=11, loc="left")
ax.grid(color="#e8e7e2", lw=0.8)
for side in ["top", "right"]:
    ax.spines[side].set_visible(False)
ax.legend(frameon=False, fontsize=8, loc="lower right", title="one point per λ run",
          title_fontsize=7)
fig.tight_layout()
fig.savefig(out / "lambda_tradeoff.png")
print(f"\nSaved to {out}")
