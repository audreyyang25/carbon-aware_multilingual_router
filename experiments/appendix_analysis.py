"""Appendix figures that back up the two main claims, on both sets.

Claim 1, carbon awareness changes model choice:
    figA1_mechanism.png        share of test queries sent to the two largest models vs grid intensity,
                               GreenServ vs carbon_pt (the mechanism behind fig1 and fig3)
    figA2_zone_differences.png carbon_pt minus GreenServ per zone, accuracy (points) and carbon (g per 1k; % in the CSV),
                               with 95% paired bootstrap CIs over test items
Claim 2, language features barely matter:
    figA3_language_ablation.png  accuracy and worst-language accuracy along the language-feature chain
                                 (carbon_no_flesch -> + English embedding -> multilingual encoder ->
                                 + language label) at each matched carbon level
    figA4_item_vs_language.png   why: each model's accuracy by language (rankings barely change), and how
                                 much of each model's right/wrong pattern the item explains vs the language
Context:
    figA5_grid_zones.png       hourly carbon intensity per zone in 2025: distribution and average day

    python -m experiments.appendix_analysis       # writes experiments/results/figures/appendix/*.png

Uses the same GreenServ / carbon_pt lambda pair as experiments.main_analysis (closest accuracy).
figA1 and figA2 read the per-decision steps.csv.gz of those runs, which are not committed: re-run the
two simulations first (README, Level 2). The others read committed files only.
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

from experiments.analyze_per_lambda import language_order, paired_bootstrap
from experiments.main_analysis import RESULTS, ROUTER_COLORS, ZONES, closest_pair

ROOT = Path(__file__).resolve().parent.parent
GENERATIONS = {"main": ROOT / "runpod_generations" / "generations_NVIDIA-A100-SXM4-80GB.jsonl",
               "low": ROOT / "runpod_generations" / "generations_lowres_NVIDIA-A100-SXM4-80GB.jsonl.gz"}
ZONE_TZ = {"SE-SE3": "Europe/Stockholm", "FR": "Europe/Paris", "DE": "Europe/Berlin",
           "US-CAL-CISO": "America/Los_Angeles", "US-NE-ISNE": "America/New_York", "PL": "Europe/Warsaw"}
ZONE_COLORS = dict(zip([z for z, _ in ZONES], plt.cm.viridis(np.linspace(0.1, 0.9, len(ZONES)))))
CHAIN = [("carbon_no_flesch", "no Flesch\n(3 topic clusters)"), ("carbon_en_emb", "+ English\nembedding"),
         ("carbon_ml_emb", "multilingual\nencoder"), ("lang_carbon", "+ language\nlabel")]

plt.rcParams.update({"font.size": 12, "axes.titlesize": 13, "savefig.dpi": 200, "savefig.bbox": "tight"})


def model_sizes():
    sizes = yaml.safe_load(open(ROOT / "config" / "models.yaml"))
    return {m: float(v["parameter_count"]) for m, v in sizes.items()}


def run_dir(sweep, router, lam):
    """The stored run for one router and lambda (base routers in lambda_<l>/, carbon_pt in carbon_pt/)."""
    sub = sweep / "carbon_pt" if router == "carbon_pt" else sweep
    dirs = sorted((sub / f"lambda_{lam}").glob("*/"))
    if len(dirs) != 1:
        raise FileNotFoundError(f"Expected one run in {sub / f'lambda_{lam}'}, found {len(dirs)}")
    return dirs[0]


def test_steps(path, router):
    """Test-phase decisions of one router (its own bandit rows only), read in chunks."""
    if not (path / "steps.csv.gz").exists():
        raise FileNotFoundError(f"{path}/steps.csv.gz is missing: re-run that simulation (README, Level 2)")
    cols = ["run", "strategy", "phase", "source_id", "language", "model", "accuracy", "carbon_g", "ci", "zone", "router"]
    parts = []
    for chunk in pd.read_csv(path / "steps.csv.gz", usecols=cols, chunksize=2_000_000):
        parts.append(chunk[(chunk.phase == "test") & (chunk.strategy == router) & (chunk.router == router)])
    return pd.concat(parts, ignore_index=True).drop(columns=["phase", "router"])


def item_of(source_id):
    """xnli_es_0936 -> xnli_0936: the same question in every language."""
    dataset, _, number = source_id.split("_")
    return f"{dataset}_{number}"


def load_sets(args):
    sets = {}
    for key, set_dir, title in [("main", args.main_dir, "Main set (8 languages)"),
                                ("low", args.lowres_dir, "Low-resource set (Belebele, 14 languages)")]:
        sweep = set_dir / "lambda_sweep"
        curves = pd.read_csv(sweep / "comparison" / "lambda_headline.csv")
        sets[key] = {"sweep": sweep, "title": title, "pair": closest_pair(curves)}
    return sets


def paired_steps(s):
    """GreenServ and carbon_pt test decisions on the same streams (same seed -> same queries and hours)."""
    g = test_steps(run_dir(s["sweep"], "greenserv", s["pair"]["greenserv"]), "greenserv")
    c = test_steps(run_dir(s["sweep"], "carbon_pt", s["pair"]["carbon_pt"]), "carbon_pt")
    key = ["zone", "run", "source_id"]
    check = g[key + ["ci"]].merge(c[key + ["ci"]], on=key, suffixes=("_g", "_c"))
    if len(check) != len(g) or not np.array_equal(check.ci_g, check.ci_c):
        raise ValueError("GreenServ and carbon_pt runs are not on the same streams; were they run with the same seed?")
    return pd.concat([g, c], ignore_index=True)


def fig_mechanism(sets, steps, out):
    sizes = model_sizes()
    large = sorted(sizes, key=sizes.get)[-2:]
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), sharey=True)
    for ax, (key, s) in zip(axes, sets.items()):
        d = steps[key].assign(large=lambda x: x.model.isin(large))
        edges = np.unique(np.quantile(d.ci, np.linspace(0, 1, 11)))
        d["bin"] = pd.cut(d.ci, edges, include_lowest=True)
        for router in ["greenserv", "carbon_pt"]:
            b = d[d.strategy == router].groupby("bin", observed=True).agg(ci=("ci", "median"), large=("large", "mean"))
            ax.plot(b.ci, b.large * 100, "-o", color=ROUTER_COLORS[router], ms=6,
                    label=f"{'GreenServ' if router == 'greenserv' else 'carbon_pt'} λ={s['pair'][router]}")
        ax.set_xscale("log")
        ax.set_xticks([10, 30, 100, 300, 900], ["10", "30", "100", "300", "900"])
        ax.set_xlabel("grid carbon intensity at decision time (g CO$_2$/kWh, log scale)")
        ax.set_title(s["title"])
        ax.grid(alpha=0.3)
    axes[0].set_ylabel(f"% of test queries to\n{' or '.join(large)}")
    axes[0].legend(loc="upper right")
    fig.text(0.5, -0.04, "Points are deciles of grid intensity, pooled over zones and runs.", ha="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "figA1_mechanism.png")
    plt.close(fig)


def carbon_diff_g(test, items, a, b, zone=None, n_boot=2000, seed=0):
    """a minus b in g CO2 per 1,000 queries, with a 95% paired bootstrap CI over items (as paired_bootstrap)."""
    sub = test[test.strategy.isin([a, b])]
    if zone:
        sub = sub[sub.zone == zone]
    wide = sub.pivot_table(index=["zone", "run", "source_id"], columns="strategy", values="carbon_g", aggfunc="first").dropna()
    groups = wide.index.get_level_values("source_id").map(items)
    diff = (wide[a] - wide[b]).groupby(groups).sum().to_numpy()
    counts = wide.groupby(groups).size().to_numpy()
    boot = np.random.default_rng(seed).integers(0, len(counts), (n_boot, len(counts)))
    point = diff.sum() / counts.sum() * 1000
    draws = diff[boot].sum(axis=1) / counts[boot].sum(axis=1) * 1000
    lo, hi = np.percentile(draws, [2.5, 97.5])
    return {"carbon_diff_g_per_1k": point, "carbon_g_lo": lo, "carbon_g_hi": hi}


def fig_zone_differences(sets, steps, out):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6), sharey=True)
    zones = [z for z, _ in ZONES]
    names = dict(ZONES)
    rows = []
    for key, s in sets.items():
        d = steps[key]
        items = {sid: item_of(sid) for sid in d.source_id.unique()}
        for zone in zones + [None]:
            r = paired_bootstrap(d, items, "carbon_pt", "greenserv", zone)
            r.update(carbon_diff_g(d, items, "carbon_pt", "greenserv", zone))
            rows.append({"set": key, "zone": zone or "all", **r})
    table = pd.DataFrame(rows)
    labels = [names[z] for z in zones] + ["All zones"]
    y = np.arange(len(labels))
    offset = {"main": -0.15, "low": 0.15}
    marker = {"main": "o", "low": "s"}
    for ax, (metric, lo, hi, xlabel) in zip(axes, [
            ("acc_diff_pp", "acc_lo", "acc_hi", "accuracy change (points)"),
            ("carbon_diff_g_per_1k", "carbon_g_lo", "carbon_g_hi", "carbon change (g CO$_2$ per 1,000 queries)")]):
        for key, s in sets.items():
            t = table[table.set == key].set_index("zone").loc[zones + ["all"]]
            ax.errorbar(t[metric], y + offset[key], xerr=[t[metric] - t[lo], t[hi] - t[metric]], fmt=marker[key],
                        color="tab:blue" if key == "main" else "tab:orange", capsize=3, ms=6,
                        label=f"{'Main' if key == 'main' else 'Low-resource'}: carbon_pt λ={s['pair']['carbon_pt']} "
                              f"vs GreenServ λ={s['pair']['greenserv']}")
        ax.axvline(0, color="black", lw=1)
        ax.axhline(len(zones) - 0.5, color="gray", lw=0.8, ls=":")
        ax.set_xlabel(xlabel)
        ax.grid(axis="x", alpha=0.3)
    axes[0].set_yticks(y, labels)
    axes[0].invert_yaxis()
    axes[0].legend(loc="lower left", fontsize=9, bbox_to_anchor=(0, 1.0), frameon=False)
    fig.text(0.5, -0.03, "95% CIs from a paired bootstrap over test items (each item in all its languages, all runs).",
             ha="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "figA2_zone_differences.png")
    plt.close(fig)
    table.round(4).to_csv(out / "figA2_zone_differences.csv", index=False)


def fig_language_ablation(sets, out):
    """Same y-range width on both sets, so differences look as big as they are."""
    span = {"accuracy": 0.12, "worst_language_acc": 0.16}
    fig, axes = plt.subplots(2, 2, figsize=(12, 7.6), sharex=True)
    for col, (key, s) in enumerate(sets.items()):
        abl = pd.read_csv(s["sweep"] / "comparison" / "ablation.csv")
        abl = abl[abl.router.isin([r for r, _ in CHAIN])].dropna(subset=["accuracy"])
        levels = [c for c, n in abl.groupby("carbon_g_per_1k").size().items() if n >= 2]  # a line needs 2 points
        colors = plt.cm.plasma(np.linspace(0.1, 0.8, len(levels)))
        for row, metric in enumerate(["accuracy", "worst_language_acc"]):
            ax = axes[row, col]
            for level, color in zip(levels, colors):
                v = abl[abl.carbon_g_per_1k == level].set_index("router").reindex([r for r, _ in CHAIN])[metric]
                ax.plot(range(len(CHAIN)), v, "-o", color=color, ms=6, label=f"{level:g} g per 1k")
            vals = abl[abl.carbon_g_per_1k.isin(levels)][metric]
            mid = (vals.min() + vals.max()) / 2
            ax.set_ylim(mid - span[metric] / 2, mid + span[metric] / 2)
            ax.grid(alpha=0.3)
            if col == 0:
                ax.set_ylabel("accuracy" if metric == "accuracy" else "worst-language accuracy")
        axes[0, col].set_title(s["title"])
        axes[1, col].set_xticks(range(len(CHAIN)), [lab for _, lab in CHAIN], fontsize=10)
        axes[1, col].legend(fontsize=9, title="matched carbon", title_fontsize=9, ncol=len(levels),
                            loc="upper center", bbox_to_anchor=(0.5, -0.22), frameon=False)
    fig.text(0.5, -0.06, "Each line reads every router's λ curve at the same carbon level; missing points are "
                         "outside that router's carbon range. Each row uses the same y-range width on both sets.",
             ha="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "figA3_language_ablation.png")
    plt.close(fig)


def eta_squared(y, groups):
    """Share of the variance in y explained by group means, adjusted for the number of groups.

    Raw eta^2 grows with the number of groups by chance (600 items vs 8 languages), so it is
    adjusted like R^2: 1 - (1 - eta^2) (N - 1) / (N - k).
    """
    total = ((y - y.mean()) ** 2).sum()
    if not total:
        return np.nan
    means = y.groupby(groups).transform("mean")
    eta = ((means - y.mean()) ** 2).sum() / total
    n, k = len(y), groups.nunique()
    return 1 - (1 - eta) * (n - 1) / (n - k)


def fig_item_vs_language(sets, out):
    sizes = model_sizes()
    models = sorted(sizes, key=sizes.get)
    colors = dict(zip(models, plt.cm.viridis(np.linspace(0.05, 0.95, len(models)))))
    fig, axes = plt.subplots(2, 2, figsize=(13, 7.6), gridspec_kw={"width_ratios": [1.7, 1]})
    rows = []
    for row, (key, s) in enumerate(sets.items()):
        g = pd.read_json(GENERATIONS[key], lines=True)[["item_id", "language", "model_id", "accuracy"]]
        by_lang = g.groupby(["model_id", "language"]).accuracy.mean().unstack()
        order = by_lang.mean().sort_values(ascending=False).index
        ax = axes[row, 0]
        for m in models:
            ax.plot(range(len(order)), by_lang.loc[m, order], "-o", color=colors[m], ms=4, label=m)
        ax.set_xticks(range(len(order)), order, fontsize=10)
        ax.set_ylabel("accuracy")
        ax.set_title(f"{s['title']}: accuracy by language")
        ax.grid(alpha=0.3)
        ax = axes[row, 1]
        for m in models:
            sub = g[g.model_id == m]
            rows.append({"set": key, "model": m, "item": eta_squared(sub.accuracy, sub.item_id),
                         "language": eta_squared(sub.accuracy, sub.language)})
        t = pd.DataFrame([r for r in rows if r["set"] == key]).set_index("model").loc[models]
        y = np.arange(len(models))
        ax.barh(y - 0.2, t["item"] * 100, height=0.4, color="tab:green", label="item")
        ax.barh(y + 0.2, t["language"] * 100, height=0.4, color="tab:purple", label="language")
        ax.set_yticks(y, models, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel("% of variance in right/wrong explained")
        ax.set_title("item vs language")
        ax.grid(axis="x", alpha=0.3)
    axes[1, 1].legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=10, frameon=False)
    axes[0, 0].legend(fontsize=9, ncol=2, loc="lower left")
    fig.text(0.5, -0.06, "Left: languages ordered by mean accuracy over models. Right: adjusted η² of each model's 0/1 "
                         "correctness grouped by item (the same question in every language) or by language.",
             ha="center", fontsize=10)
    fig.tight_layout()
    fig.savefig(out / "figA4_item_vs_language.png")
    plt.close(fig)
    pd.DataFrame(rows).round(4).to_csv(out / "figA4_item_vs_language.csv", index=False)


def fig_grid_zones(grid_dir, out):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1, 1.3]})
    data = []
    for zone, name in ZONES:
        g = pd.read_csv(grid_dir / f"{zone}.csv", parse_dates=["datetime"])
        g["hour"] = g.datetime.dt.tz_convert(ZONE_TZ[zone]).dt.hour
        data.append((zone, name, g))
    axes[0].boxplot([g.carbon_intensity for _, _, g in data], orientation="horizontal", whis=(5, 95), showfliers=False,
                    patch_artist=True, boxprops={"facecolor": "white"})
    axes[0].set_yticks(range(1, len(data) + 1), [name for _, name, _ in data])
    axes[0].invert_yaxis()
    axes[0].set_xscale("log")
    axes[0].set_xticks([10, 30, 100, 300, 900], ["10", "30", "100", "300", "900"])
    axes[0].set_xlabel("g CO$_2$/kWh (log scale; box 25–75%, whiskers 5–95%)")
    axes[0].set_title("Hourly intensity, 2025")
    axes[0].grid(axis="x", alpha=0.3)
    for zone, name, g in data:
        day = g.groupby("hour").carbon_intensity.mean()
        axes[1].plot(day.index, day.values, "-", color=ZONE_COLORS[zone], lw=2, label=name)
    axes[1].set_yscale("log")
    axes[1].set_yticks([10, 30, 100, 300, 900], ["10", "30", "100", "300", "900"])
    axes[1].set_xticks(range(0, 24, 3))
    axes[1].set_xlabel("local hour of day")
    axes[1].set_ylabel("mean g CO$_2$/kWh (log scale)")
    axes[1].set_title("Average day")
    axes[1].grid(alpha=0.3)
    axes[1].legend(fontsize=9, loc="center left", bbox_to_anchor=(1.01, 0.5), frameon=False)
    fig.tight_layout()
    fig.savefig(out / "figA5_grid_zones.png")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--main-dir", type=Path, default=RESULTS)
    parser.add_argument("--lowres-dir", type=Path, default=RESULTS / "lowres")
    parser.add_argument("--grid-dir", type=Path, default=ROOT / "data" / "grid")
    parser.add_argument("--out", type=Path, default=RESULTS / "figures" / "appendix")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    sets = load_sets(args)
    for s in sets.values():
        print(f"{s['title']}: GreenServ λ={s['pair']['greenserv']} vs carbon_pt λ={s['pair']['carbon_pt']}")
    fig_language_ablation(sets, args.out)
    fig_item_vs_language(sets, args.out)
    fig_grid_zones(args.grid_dir, args.out)
    try:
        steps = {key: paired_steps(s) for key, s in sets.items()}
    except FileNotFoundError as e:
        print(f"Skipping figA1 and figA2: {e}")
    else:
        fig_mechanism(sets, steps, args.out)
        fig_zone_differences(sets, steps, args.out)
    print("wrote", args.out, *sorted(p.name for p in args.out.glob("*.png")))


if __name__ == "__main__":
    main()
