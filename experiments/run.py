"""Simulate carbon-aware routing on pre-generated results.

Each run replays the training items (all languages) as a shuffled stream: the router picks a
model, gets that model's stored accuracy and energy back as a reward, and learns online. The
policy is then frozen (no updates, no exploration) and evaluated on the held-out test items. Grid intensity comes from an
hourly series for the chosen zone, starting at a different hour each run. Baselines and the
oracle see exactly the same stream and intensities, so every comparison is paired.

    python -m experiments.run --router lang_carbon --zone DE --results results/generations_*.jsonl
    python -m experiments.run --router all --zone all --results results/generations_*.jsonl
    python -m experiments.run --router lang_carbon carbon_onehot --holdout-language th --results ...

Writes experiments/results/<timestamp>/ with summary.csv (one row per zone x router x strategy x
phase, mean and std over runs), choices.csv (model share per language), steps.csv.gz and config.json.
"""
import argparse
import json
import logging
import math
import os
import random
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))
os.chdir(project_root)  # default paths (data/..., results/...) are relative to the repo root

from config.manager import load_config
from experiments.simulation.rewards import COST_FUNCTIONS, calculate_reward
from experiments.simulation.features import ContextBuilder
from experiments.simulation.data import (
    TrainBounds,
    build_query_table,
    complete_queries,
    hardware_slug,
    load_results,
)
from src.bandit.factory import create_bandit_instance
from src.metrics.carbon import CarbonNormalizer, carbon_g
from src.metrics.grid import IntensitySeries

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("experiments.run")


def parse_args(router_config, grid_config):
    defaults = router_config["defaults"]
    parser = argparse.ArgumentParser(description="Simulate LLM routers on pre-generated results")
    parser.add_argument("--router", nargs="+", required=True,
                        help=f"Profiles from routers.yaml, or 'all': {list(router_config['routers'])}")
    parser.add_argument("--zone", nargs="+", default=[next(iter(grid_config["zones"]))],
                        help=f"Zones with data in data/grid/, or 'all': {list(grid_config['zones'])}")
    parser.add_argument("--results", nargs="+", required=True, help="Result JSONL files or globs")
    parser.add_argument("--algorithm", default=defaults["algorithm"], choices=list(router_config["algorithms"]))
    parser.add_argument("--lambda", dest="lambda_weight", type=float, default=defaults["lambda"])
    parser.add_argument("--pue", type=float, default=defaults["pue"])
    parser.add_argument("--runs", type=int, default=defaults["runs"])
    parser.add_argument("--seed", type=int, default=load_config("general").get("random_seed", 40))
    parser.add_argument("--hardware", help="GPU to use if the results mix several")
    parser.add_argument("--models", nargs="*", help="Restrict the model pool (default: all in the results)")
    parser.add_argument("--holdout-language", help="Leave this language out of training entirely")
    parser.add_argument("--pca-dim", type=int,
                        help="Embedding PCA size (default: pca_dim in config/feature_extraction.yaml)")
    parser.add_argument("--queries-per-hour", type=int, default=grid_config["queries_per_hour"],
                        help="Simulation clock: decisions per hour of grid time (250 = one day for "
                             "the whole stream, 25 = ten days)")
    parser.add_argument("--queries", default="data/preprocessed/combined.csv")
    parser.add_argument("--splits", default="data/preprocessed/splits.csv")
    parser.add_argument("--grid-dir", default="data/grid", help="Zone CSVs and bounds.yaml from data/fetch_grid.py")
    parser.add_argument("--output-dir", default="experiments/results")
    parser.add_argument("--no-steps", action="store_true", help="Skip the per-step file")
    return parser.parse_args()


def load_encoder_energy(router_config, hardware):
    """{encoder section: joules per query} measured on the same GPU as the results."""
    path = router_config["encoder_energy_file"].format(hardware=hardware_slug(hardware))
    if not os.path.exists(path):
        logger.warning(f"{path} not found: encoder energy is not charged to routers "
                       f"(run scripts/measure_encoder_energy.py on this GPU)")
        return {}
    with open(path) as f:
        return {section: m["j_per_query"] for section, m in json.load(f)["encoders"].items()}


def encoder_overhead_j(profile, encoder_energy):
    """Joules per query the router spends on its own encoder(s) before routing."""
    sections = set()
    if "semantic_cluster" in profile["features"]:
        sections.add("english_embedding")
    if "embedding" in profile["features"]:
        sections.add(profile["encoder"])
    return sum(encoder_energy.get(s, 0.0) for s in sections)


