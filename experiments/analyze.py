"""Analyze one experiments/run.py output folder: tables, paired comparisons and figures.

    python -m experiments.analyze experiments/results/<timestamp>

Writes <folder>/analysis/:
    headline.csv      test phase, per zone and pooled over zones (each zone weighted equally):
                      accuracy, worst-language accuracy, gCO2 per 1k queries, J per query
    by_language.csv   test accuracy per strategy x language, pooled over zones
    by_benchmark.csv  test accuracy, gCO2 per 1k, J per query, carbon as % of always-largest and
                      share of total carbon, per strategy x benchmark, pooled over zones
    comparisons.csv   paired router-vs-reference differences with 95% bootstrap CIs over test items
    report.md         the tables above as markdown, for slides
    tradeoff.png, language_accuracy.png, model_share.png, carbon_awareness.png, learning_curve.png

Every run of run.py uses the same query order and grid start hour for every router (the seed
depends only on the run), so routers and baselines are compared on identical streams. Baselines
and the oracle are taken from one carbon-cost router's rows: they don't depend on the router,
except best_fixed and oracle, which depend on the cost function (energy routers pick them by energy).
"""
import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from config.manager import load_config  # noqa: E402

BASELINES = ["random", "smallest", "largest", "best_fixed", "oracle"]
LANGUAGES = ["en", "de", "es", "fr", "ru", "zh", "th", "sw"]


def language_order(present):
    """Main-run languages in their usual order, then any others (e.g. low-resource) alphabetically."""
    present = set(present)
    return [l for l in LANGUAGES if l in present] + sorted(present - set(LANGUAGES))
CURVE_BUCKET = 250  # training steps per learning-curve point (one grid hour at the default clock)

# (router, reference, question). Rows whose strategies aren't in the results are skipped.
COMPARISONS = [
    ("lang_carbon", "largest", "Savings vs always using the largest model"),
    ("lang_carbon", "best_fixed", "vs the best single model in hindsight"),
    ("lang_carbon", "greenserv", "vs GreenServ (energy-per-token cost, English features)"),
    ("lang_carbon", "carbon_no_flesch", "Do language + multilingual embedding help?"),
    ("lang_carbon", "carbon_onehot", "Does the embedding add beyond the language label?"),
    ("lang_carbon", "carbon_ml_emb", "Does the language label add beyond the embedding?"),
    ("carbon_ml_emb", "carbon_en_emb", "Multilingual vs English encoder"),
    ("carbon", "energy_pq", "Does seeing the grid help? (carbon vs energy cost)"),
    ("carbon", "carbon_no_flesch", "Does Flesch complexity help?"),
    ("carbon", "greenserv", "Carbon cost vs GreenServ's energy-per-token cost"),
]


def reference_router(config):
    """Router whose baseline rows are kept: the first carbon-cost one, else the first."""
    routers = config["routers"]
    return next((r for r, p in routers.items() if p["cost"] == "carbon"), next(iter(routers)))


