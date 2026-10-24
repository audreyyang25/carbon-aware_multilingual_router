# data/load.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import load_config
from datasets import load_dataset

def load_datasets(dataset_names=None, languages=None):
    """Load every (benchmark, language) split from HuggingFace based on config.

    Returns {dataset_name: {language: Dataset}}.
    """
    config = load_config("datasets")

    # Use all datasets if none specified
    if dataset_names is None:
        dataset_names = list(config["datasets"].keys())

    loaded_datasets = {}
    for name in dataset_names:
        if name not in config["datasets"]:
            print(f"Dataset {name} not found in config")
            continue

        dataset_config = config["datasets"][name]
        load_params = dataset_config.get("load_params", {})
        split = dataset_config.get("split", "")
        loaded_datasets[name] = {}
        for lang, hf_config in dataset_config.get("languages", {}).items():
            if languages and lang not in languages:
                continue
            try:
                dataset = load_dataset(**load_params, name=hf_config, split=split or None)
                loaded_datasets[name][lang] = dataset
                print(f"Loaded {name}/{lang} ({len(dataset)} rows)")
            except Exception as e:
                print(f"Failed to load {name}/{lang}: {e}")

    return loaded_datasets


if __name__ == "__main__":
    load_datasets(["mgsm"], languages=["en", "sw"])
