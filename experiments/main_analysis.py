"""Main-result figures: GreenServ vs carbon_pt, on the main and low-resource sets.

Last step of the pipeline. Reads only outputs that already exist:
    experiments.analyze         -> <run>/analysis/headline.csv   (per-zone numbers)
    experiments.lambda_compare  -> <sweep>/comparison/*.csv      (curves across lambda, model mix)

GreenServ and carbon_pt are compared at the pair of lambdas where their accuracy is closest, so
the figures show what grid awareness saves at about the same accuracy. The pair is chosen from
lambda_headline.csv for each set (currently main: GreenServ 0.3 vs carbon_pt 0.7; low-resource:
GreenServ 0.3 vs carbon_pt 0.5).

    python -m experiments.main_analysis            # writes results/figures/main_analysis/*.png

fig1_model_mix_by_zone.png   test-phase model share: GreenServ (same in every zone) vs carbon_pt per zone
fig2_carbon_vs_accuracy.png  carbon vs accuracy for the chosen pair, other lambdas faint
fig3_zones.png               per zone, GreenServ -> carbon_pt in carbon and accuracy
fig4_language_mix.png        model share of the carbon routers with and without language features
"""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RESULTS = Path(__file__).resolve().parent / "results"
MODELS = ["qwen3.5-2b", "tiny-aya-global", "gemma-4-e4b", "qwen3.5-9b", "qwen3.5-27b", "gemma-4-31b"]
MODEL_LABELS = ["Qwen3.5 2B", "Tiny Aya", "Gemma 4 E4B", "Qwen3.5 9B", "Qwen3.5 27B", "Gemma 4 31B"]
MODEL_COLORS = plt.cm.viridis(np.linspace(0.05, 0.95, len(MODELS)))
ZONES = [("SE-SE3", "Sweden"), ("FR", "France"), ("DE", "Germany"), ("US-CAL-CISO", "California"),
         ("US-NE-ISNE", "New England"), ("PL", "Poland")]
ROUTER_COLORS = {"greenserv": "tab:gray", "carbon_pt": "tab:blue"}
ROUTER_NAMES = {"greenserv": "GreenServ", "carbon_pt": "carbon_pt"}
LANGUAGE_CHAIN = [("carbon", "carbon (start)"), ("carbon_en_emb", "+ English embedding"),
                  ("carbon_ml_emb", "multilingual encoder"), ("lang_carbon", "+ language label")]

# where each value label sits, in points from its marker (tuned for the current numbers)
LABEL_AT = {"main": {"greenserv": ((12, -14), "left"), "carbon_pt": ((-14, 10), "right")},
            "low": {"greenserv": ((0, -44), "right"), "carbon_pt": ((-14, -22), "right")}}
ZONE_LABEL_AT = {"Sweden": ((12, 0), "left"), "France": ((-12, 4), "right"), "Germany": ((-12, 6), "right"),
                 "California": ((12, 0), "left"), "New England": ((-12, -14), "right"), "Poland": ((-12, 0), "right")}

plt.rcParams.update({"font.size": 13, "axes.titlesize": 14, "savefig.dpi": 200, "savefig.bbox": "tight"})


def closest_pair(curves):
    """{router: lambda} for GreenServ and carbon_pt at the lambdas where their accuracy is closest."""
    g = curves[curves.strategy == "greenserv"][["lambda", "accuracy"]]
    c = curves[curves.strategy == "carbon_pt"][["lambda", "accuracy"]]
    pairs = g.merge(c, how="cross", suffixes=("_g", "_c"))
    best = pairs.loc[(pairs.accuracy_c - pairs.accuracy_g).abs().idxmin()]
    return {"greenserv": float(best.lambda_g), "carbon_pt": float(best.lambda_c)}