def load_steps(run_dir, reference):
    """Test rows (bandits + the reference router's baselines) and training regret per bucket.

    steps.csv.gz repeats the baselines for every router, so it's read in chunks and filtered.
    """
    columns = ["run", "strategy", "phase", "step", "source_id", "dataset", "language", "model",
               "reward", "regret", "accuracy", "energy_j", "ci", "carbon_g", "zone", "router"]
    test, curves = [], []
    for chunk in pd.read_csv(run_dir / "steps.csv.gz", usecols=columns, chunksize=2_000_000):
        bandit = chunk["strategy"] == chunk["router"]
        train = chunk[bandit & (chunk["phase"] == "train")]
        curves.append(train.assign(bucket=train["step"] // CURVE_BUCKET)
                      .groupby(["zone", "router", "run", "bucket"])["regret"].agg(["sum", "size"]))
        keep = (chunk["phase"] == "test") & (bandit | (chunk["router"] == reference))
        test.append(chunk[keep].drop(columns=["phase", "step", "router"]))
    curves = pd.concat(curves).groupby(level=[0, 1, 2, 3]).sum()
    curves = (curves["sum"] / curves["size"]).rename("regret").reset_index()
    return pd.concat(test, ignore_index=True), curves


def headline(test):
    """Per zone x strategy: mean and std over runs; plus an 'all' zone averaging the zones."""
    per_run = test.groupby(["zone", "strategy", "run"]).agg(
        accuracy=("accuracy", "mean"),
        carbon_g_per_1k=("carbon_g", lambda c: c.mean() * 1000),
        energy_j=("energy_j", "mean"),
        reward=("reward", "mean"),
    )
    by_lang = test.groupby(["zone", "strategy", "run", "language"])["accuracy"].mean().unstack()
    per_run["worst_language_acc"] = by_lang.min(axis=1)
    per_run["worst_language"] = by_lang.idxmin(axis=1)

    numeric = per_run.drop(columns="worst_language")
    pooled = numeric.groupby(["strategy", "run"]).mean().assign(zone="all")
    pooled = pooled.reset_index().set_index(["zone", "strategy", "run"])
    numeric = pd.concat([numeric, pooled])
    table = numeric.groupby(["zone", "strategy"]).agg(["mean", "std"])
    table.columns = [c if s == "mean" else f"{c}_std" for c, s in table.columns]
    return table.reset_index()


def by_benchmark(test):
    """Per strategy x benchmark, test phase, zones weighted equally (mean over zones and runs).

    The pooled carbon in headline() is a mean over all test queries, and an MGSM answer uses about
    100x the energy of an XNLI or Belebele one, so pooled carbon is almost entirely MGSM. This
    splits accuracy and carbon by benchmark, and puts carbon on a common scale as a percentage of
    always using the largest model on that benchmark. `carbon_share` is the fraction of the
    strategy's total carbon spent on that benchmark.
    """
    per_run = test.groupby(["zone", "strategy", "run", "dataset"]).agg(
        accuracy=("accuracy", "mean"),
        carbon_g_per_1k=("carbon_g", lambda c: c.mean() * 1000),
        carbon_total=("carbon_g", "sum"),
        energy_j=("energy_j", "mean"),
    )
    totals = per_run.groupby(["zone", "strategy", "run"])["carbon_total"].transform("sum")
    per_run["carbon_share"] = per_run["carbon_total"] / totals
    table = per_run.drop(columns="carbon_total").groupby(["strategy", "dataset"]).mean()
    if "largest" in table.index.get_level_values("strategy"):
        largest = table.loc["largest", "carbon_g_per_1k"]
        table["carbon_vs_largest_pct"] = (
            table["carbon_g_per_1k"] / table.index.get_level_values("dataset").map(largest) * 100
        )
    return table.reset_index()


def paired_bootstrap(test, item_of, a, b, zone=None, n_boot=2000, seed=0):
    """a minus b on the same queries: accuracy in points and carbon in % of b, with 95% CIs.

    Resamples test items (each item = one question in all 8 languages, all runs and zones),
    because languages of one item and runs over the same items are not independent.
    """
    sub = test[test["strategy"].isin([a, b])]
    if zone:
        sub = sub[sub["zone"] == zone]
    wide = sub.pivot_table(index=["zone", "run", "source_id"], columns="strategy",
                           values=["accuracy", "carbon_g"], aggfunc="first").dropna()
    items = wide.index.get_level_values("source_id").map(item_of)
    per_item = wide.groupby(items).sum()
    counts = wide.groupby(items).size().to_numpy()
    acc_a, acc_b = per_item[("accuracy", a)].to_numpy(), per_item[("accuracy", b)].to_numpy()
    co2_a, co2_b = per_item[("carbon_g", a)].to_numpy(), per_item[("carbon_g", b)].to_numpy()

    def stats(idx):
        n = counts[idx].sum(axis=-1)
        acc = (acc_a[idx].sum(axis=-1) - acc_b[idx].sum(axis=-1)) / n * 100
        co2 = (co2_a[idx].sum(axis=-1) / co2_b[idx].sum(axis=-1) - 1) * 100
        return acc, co2

    acc, co2 = stats(np.arange(len(counts)))
    boot = np.random.default_rng(seed).integers(0, len(counts), (n_boot, len(counts)))
    acc_boot, co2_boot = stats(boot)
    acc_lo, acc_hi = np.percentile(acc_boot, [2.5, 97.5])
    co2_lo, co2_hi = np.percentile(co2_boot, [2.5, 97.5])
    return {"acc_diff_pp": acc, "acc_lo": acc_lo, "acc_hi": acc_hi,
            "carbon_change_pct": co2, "carbon_lo": co2_lo, "carbon_hi": co2_hi,
            "items": len(counts)}


def comparisons(test, item_of, zones):
    strategies = set(test["strategy"])
    rows = []
    for a, b, question in COMPARISONS:
        if a not in strategies or b not in strategies:
            continue
        for zone in ["all"] + zones:
            result = paired_bootstrap(test, item_of, a, b, None if zone == "all" else zone)
            rows.append({"router": a, "reference": b, "zone": zone, "question": question, **result})
    return pd.DataFrame(rows)


def strategy_order(strategies):
    routers = [s for s in strategies if s not in BASELINES]
    return routers + [b for b in BASELINES if b in strategies]


def router_colors(routers):
    """One colour per router, shared by every figure."""
    return dict(zip(routers, plt.cm.tab10.colors))


def plot_tradeoff(table, zones, routers, out):
    cols = min(3, len(zones))
    rows = int(np.ceil(len(zones) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 4 * rows), squeeze=False)
    colors = router_colors(routers)
    for ax, zone in zip(axes.flat, zones):
        z = table[table["zone"] == zone].set_index("strategy")
        for s in z.index:
            r = z.loc[s]
            if s in routers:
                style = dict(color=colors[s], marker="o", markersize=7)
            elif s == "oracle":
                style = dict(color="black", marker="*", markersize=11)
            else:
                style = dict(color="grey", marker="s", markersize=6)
            ax.errorbar(r["carbon_g_per_1k"], r["accuracy"], xerr=r["carbon_g_per_1k_std"],
                        yerr=r["accuracy_std"], linestyle="none", **style)
            if s not in routers:
                ax.annotate(s, (r["carbon_g_per_1k"], r["accuracy"]), fontsize=7, color="dimgrey",
                            xytext=(4, -9), textcoords="offset points")
        ax.set_title(zone)
        ax.set_xlabel("gCO2 per 1,000 queries")
        ax.set_ylabel("accuracy")
        ax.grid(alpha=0.3)
    for ax in axes.flat[len(zones):]:
        ax.axis("off")
    handles = [plt.Line2D([], [], color=colors[r], marker="o", linestyle="none", label=r) for r in routers]
    fig.legend(handles=handles, loc="lower center", ncol=min(len(routers), 4), frameon=False)
    fig.suptitle("Accuracy vs carbon on test queries (up and left is better; bars = std over runs)")
    fig.tight_layout(rect=(0, 0.06, 1, 0.97))
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_language_accuracy(by_language, out):
    fig, ax = plt.subplots(figsize=(max(8, 0.65 * len(by_language.columns) + 2), 0.45 * len(by_language) + 1.5))
    im = ax.imshow(by_language.to_numpy(), cmap="viridis", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(by_language.columns)), by_language.columns)
    ax.set_yticks(range(len(by_language)), by_language.index)
    for (i, j), v in np.ndenumerate(by_language.to_numpy()):
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                color="white" if v < 0.6 else "black")
    fig.colorbar(im, ax=ax, label="accuracy")
    ax.set_title("Test accuracy by language (all zones)")
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_model_share(test, routers, model_ids, out):
    cols = min(4, len(routers))
    rows = int(np.ceil(len(routers) / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 3.2 * rows), squeeze=False, sharey=True)
    colors = dict(zip(model_ids, plt.cm.viridis(np.linspace(0.1, 0.95, len(model_ids)))))
    for ax, router in zip(axes.flat, routers):
        share = (test[test["strategy"] == router].groupby("language")["model"]
                 .value_counts(normalize=True).unstack(fill_value=0))
        share = share.reindex(index=language_order(share.index), columns=model_ids, fill_value=0)
        bottom = np.zeros(len(share))
        for m in model_ids:
            ax.bar(share.index, share[m], bottom=bottom, color=colors[m], label=m)
            bottom += share[m].to_numpy()
        ax.set_title(router, fontsize=10)
        ax.set_ylim(0, 1)
    for ax in axes.flat[len(routers):]:
        ax.axis("off")
    axes[0, 0].set_ylabel("share of test queries")
    fig.legend(*axes[0, 0].get_legend_handles_labels(), loc="lower center", ncol=len(model_ids), frameon=False,
               fontsize=8)
    fig.suptitle("Which model each router picks, by language (models small to large, all zones)")
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_carbon_awareness(test, routers, out, bins=8):
    """Energy of the chosen model vs grid intensity: a carbon-aware router slopes down."""
    sub = test[test["strategy"].isin(routers)].copy()
    sub["ci_bin"] = pd.qcut(sub["ci"], bins, duplicates="drop")
    curve = sub.groupby(["strategy", "ci_bin"], observed=True).agg(ci=("ci", "mean"), energy=("energy_j", "mean"))
    colors = router_colors(routers)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for router in routers:
        c = curve.loc[router]
        ax.plot(c["ci"], c["energy"], marker="o", label=router, color=colors[router])
    ax.set_xlabel("grid carbon intensity (gCO2/kWh), binned")
    ax.set_ylabel("mean energy of chosen model (J/query)")
    ax.set_title("Does the router pick smaller models when the grid is dirty?")
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def plot_learning_curve(curves, routers, out):
    """Regret is against each router's own reward, so energy-cost routers aren't on the same scale."""
    mean = curves.groupby(["router", "bucket"])["regret"].mean().unstack(0)
    colors = router_colors(routers)
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for router in [r for r in routers if r in mean.columns]:
        ax.plot(mean.index * CURVE_BUCKET, mean[router].rolling(3, min_periods=1).mean(), label=router,
                color=colors[router])
    ax.set_xlabel("training queries seen")
    ax.set_ylabel(f"mean regret per query (per {CURVE_BUCKET} queries, smoothed)")
    ax.set_title("Learning during training (lower is better; regret on each router's own reward)", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)