def step_rewards(table, order, ci, cost_name, lambda_weight, ctx, n_models):
    """Reward of every model at every step: shape (steps, models)."""
    cost_fn = COST_FUNCTIONS[cost_name]
    rewards = np.empty((len(order), n_models))
    for t, sid in enumerate(order):
        q = table.loc[sid]
        for m in range(n_models):
            row = {
                "dataset": q["dataset"],
                "energy_consumption": q["energy"][m],
                "energy_consumption_norm": q["energy_norm"][m],
                "energy_per_token_norm": q["ept_norm"][m],
                "energy_per_token": q["energy"][m] / q["tokens"][m],
            }
            rewards[t, m] = calculate_reward(q["accuracy"][m], cost_fn(row, ci[t], ctx), lambda_weight)
    return rewards


def freeze_exploration(bandit):
    """Test phase: pick the model with the best current reward estimate, with no exploration."""
    if hasattr(bandit, "alpha"):
        bandit.alpha = 0.0  # LinUCB: drop the uncertainty bonus
    if hasattr(bandit, "epsilon"):
        bandit.epsilon = 0.0  # epsilon-greedy variants: never pick at random
    if hasattr(bandit, "greedy"):
        bandit.greedy = True  # Thompson sampling: use the posterior mean instead of a sample


def simulate_run(router_name, profile, builder, table, model_ids, series, run, seed, args,
                 router_config, ctx, overhead_j):
    """One run: train stream (online learning) then frozen evaluation on test items."""
    rng = random.Random(seed)
    is_train = table["split"] == "train"
    if args.holdout_language:
        is_train &= table["language"] != args.holdout_language
    train_ids = list(table.index[is_train])
    test_ids = list(table.index[table["split"] == "test"])
    rng.shuffle(train_ids)
    rng.shuffle(test_ids)
    order = train_ids + test_ids
    phase = ["train"] * len(train_ids) + ["test"] * len(test_ids)

    # Start the clock at a random hour that leaves room for the whole stream
    hours = math.ceil(len(order) / series.queries_per_hour) + 1
    series.start_hour = rng.randrange(0, len(series.ci) - hours)
    ci = np.array([series.at_step(t) for t in range(len(order))])

    n_models = len(model_ids)
    rewards = step_rewards(table, order, ci, profile["cost"], args.lambda_weight, ctx, n_models)
    best_fixed = int(np.argmax(rewards[: len(train_ids)].mean(axis=0)))
    sizes = load_config("models")
    by_size = sorted(range(n_models), key=lambda m: float(sizes[model_ids[m]]["parameter_count"]))

    strategies = {router_name: "bandit", "oracle": "oracle", **{b: "baseline" for b in router_config["baselines"]}}

    def new_bandit():
        b = create_bandit_instance(
            algo_name=args.algorithm,
            algo_params=router_config["algorithms"][args.algorithm],
            model_ids=list(range(n_models)),
            context_dimension=builder.dim,
            reg_lambda=router_config["algorithms"][args.algorithm].get(
                "lambda_", router_config["algorithms"][args.algorithm].get("regularization")),
            seed=seed,
        )
        if b is None:
            raise RuntimeError(f"Could not create bandit '{args.algorithm}'")
        if hasattr(b, "reset"):
            b.reset()
        return b

    random_choice = random.Random(seed + 1)
    n_train = len(train_ids)
    contexts = [builder.context(sid, ci[t]) for t, sid in enumerate(order)]

    # Per-language accuracy floors (profile `floor`), tuned by dual ascent on the training stream
    # only. Language l gets a multiplier mu_l and the bandit learns from
    #     reward + mu_l * (1 - lambda) * accuracy.
    # Each pass trains a fresh bandit with mu fixed, scores its frozen policy on the training
    # items, and raises mu_l by step * (floor_l - accuracy_l). Keeping mu fixed within a pass
    # matters: a multiplier that drifts during one pass gets averaged away by LinUCB. The floor is
    # ratio x the best single model's training accuracy in that language. Reported rewards stay
    # unaugmented.
    floor_cfg = profile.get("floor")
    bonus = np.zeros_like(rewards)
    if floor_cfg:
        step_lang = np.array([table.at[sid, "language"] for sid in order])
        step_acc = np.stack([table.at[sid, "accuracy"] for sid in order])
        train_lang, train_acc = step_lang[:n_train], step_acc[:n_train]
        floors = {l: floor_cfg["ratio"] * float(train_acc[train_lang == l].mean(axis=0).max())
                  for l in np.unique(train_lang)}
        mu = dict.fromkeys(floors, 0.0)

        def bonus_for(mu):
            w = np.array([mu[l] for l in step_lang])[:, None]
            return w * (1 - args.lambda_weight) * step_acc

        for _ in range(floor_cfg["passes"]):
            bonus = bonus_for(mu)
            b = new_bandit()
            for t in range(n_train):
                m = b.select_model(context=contexts[t])
                b.update(m, rewards[t, m] + bonus[t, m], context=contexts[t])
            freeze_exploration(b)
            picks = np.array([b.select_model(context=contexts[t]) for t in range(n_train)])
            got = train_acc[np.arange(n_train), picks]
            for l in mu:
                mu[l] = min(floor_cfg["max"], max(0.0, mu[l] + floor_cfg["step"] * (floors[l] - got[train_lang == l].mean())))
        bonus = bonus_for(mu)
        logger.info("floor multipliers: " + ", ".join(f"{l} {mu[l]:.2f} (floor {floors[l]:.2f})" for l in sorted(mu)))

    bandit = new_bandit()
    rows = []
    for strategy, kind in strategies.items():
        for t, sid in enumerate(order):
            if kind == "bandit":
                if t == n_train:
                    freeze_exploration(bandit)
                context = contexts[t]
                m = bandit.select_model(context=context)
                if phase[t] == "train":
                    bandit.update(m, rewards[t, m] + bonus[t, m], context=context)
            elif kind == "oracle":
                m = int(np.argmax(rewards[t]))
            elif strategy == "random":
                m = random_choice.randrange(n_models)
            elif strategy == "smallest":
                m = by_size[0]
            elif strategy == "largest":
                m = by_size[-1]
            elif strategy == "best_fixed":
                m = best_fixed  # best single model on this run's training stream, in hindsight
            else:
                raise ValueError(f"Unknown baseline '{strategy}'")

            q = table.loc[sid]
            overhead = overhead_j if kind == "bandit" else 0.0
            rows.append({
                "run": run, "strategy": strategy, "phase": phase[t], "step": t,
                "source_id": sid, "dataset": q["dataset"], "language": q["language"],
                "model": model_ids[m],
                "reward": rewards[t, m], "oracle_reward": rewards[t].max(),
                "regret": rewards[t].max() - rewards[t, m],
                "accuracy": q["accuracy"][m],
                "energy_j": q["energy"][m] + overhead,
                "ci": ci[t],
                "carbon_g": carbon_g(q["energy"][m] + overhead, ci[t], args.pue),
                "start_hour": series.start_hour,
            })
    return rows


