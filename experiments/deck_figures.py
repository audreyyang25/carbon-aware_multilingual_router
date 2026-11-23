"""Headline figures for the talk deck, from the stored lambda-sweep results.

Compares GreenServ and carbon_pt at the lambda pair where their accuracy is closest:
main set GreenServ 0.3 vs carbon_pt 0.7, low-resource set GreenServ 0.3 vs carbon_pt 0.5.

    python -m experiments.deck_figures            # writes results/figures/deck/*.png

fig1_model_mix_by_zone.png   test-phase model share: GreenServ (same in every zone) vs carbon_pt per zone
fig2_carbon_vs_accuracy.png  carbon vs accuracy for the chosen pair, other lambdas faint
fig3_zones.png               per zone, GreenServ -> carbon_pt in carbon and accuracy
fig4_language_mix.png        model share of the carbon routers with and without language features
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent / "results"
MAIN = ROOT / "lambda_sweep"
LOW = ROOT / "lowres" / "lambda_sweep"
OUT = Path(__file__).resolve().parent.parent / "results" / "figures" / "deck"
OUT.mkdir(parents=True, exist_ok=True)

PAIR = {"main": {"greenserv": 0.3, "carbon_pt": 0.7}, "low": {"greenserv": 0.3, "carbon_pt": 0.5}}
MODELS = ["qwen3.5-2b", "tiny-aya-global", "gemma-4-e4b", "qwen3.5-9b", "qwen3.5-27b", "gemma-4-31b"]
MODEL_LABELS = ["Qwen3.5 2B", "Tiny Aya", "Gemma 4 E4B", "Qwen3.5 9B", "Qwen3.5 27B", "Gemma 4 31B"]
MODEL_COLORS = plt.cm.viridis(np.linspace(0.05, 0.95, len(MODELS)))
ZONES = [("SE-SE3", "Sweden"), ("FR", "France"), ("DE", "Germany"), ("US-CAL-CISO", "California"),
         ("US-NE-ISNE", "New England"), ("PL", "Poland")]
ROUTER_COLORS = {"greenserv": "tab:gray", "carbon_pt": "tab:blue"}
ROUTER_NAMES = {"greenserv": "GreenServ", "carbon_pt": "carbon_pt"}

# where each value label sits, in points from its marker
LABEL_AT = {"main": {"greenserv": ((12, -14), "left"), "carbon_pt": ((-14, 10), "right")},
            "low": {"greenserv": ((0, -44), "right"), "carbon_pt": ((-14, -22), "right")}}
ZONE_LABEL_AT = {"Sweden": ((12, 0), "left"), "France": ((-12, 4), "right"), "Germany": ((-12, 6), "right"),
                 "California": ((12, 0), "left"), "New England": ((-12, -14), "right"), "Poland": ((-12, 0), "right")}

plt.rcParams.update({"font.size": 13, "axes.titlesize": 14, "savefig.dpi": 200, "savefig.bbox": "tight"})


def headline(sweep, router, lam):
    """Per-zone headline rows for one router and lambda, from whichever run holds it."""
    sub = "carbon_pt" if router == "carbon_pt" else ""
    pattern = f"{sub}/lambda_{lam}/*/analysis/headline.csv" if sub else f"lambda_{lam}/*/analysis/headline.csv"
    files = sorted(sweep.glob(pattern))
    if not files and lam == 0.5 and sweep == MAIN:  # main-set lambda 0.5 run predates the sweep folder
        files = sorted(ROOT.glob("2026*/analysis/headline.csv"))
    h = pd.read_csv(files[0])
    return h[h["strategy"] == router].set_index("zone")


def stacked(ax, rows, labels):
    left = np.zeros(len(rows))
    for j, color in enumerate(MODEL_COLORS):
        vals = np.array([r[j] for r in rows]) * 100
        ax.barh(range(len(rows)), vals, left=left, color=color, edgecolor="white", height=0.7,
                label=MODEL_LABELS[j])
        for i, v in enumerate(vals):
            if v >= 9:
                ax.text(left[i] + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=11,
                        color="white" if j < 4 else "black")
        left += vals
    ax.set_yticks(range(len(rows)), labels)
    if not ax.yaxis_inverted():
        ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("share of test queries (%)")


# ---- Figure 1: model mix by zone, main set ----
mix_zone = pd.read_csv(MAIN / "comparison" / "model_mix_by_zone.csv").drop_duplicates(["strategy", "lambda", "zone"])
gs = mix_zone[(mix_zone.strategy == "greenserv") & (mix_zone["lambda"] == 0.3)].iloc[0][MODELS].to_numpy(float)
cp = mix_zone[(mix_zone.strategy == "carbon_pt") & (mix_zone["lambda"] == 0.7)].set_index("zone")
rows = [gs] + [cp.loc[z, MODELS].to_numpy(float) for z, _ in ZONES]
labels = ["GreenServ λ=0.3\n(every zone)"] + [f"carbon_pt λ=0.7\n{name}" for _, name in ZONES]
fig, ax = plt.subplots(figsize=(11, 4.6))
stacked(ax, rows, labels)
ax.axhline(0.5, color="black", lw=1)
ax.legend(ncol=6, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False, fontsize=11,
          handlelength=1.2, columnspacing=1.2)
fig.savefig(OUT / "fig1_model_mix_by_zone.png")
plt.close(fig)

# ---- Figure 2: carbon vs accuracy, chosen pair bold ----
fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
for ax, (key, sweep, title) in zip(axes, [("main", MAIN, "Main set"), ("low", LOW, "Low-resource set")]):
    curves = pd.read_csv(sweep / "comparison" / "lambda_headline.csv")
    pts = {}
    for router in ["greenserv", "carbon_pt"]:
        c = curves[curves.strategy == router].sort_values("lambda")
        ax.plot(c.carbon_g_per_1k, c.accuracy, "-o", color=ROUTER_COLORS[router], alpha=0.25, ms=4)
        lam = PAIR[key][router]
        row = c[c["lambda"] == lam].iloc[0]
        pts[router] = (row.carbon_g_per_1k, row.accuracy)
        ax.plot(*pts[router], "o", color=ROUTER_COLORS[router], ms=11,
                label=f"{ROUTER_NAMES[router]} λ={lam}")
        (dx, dy), ha = LABEL_AT[key][router]
        ax.annotate(f"{row.accuracy:.3f} @ {row.carbon_g_per_1k:.1f} g", pts[router], xytext=(dx, dy),
                    textcoords="offset points", fontsize=11, ha=ha, va="center")
    dc = (pts["carbon_pt"][0] / pts["greenserv"][0] - 1) * 100
    da = (pts["carbon_pt"][1] - pts["greenserv"][1]) * 100
    ax.annotate("", xy=pts["carbon_pt"], xytext=pts["greenserv"],
                arrowprops=dict(arrowstyle="->", color="black", lw=1.5, shrinkA=8, shrinkB=8))
    ax.set_title(f"{title}: {dc:+.0f}% carbon, {da:+.1f} pts accuracy".replace("-", "\u2212"))
    ax.set_xlabel("g CO$_2$ per 1,000 queries")
    ax.set_ylabel("accuracy")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right", fontsize=11)
fig.tight_layout()
fig.savefig(OUT / "fig2_carbon_vs_accuracy.png")
plt.close(fig)

# ---- Figure 3: per zone, GreenServ -> carbon_pt, main set ----
g = headline(MAIN, "greenserv", 0.3)
c = headline(MAIN, "carbon_pt", 0.7)
fig, ax = plt.subplots(figsize=(11, 4.6))
for z, name in ZONES:
    x0, y0 = g.loc[z, "carbon_g_per_1k"], g.loc[z, "accuracy"]
    x1, y1 = c.loc[z, "carbon_g_per_1k"], c.loc[z, "accuracy"]
    color = "tab:blue" if y1 >= y0 else "tab:red"
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=2, shrinkA=5, shrinkB=5))
    ax.plot(x0, y0, "o", color="tab:gray", ms=8)
    ax.plot(x1, y1, "o", color=color, ms=8)
    (dx, dy), ha = ZONE_LABEL_AT[name]
    ax.annotate(f"{name}\n{(y1 - y0) * 100:+.1f} pts, {x1 - x0:+.1f} g".replace("-", "\u2212"), (x1, y1),
                xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=11)
for router, frame in [("greenserv", g), ("carbon_pt", c)]:
    a = frame.loc["all"]
    ax.plot(a.carbon_g_per_1k, a.accuracy, "*", ms=16, color=ROUTER_COLORS[router], mec="black",
            label=f"{ROUTER_NAMES[router]}, all zones: {a.accuracy:.3f} @ {a.carbon_g_per_1k:.1f} g")
ax.plot([], [], "o", color="tab:gray", label="GreenServ λ=0.3 (same accuracy in every zone)")
ax.plot([], [], "o", color="tab:blue", label="carbon_pt λ=0.7")
ax.set_xscale("log")
ax.set_xticks([2, 5, 10, 20, 50, 100], ["2", "5", "10", "20", "50", "100"])
ax.set_ylim(0.72, 0.9)
ax.set_xlabel("g CO$_2$ per 1,000 queries (log scale)")
ax.set_ylabel("accuracy")
ax.grid(alpha=0.3)
ax.legend(loc="lower left", fontsize=10)
fig.savefig(OUT / "fig3_zones.png")
plt.close(fig)

# ---- Figure 4: do language features change the mix? lambda 0.7, pooled over zones ----
chain = [("carbon", "carbon (start)"), ("carbon_en_emb", "+ English embedding"),
         ("carbon_ml_emb", "multilingual encoder"), ("lang_carbon", "+ language label")]
fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), sharey=True)
for ax, (sweep, title) in zip(axes, [(MAIN, "Main set"), (LOW, "Low-resource set")]):
    mix = pd.read_csv(sweep / "comparison" / "model_mix.csv")
    mix = mix[mix["lambda"] == 0.7].set_index("strategy")
    stacked(ax, [mix.loc[s, MODELS].to_numpy(float) for s, _ in chain], [lab for _, lab in chain])
    ax.set_title(f"{title}, λ=0.7")
handles, labs = axes[0].get_legend_handles_labels()
fig.legend(handles, labs, ncol=6, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False,
           fontsize=11, handlelength=1.2, columnspacing=1.2)
fig.tight_layout()
fig.savefig(OUT / "fig4_language_mix.png")
plt.close(fig)

print("wrote", *sorted(p.name for p in OUT.glob("*.png")))
