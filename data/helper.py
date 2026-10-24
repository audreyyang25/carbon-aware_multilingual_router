import pandas as pd
from config.manager import load_config
from datasets import Dataset


dataset_config = load_config("datasets")["datasets"]


def restructure_xnli(entry, config):
    """Convert xnli format to standard format"""
    input1_col = config.get("input1", "")
    input2_col = config.get("input2", "")
    reference_col = config.get("reference", "")

    return {
        'input1': entry[input1_col],
        'input2': entry[input2_col],
        'reference': int(entry[reference_col])  # 0 entailment, 1 neutral, 2 contradiction
    }


def restructure_belebele(entry, config):
    """Convert belebele format to standard format"""
    passage_col, question_col = config.get("input1", [])
    input2 = [entry[col] for col in config.get("input2", [])]
    reference_col = config.get("reference", "")

    return {
        'input1': entry[passage_col] + "\nQuestion:\n" + entry[question_col],
        'input2': input2,
        'reference': int(entry[reference_col]) - 1  # Convert "1"-"4" to 0-based index
    }


def restructure_mgsm(entry, config):
    """Convert mgsm format to standard format"""
    input1_col = config.get("input1", "")
    reference_col = config.get("reference", "")

    return {
        'input1': entry[input1_col],
        'reference': str(entry[reference_col])  # answer_number; the 'answer' column is empty in test
    }


RESTRUCTURE_FUNCTIONS = {
    "xnli": restructure_xnli,
    "belebele": restructure_belebele,
    "mgsm": restructure_mgsm,
}


def preprocess_dataset(dataset_name, dataset):
    """Apply dataset-specific preprocessing.

    Keeps any align_key columns (e.g. belebele's link/question_number) as 'item_key'
    so the same item can be matched across languages.
    """
    print("Preprocessing dataset: ", dataset_name)

    if dataset_name not in RESTRUCTURE_FUNCTIONS:
        raise ValueError(f"No preprocessing function for {dataset_name} found")
    restructure = RESTRUCTURE_FUNCTIONS[dataset_name]
    config = dataset_config[dataset_name]["columns"]
    align_key = dataset_config[dataset_name].get("align_key")

    processed_entries = []
    for entry in dataset:
        processed = restructure(entry, config)
        if align_key:
            processed['item_key'] = "#".join(str(entry[col]) for col in align_key)
        processed_entries.append(processed)

    new_dataset = Dataset.from_list(processed_entries)
    print("First entry after preprocessing:", new_dataset[0])
    return new_dataset