def summarize(steps):
    """Per zone x router x strategy x phase: mean and std over runs."""
    keys = ["zone", "router", "strategy", "phase"]
    per_run = steps.groupby(keys + ["run"]).agg(
        queries=("reward", "size"),
        reward=("reward", "mean"),
        cumulative_regret=("regret", "sum"),
        accuracy=("accuracy", "mean"),
        carbon_g=("carbon_g", "sum"),
        energy_kj=("energy_j", lambda e: e.sum() / 1000),
    )
    by_language = steps.pivot_table(index=keys + ["run"], columns="language", values="accuracy", aggfunc="mean")
    by_language.columns = [f"acc_{c}" for c in by_language.columns]
    per_run = per_run.join(by_language)
    lang_cols = list(by_language.columns)
    per_run["acc_gap"] = per_run[lang_cols].max(axis=1) - per_run[lang_cols].min(axis=1)
    per_run["acc_worst_language"] = per_run[lang_cols].min(axis=1)

    agg = per_run.groupby(keys).agg(["mean", "std"])
    agg.columns = [f"{c}_{s}" if s == "std" else c for c, s in agg.columns]
    return agg.reset_index()


def main():
    router_config = load_config("routers")
    grid_config = load_config("grid")
    args = parse_args(router_config, grid_config)
    feature_config = load_config("feature_extraction")["feature_extraction"]

    routers = list(router_config["routers"]) if args.router == ["all"] else args.router
    unknown = [r for r in routers if r not in router_config["routers"]]
    if unknown:
        sys.exit(f"Unknown routers {unknown}; choose from {list(router_config['routers'])}")
    zones = list(grid_config["zones"]) if args.zone == ["all"] else args.zone
    zone_csv = {z: os.path.join(args.grid_dir, f"{z}.csv") for z in zones}
    zones = [z for z in zones if os.path.exists(zone_csv[z]) and os.path.getsize(zone_csv[z])]
    if not zones:
        sys.exit(f"No grid data for the requested zones in {args.grid_dir}; run data/fetch_grid.py first")
    with open(os.path.join(args.grid_dir, "bounds.yaml")) as f:
        grid_bounds = yaml.safe_load(f)
    ci_bounds = (grid_bounds["ci_min"], grid_bounds["ci_max"])

    # Results -> one row per query with per-model arrays
    results, model_ids = complete_queries(load_results(args.results, args.hardware, args.models))
    if len(model_ids) < 2:
        sys.exit(f"Need at least two models to route between; results only have {model_ids}")
    hardware = results["hardware"].iloc[0]
    table = build_query_table(results, model_ids, args.queries, args.splits)
    bounds = TrainBounds(table)
    table["energy_norm"] = [bounds.normalize("energy_consumption", e, d) for e, d in zip(table["energy"], table["dataset"])]
    table["ept_norm"] = [bounds.normalize("energy_per_token", e / n, d)
                         for e, n, d in zip(table["energy"], table["tokens"], table["dataset"])]
    ctx = {"carbon_normalizer": CarbonNormalizer(*ci_bounds, bounds, pue=args.pue)}
    encoder_energy = load_encoder_energy(router_config, hardware)

    logger.info(f"{len(table)} queries ({(table['split'] == 'train').sum()} train) x {len(model_ids)} models "
                f"on {hardware}; routers {routers}; zones {zones}; {args.algorithm}, lambda={args.lambda_weight}, "
                f"{args.queries_per_hour} queries/hour")

    out_dir = Path(args.output_dir) / datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir.mkdir(parents=True, exist_ok=True)
    all_steps = []
    for zone in zones:
        series = IntensitySeries(zone_csv[zone], args.queries_per_hour)
        for router_name in routers:
            profile = router_config["routers"][router_name]
            builder = ContextBuilder(profile, table, feature_config, ci_bounds, args.holdout_language,
                                     router_config["defaults"]["semantic_clusters"], args.pca_dim)
            overhead_j = encoder_overhead_j(profile, encoder_energy)
            for run in range(args.runs):
                rows = simulate_run(router_name, profile, builder, table, model_ids, series, run,
                                    args.seed + run, args, router_config, ctx, overhead_j)
                steps = pd.DataFrame(rows).assign(zone=zone, router=router_name)
                all_steps.append(steps)
            logger.info(f"{zone} / {router_name}: done ({args.runs} runs, context dim {builder.dim})")

    steps = pd.concat(all_steps, ignore_index=True)
    summary = summarize(steps)
    summary.to_csv(out_dir / "summary.csv", index=False)
    choices = (steps.groupby(["zone", "router", "strategy", "phase", "language"])["model"]
               .value_counts(normalize=True).rename("share").reset_index())
    choices.to_csv(out_dir / "choices.csv", index=False)
    if not args.no_steps:
        steps.to_csv(out_dir / "steps.csv.gz", index=False)
    with open(out_dir / "config.json", "w") as f:
        json.dump({
            "args": vars(args), "routers": {r: router_config["routers"][r] for r in routers},
            "model_ids": model_ids, "hardware": hardware, "ci_bounds": ci_bounds,
            "energy_bounds": bounds.bounds, "encoder_energy_j": encoder_energy,
            "algorithm_params": router_config["algorithms"][args.algorithm],
            "embedding_pca_dim": {s: args.pca_dim or feature_config[s]["pca_dim"]
                                  for s in ("multilingual_embedding", "english_embedding")},
        }, f, indent=2, default=str)

    test = summary[summary["phase"] == "test"]
    cols = ["zone", "router", "strategy", "accuracy", "acc_worst_language", "carbon_g", "reward"]
    with pd.option_context("display.width", 160, "display.max_rows", 200):
        print("\nTest phase (frozen policy, mean over runs):")
        print(test[cols].round(3).to_string(index=False))
    print(f"\nSaved to {out_dir}")


if __name__ == "__main__":
    main()