def markdown_table(df, index=False):
    """Plain markdown table (pandas' to_markdown needs the tabulate package)."""
    if index:
        df = df.reset_index()
    fmt = lambda v: f"{v:.3f}" if isinstance(v, float) else str(v)
    lines = ["| " + " | ".join(map(str, df.columns)) + " |", "|" + "---|" * len(df.columns)]
    lines += ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def fmt_ci(value, lo, hi, unit):
    flag = "" if lo <= 0 <= hi else " *"
    return f"{value:+.1f}{unit} [{lo:+.1f}, {hi:+.1f}]{flag}"


def benchmark_report(bench, order):
    """Markdown for the per-benchmark section: accuracy, gCO2 per 1k and % of largest, side by side."""
    datasets = sorted(bench["dataset"].unique())
    wide = bench.pivot(index="strategy", columns="dataset")
    wide = wide.reindex([s for s in order if s in wide.index])
    acc = wide["accuracy"][datasets].add_prefix("acc ")
    co2 = wide["carbon_g_per_1k"][datasets].add_prefix("gCO2/1k ")
    parts = [acc, co2]
    if "carbon_vs_largest_pct" in wide:
        rel = wide["carbon_vs_largest_pct"][datasets]
        parts.append(rel.add_prefix("% of largest "))
        parts.append(rel.mean(axis=1).rename("% of largest, benchmarks averaged").to_frame())
    share = wide["carbon_share"][datasets].add_prefix("share of carbon ")
    return markdown_table(pd.concat(parts, axis=1), index=True), markdown_table(share, index=True)