def zone_headline(s, router, lam):
    """Per-zone headline rows for one router and lambda.

    Searches every analyzed run of this set for one at this lambda whose all-zone accuracy
    matches lambda_headline.csv, so the per-zone numbers come from the same run as the curves.
    """
    curves = s["curves"]
    target = curves[(curves.strategy == router) & (curves["lambda"] == lam)].accuracy.iloc[0]
    for path in sorted(s["dir"].rglob("analysis/headline.csv")):
        if any(path.resolve().is_relative_to(e.resolve()) for e in s["exclude"]):
            continue
        config = json.loads((path.parent.parent / "config.json").read_text())
        if config["args"]["lambda_weight"] != lam:
            continue
        h = pd.read_csv(path)
        h = h[h.strategy == router].set_index("zone")
        if len(h) and np.isclose(h.loc["all", "accuracy"], target):
            return h
    raise FileNotFoundError(f"No analyzed run under {s['dir']} matches {router} at lambda {lam}")


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


def fig_model_mix_by_zone(sweep, pair, out):
    mix = pd.read_csv(sweep / "comparison" / "model_mix_by_zone.csv").drop_duplicates(["strategy", "lambda", "zone"])
    gs = mix[(mix.strategy == "greenserv") & (mix["lambda"] == pair["greenserv"])].iloc[0][MODELS].to_numpy(float)
    cp = mix[(mix.strategy == "carbon_pt") & (mix["lambda"] == pair["carbon_pt"])].set_index("zone")
    rows = [gs] + [cp.loc[z, MODELS].to_numpy(float) for z, _ in ZONES]
    labels = [f"GreenServ λ={pair['greenserv']}\n(every zone)"] + \
             [f"carbon_pt λ={pair['carbon_pt']}\n{name}" for _, name in ZONES]
    fig, ax = plt.subplots(figsize=(11, 4.6))
    stacked(ax, rows, labels)
    ax.axhline(0.5, color="black", lw=1)
    ax.legend(ncol=6, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False, fontsize=11,
              handlelength=1.2, columnspacing=1.2)
    fig.savefig(out / "fig1_model_mix_by_zone.png")
    plt.close(fig)


def fig_carbon_vs_accuracy(sets, out):
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    for ax, (key, s) in zip(axes, sets.items()):
        pts = {}
        for router in ["greenserv", "carbon_pt"]:
            c = s["curves"][s["curves"].strategy == router].sort_values("lambda")
            ax.plot(c.carbon_g_per_1k, c.accuracy, "-o", color=ROUTER_COLORS[router], alpha=0.25, ms=4)
            lam = s["pair"][router]
            row = c[c["lambda"] == lam].iloc[0]
            pts[router] = (row.carbon_g_per_1k, row.accuracy)
            ax.plot(*pts[router], "o", color=ROUTER_COLORS[router], ms=11, label=f"{ROUTER_NAMES[router]} λ={lam}")
            (dx, dy), ha = LABEL_AT[key][router]
            ax.annotate(f"{row.accuracy:.3f} @ {row.carbon_g_per_1k:.1f} g", pts[router], xytext=(dx, dy),
                        textcoords="offset points", fontsize=11, ha=ha, va="center")
        dc = (pts["carbon_pt"][0] / pts["greenserv"][0] - 1) * 100
        da = (pts["carbon_pt"][1] - pts["greenserv"][1]) * 100
        ax.annotate("", xy=pts["carbon_pt"], xytext=pts["greenserv"],
                    arrowprops=dict(arrowstyle="->", color="black", lw=1.5, shrinkA=8, shrinkB=8))
        ax.set_title(f"{s['title']}: {dc:+.0f}% carbon, {da:+.1f} pts accuracy".replace("-", "−"))
        ax.set_xlabel("g CO$_2$ per 1,000 queries")
        ax.set_ylabel("accuracy")
        ax.grid(alpha=0.3)
        ax.legend(loc="lower right", fontsize=11)
    fig.tight_layout()
    fig.savefig(out / "fig2_carbon_vs_accuracy.png")
    plt.close(fig)


