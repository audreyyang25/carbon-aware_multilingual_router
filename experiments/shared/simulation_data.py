"""Load generation results for routing simulations (no database needed).

Reads the JSONL files written by data/generate.py, joins them with the preprocessed queries
and the item-level train/test split, and computes normalization bounds from training items.
"""
import glob
import json
import logging
import re

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def hardware_slug(hardware):
    """Filename-safe GPU name, matching data/generate.py's default output name."""
    return re.sub(r"[^A-Za-z0-9]+", "-", hardware).strip("-")


def load_results(paths, hardware=None, models=None):
    """Read result JSONL files; returns one row per (source_id, model_id) on one GPU type."""
    files = sorted({f for p in paths for f in glob.glob(p)})
    if not files:
        raise FileNotFoundError(f"No results files match {paths}")
    rows = []
    for path in files:
        with open(path) as f:
            rows.extend(json.loads(line) for line in f if line.strip())
    df = pd.DataFrame(rows)

    gpus = sorted(df["hardware"].dropna().unique())
    if hardware:
        df = df[df["hardware"] == hardware]
    elif len(gpus) > 1:
        raise ValueError(f"Results mix GPU types {gpus}; energy isn't comparable. Pick one with --hardware.")
    if df.empty:
        raise ValueError(f"No results for hardware {hardware!r}; available: {gpus}")
    if models:
        df = df[df["model_id"].isin(models)]

    # A re-run of the same pair replaces the earlier row
    df = df.drop_duplicates(["source_id", "model_id"], keep="last")
    logger.info(f"Loaded {len(df)} results from {len(files)} file(s) on {df['hardware'].iloc[0]}")
    return df


def complete_queries(results):
    """Keep queries that have a result for every model; returns (results, model_ids)."""
    model_ids = sorted(results["model_id"].unique())
    counts = results.groupby("source_id")["model_id"].nunique()
    complete = counts[counts == len(model_ids)].index
    dropped = len(counts) - len(complete)
    if dropped:
        logger.warning(f"Dropping {dropped} queries missing a result for some model")
    return results[results["source_id"].isin(complete)], model_ids


def build_query_table(results, model_ids, queries_path, splits_path):
    """One row per query with per-model arrays, plus text/language/split metadata.

    Returns a DataFrame indexed by source_id with columns dataset, language, item_id, split,
    text, and arrays accuracy / energy / tokens of shape (n_models,) in model_ids order.
    """
    queries = pd.read_csv(queries_path, keep_default_na=False).set_index("id")
    splits = pd.read_csv(splits_path).set_index("item_id")["split"]

    wide = results.pivot(index="source_id", columns="model_id")
    table = queries.loc[wide.index, ["dataset", "language", "item_id", "processed_input"]].rename(
        columns={"processed_input": "text"}
    )
    table["split"] = table["item_id"].map(splits)
    if table["split"].isna().any():
        raise ValueError("Some items have no split; re-run data/split.py on the current combined.csv")

    def per_model(column, dtype=float):
        return list(wide[column][model_ids].to_numpy(dtype=dtype))

    table["accuracy"] = per_model("accuracy")
    table["energy"] = per_model("energy_consumption")
    table["tokens"] = list(
        (wide["input_tokens"][model_ids] + wide["output_tokens"][model_ids]).to_numpy(dtype=float)
    )
    return table


class TrainBounds:
    """Per-dataset min/max of energy metrics over training queries.

    Has the same `bounds` shape as MetricNormalizer ({dataset: {metric: {min, max}}}), so it can
    be passed to CarbonNormalizer. Test queries outside the range are clamped to [0, 1].
    """

    def __init__(self, table):
        self.bounds = {}
        train = table[table["split"] == "train"]
        for dataset, group in train.groupby("dataset"):
            energy = np.concatenate(group["energy"].to_list())
            per_token = np.concatenate((group["energy"] / group["tokens"]).to_list())
            self.bounds[dataset] = {
                "energy_consumption": {"min": float(energy.min()), "max": float(energy.max())},
                "energy_per_token": {"min": float(per_token.min()), "max": float(per_token.max())},
            }

    def normalize(self, metric, value, dataset):
        b = self.bounds[dataset][metric]
        span = b["max"] - b["min"]
        return np.clip((np.asarray(value) - b["min"]) / span, 0.0, 1.0) if span > 0 else np.zeros_like(value)