def write_report(out_dir, config, table, by_language, comp, zones, bench_md=None):
    show = ["strategy", "accuracy", "worst_language_acc", "carbon_g_per_1k", "energy_j"]
    lines = [
        f"# Routing results: {Path(out_dir).parent.name}",
        "",
        f"- Hardware: {config['hardware']}; models: {', '.join(config['model_ids'])}",
        f"- Algorithm: {config['args']['algorithm']}, lambda = {config['args']['lambda_weight']}, "
        f"{config['args']['runs']} runs, {config['args']['queries_per_hour']} queries/hour",
        f"- Zones: {', '.join(zones)}",
        "",
        "## Test phase, averaged over zones",
        "",
        markdown_table(table[table["zone"] == "all"][show]),
        "",
        "## Paired comparisons (all zones)",
        "",
        "Router minus reference on the same queries. Accuracy in points, carbon in % of the reference. "
        "95% bootstrap CI over test items; * = CI excludes 0.",
        "",
    ]
    pooled = comp[comp["zone"] == "all"]
    if len(pooled):
        pretty = pd.DataFrame({
            "comparison": pooled["router"] + " vs " + pooled["reference"],
            "question": pooled["question"],
            "accuracy (pp)": [fmt_ci(r.acc_diff_pp, r.acc_lo, r.acc_hi, "") for r in pooled.itertuples()],
            "carbon (%)": [fmt_ci(r.carbon_change_pct, r.carbon_lo, r.carbon_hi, "%") for r in pooled.itertuples()],
        })
        lines += [markdown_table(pretty), ""]
    if bench_md:
        main_table, share_table = bench_md
        lines += [
            "## Test results by benchmark (all zones)",
            "",
            "Pooled carbon above is a mean over all test queries, so it is almost entirely MGSM "
            "(an MGSM answer uses about 100x the energy of an XNLI or Belebele one). Here each "
            "benchmark is on its own; `% of largest` puts carbon on a common scale (always using "
            "the largest model = 100), and its benchmark average weights the three equally.",
            "",
            main_table,
            "",
            "Share of each strategy's total carbon spent on each benchmark:",
            "",
            share_table,
            "",
        ]
    lines += ["## Test accuracy by language (all zones)", "", markdown_table(by_language, index=True), ""]
    for zone in zones:
        lines += [f"## {zone}", "", markdown_table(table[table["zone"] == zone][show]), ""]
    (out_dir / "report.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Analyze an experiments/run.py output folder")
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    if not (args.run_dir / "steps.csv.gz").exists():
        sys.exit(f"{args.run_dir}/steps.csv.gz not found (was run.py called with --no-steps?)")

    config = json.loads((args.run_dir / "config.json").read_text())
    reference = reference_router(config)
    test, curves = load_steps(args.run_dir, reference)
    zones = list(dict.fromkeys(test["zone"]))
    order = strategy_order(list(dict.fromkeys(test["strategy"])))
    routers = [s for s in order if s not in BASELINES]
    sizes = load_config("models")
    model_ids = sorted(config["model_ids"], key=lambda m: float(sizes[m]["parameter_count"]))
    queries = pd.read_csv(project_root / config["args"]["queries"], usecols=["id", "item_id"])
    item_of = dict(zip(queries["id"], queries["item_id"]))

    out_dir = args.run_dir / "analysis"
    out_dir.mkdir(exist_ok=True)

    table = headline(test)
    table["strategy"] = pd.Categorical(table["strategy"], order)
    table = table.sort_values(["zone", "strategy"])
    table.to_csv(out_dir / "headline.csv", index=False)

    by_language = test.groupby(["strategy", "language"])["accuracy"].mean().unstack()
    by_language = by_language.reindex(index=order, columns=language_order(by_language.columns))
    by_language["worst"] = by_language.min(axis=1)
    by_language.to_csv(out_dir / "by_language.csv")

    bench = by_benchmark(test)
    bench["strategy"] = pd.Categorical(bench["strategy"], order)
    bench = bench.sort_values(["strategy", "dataset"])
    bench.to_csv(out_dir / "by_benchmark.csv", index=False)

    comp = comparisons(test, item_of, zones)
    comp.to_csv(out_dir / "comparisons.csv", index=False)

    plot_tradeoff(table, zones, routers, out_dir / "tradeoff.png")
    plot_language_accuracy(by_language.drop(columns="worst"), out_dir / "language_accuracy.png")
    plot_model_share(test, routers, model_ids, out_dir / "model_share.png")
    plot_carbon_awareness(test, routers, out_dir / "carbon_awareness.png")
    plot_learning_curve(curves, routers, out_dir / "learning_curve.png")
    write_report(out_dir, config, table, by_language, comp, zones,
                 benchmark_report(bench.astype({"strategy": str}), order))

    print((out_dir / "report.md").read_text())
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()