def fig_zones(s, out):
    g = zone_headline(s, "greenserv", s["pair"]["greenserv"])
    c = zone_headline(s, "carbon_pt", s["pair"]["carbon_pt"])
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
        ax.annotate(f"{name}\n{(y1 - y0) * 100:+.1f} pts, {x1 - x0:+.1f} g".replace("-", "−"), (x1, y1),
                    xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=11)
    for router, frame in [("greenserv", g), ("carbon_pt", c)]:
        a = frame.loc["all"]
        ax.plot(a.carbon_g_per_1k, a.accuracy, "*", ms=16, color=ROUTER_COLORS[router], mec="black",
                label=f"{ROUTER_NAMES[router]}, all zones: {a.accuracy:.3f} @ {a.carbon_g_per_1k:.1f} g")
    ax.plot([], [], "o", color="tab:gray", label=f"GreenServ λ={s['pair']['greenserv']} (same accuracy in every zone)")
    ax.plot([], [], "o", color="tab:blue", label=f"carbon_pt λ={s['pair']['carbon_pt']}")
    ax.set_xscale("log")
    ax.set_xticks([2, 5, 10, 20, 50, 100], ["2", "5", "10", "20", "50", "100"])
    ax.set_ylim(0.72, 0.9)
    ax.set_xlabel("g CO$_2$ per 1,000 queries (log scale)")
    ax.set_ylabel("accuracy")
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left", fontsize=10)
    fig.savefig(out / "fig3_zones.png")
    plt.close(fig)


def fig_language_mix(sets, lam, out):
    """Do language features change which models the carbon router picks? Pooled over zones."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), sharey=True)
    for ax, s in zip(axes, sets.values()):
        mix = pd.read_csv(s["sweep"] / "comparison" / "model_mix.csv")
        mix = mix[mix["lambda"] == lam].set_index("strategy")
        stacked(ax, [mix.loc[r, MODELS].to_numpy(float) for r, _ in LANGUAGE_CHAIN], [lab for _, lab in LANGUAGE_CHAIN])
        ax.set_title(f"{s['title']}, λ={lam}")
    handles, labs = axes[0].get_legend_handles_labels()
    fig.legend(handles, labs, ncol=6, loc="lower center", bbox_to_anchor=(0.5, 1.0), frameon=False,
               fontsize=11, handlelength=1.2, columnspacing=1.2)
    fig.tight_layout()
    fig.savefig(out / "fig4_language_mix.png")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--main-dir", type=Path, default=RESULTS,
                        help="Main-set runs; its lambda_sweep/comparison is the lambda_compare output")
    parser.add_argument("--lowres-dir", type=Path, default=RESULTS / "lowres", help="Low-resource runs, same layout")
    parser.add_argument("--mix-lambda", type=float, default=0.7, help="Lambda for the language-feature model mix")
    parser.add_argument("--out", type=Path, default=Path(__file__).resolve().parent.parent / "results" / "figures" / "main_analysis")
    args = parser.parse_args()

    sets = {}
    for key, set_dir, title in [("main", args.main_dir, "Main set"), ("low", args.lowres_dir, "Low-resource set")]:
        sweep = set_dir / "lambda_sweep"
        curves = pd.read_csv(sweep / "comparison" / "lambda_headline.csv")
        # The main dir also holds lowres/ and extensions/; never take a run from those
        exclude = [args.lowres_dir, args.main_dir / "extensions"] if key == "main" else []
        sets[key] = {"dir": set_dir, "exclude": exclude, "sweep": sweep, "curves": curves, "title": title,
                     "pair": closest_pair(curves)}
        print(f"{title}: GreenServ λ={sets[key]['pair']['greenserv']} vs carbon_pt λ={sets[key]['pair']['carbon_pt']}")

    args.out.mkdir(parents=True, exist_ok=True)
    fig_model_mix_by_zone(sets["main"]["sweep"], sets["main"]["pair"], args.out)
    fig_carbon_vs_accuracy(sets, args.out)
    fig_zones(sets["main"], args.out)
    fig_language_mix(sets, args.mix_lambda, args.out)
    print("wrote", args.out, *sorted(p.name for p in args.out.glob("*.png")))


if __name__ == "__main__":
    main()
