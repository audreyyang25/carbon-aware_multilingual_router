"""Build the Belebele query file for the extra low-resource languages.

Uses the languages in config/lowres_languages.yaml and the Belebele settings in
config/datasets.yaml (prompt, sampling, extraction). Items are chosen on English exactly as
data/process.py does, so they are the same 250 items (same item_id) as the main run, and
data/preprocessed/splits.csv applies unchanged. Writes data/preprocessed/belebele_lowres.csv;
it never touches belebele.csv or combined.csv.

    python data/process_lowres.py                    # all languages in the config
    python data/process_lowres.py --languages yo am  # a subset

Then, on the GPU Pod:
    python data/generate.py --input data/preprocessed/belebele_lowres.csv \
        --output results/generations_lowres_<gpu>.jsonl

Needs Hugging Face access. A language that fails to load is reported and skipped.
"""
import argparse
import os
import sys

import pandas as pd
from datasets import load_dataset

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import load_config
from data.helper import preprocess_dataset
from data.process import DataProcessor, align_items, select_items

DEFAULT_OUTPUT = "data/preprocessed/belebele_lowres.csv"
MAIN_RUN_FILE = "data/preprocessed/belebele.csv"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--languages", nargs="*", help="Short codes from config/lowres_languages.yaml (default: all)")
    parser.add_argument("--no-anchors", action="store_true", help="Leave out the anchor languages (en, sw)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    lowres = load_config("lowres_languages")
    name = lowres["dataset"]
    dataset_config = load_config("datasets")
    config = dataset_config["datasets"][name]
    pivot = dataset_config.get("pivot_language", "en")
    pivot_hf = config["languages"][pivot]
    seed = load_config("general").get("random_seed", 40)

    languages = dict(lowres["languages"])
    if not args.no_anchors:
        languages.update(lowres.get("anchor_languages") or {})
    if args.languages:
        unknown = sorted(set(args.languages) - set(languages))
        if unknown:
            sys.exit(f"Unknown languages {unknown}; choose from {sorted(languages)}")
        languages = {k: v for k, v in languages.items() if k in args.languages}

    def load(hf_config):
        return preprocess_dataset(name, load_dataset(**config["load_params"], name=hf_config, split=config["split"]))

    # Same item choice as data/process.py: on the pivot language, same n, strata and seed
    pivot_dataset = load(pivot_hf)
    sampling = config.get("sampling", {})
    pivot_items = select_items(pivot_dataset, sampling.get("n"), sampling.get("stratify"), seed)

    processor = DataProcessor(name)
    if os.path.exists(MAIN_RUN_FILE):
        # Guard: the items must be the ones the main run used, or the two runs can't be compared
        main_ids = set(pd.read_csv(MAIN_RUN_FILE, usecols=["item_id"])["item_id"])
        ours = {f"{name}_{i:04d}" for i in pivot_items}
        if ours != main_ids:
            sys.exit(f"Item selection differs from {MAIN_RUN_FILE} ({len(ours ^ main_ids)} items); not writing.")
        print(f"Same {len(ours)} items as {MAIN_RUN_FILE}")

    frames, failed = [], {}
    for lang, hf_config in languages.items():
        try:
            dataset = pivot_dataset if hf_config == pivot_hf else load(hf_config)
            indices = align_items(pivot_dataset, dataset, pivot_items)
        except Exception as e:  # a wrong config name or a missing item shouldn't stop the others
            failed[lang] = f"{hf_config}: {type(e).__name__}: {str(e)[:200]}"
            print(f"FAILED {lang} ({failed[lang]}); skipped")
            continue
        frames.append(processor.process_dataset(dataset, lang, indices, pivot_items))
        print(f"{lang} ({hf_config}): {len(indices)} items")

    if not frames:
        sys.exit("No language could be loaded.")
    df = pd.concat(frames, ignore_index=True)
    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"Saved {len(df)} queries ({df['language'].nunique()} languages) to {args.output}")
    if failed:
        print(f"WARNING: {len(failed)} languages skipped: {failed}")


if __name__ == "__main__":
    main()
