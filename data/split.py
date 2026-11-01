"""Assign each benchmark item to train or test, before any results are looked at.

Splits by item_id, not by row: the same item exists in every language, so splitting rows
would put e.g. xnli_0042 (en) in train and xnli_0042 (sw) in test and leak the answer.
Each dataset is split separately so train and test have the same benchmark mix.

    python data/split.py   ->   data/preprocessed/splits.csv (item_id, dataset, split)
"""
import argparse
import os
import random
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import load_config


def split_items(queries, test_fraction, seed):
    """Return a DataFrame of item_id, dataset, split ('train' / 'test')."""
    rng = random.Random(seed)
    rows = []
    for dataset, items in queries.groupby("dataset")["item_id"]:
        item_ids = sorted(items.unique())
        rng.shuffle(item_ids)
        n_test = round(len(item_ids) * test_fraction)
        for i, item_id in enumerate(item_ids):
            rows.append({"item_id": item_id, "dataset": dataset, "split": "test" if i < n_test else "train"})
    return pd.DataFrame(rows).sort_values("item_id").reset_index(drop=True)


def main():
    parser = argparse.ArgumentParser(description="Item-level train/test split")
    parser.add_argument("--input", default="data/preprocessed/combined.csv")
    parser.add_argument("--output", default="data/preprocessed/splits.csv")
    args = parser.parse_args()

    test_fraction = load_config("datasets").get("split", {}).get("test_fraction", 0.3)
    seed = load_config("general").get("random_seed", 40)
    queries = pd.read_csv(args.input, usecols=["dataset", "item_id"])

    splits = split_items(queries, test_fraction, seed)
    splits.to_csv(args.output, index=False)
    print(splits.groupby(["dataset", "split"]).size().unstack())
    print(f"Saved {len(splits)} items to {args.output}")


if __name__ == "__main__":
    main()
