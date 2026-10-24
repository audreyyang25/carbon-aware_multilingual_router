import re
import os
import sys
import pandas as pd
import random
import argparse
from collections import defaultdict
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import load_config
from data.load import load_datasets
from data.helper import preprocess_dataset


def difficulty_strata(pivot_dataset, stratify):
    """Assign each pivot item a stratum from difficulty proxies (label, length tertile)."""
    keys = [[] for _ in range(len(pivot_dataset))]
    if "label" in stratify:
        for i, example in enumerate(pivot_dataset):
            keys[i].append(str(example["reference"]))
    if "length" in stratify:
        lengths = [
            len(example["input1"]) + len(str(example.get("input2") or ""))
            for example in pivot_dataset
        ]
        tertiles = pd.qcut(lengths, 3, labels=False, duplicates="drop")
        for i, t in enumerate(tertiles):
            keys[i].append(f"len{t}")
    return ["|".join(k) for k in keys]


def select_items(pivot_dataset, n, stratify, seed):
    """Pick n pivot-language item positions, balanced across difficulty strata.

    Draws round-robin from each stratum so every label/length bucket is equally represented.
    """
    if n is None or n >= len(pivot_dataset):
        return list(range(len(pivot_dataset)))

    rng = random.Random(seed)
    groups = defaultdict(list)
    for i, stratum in enumerate(difficulty_strata(pivot_dataset, stratify or [])):
        groups[stratum].append(i)
    for members in groups.values():
        rng.shuffle(members)

    selected = []
    strata = sorted(groups)
    while len(selected) < n and any(groups[s] for s in strata):
        for s in strata:
            if groups[s] and len(selected) < n:
                selected.append(groups[s].pop())
    return sorted(selected)


def align_items(pivot_dataset, dataset, pivot_items):
    """Map pivot positions to the same items in another language (by item_key, else by position)."""
    if "item_key" in pivot_dataset.column_names:
        position = {key: i for i, key in enumerate(dataset["item_key"])}
        missing = [pivot_dataset[i]["item_key"] for i in pivot_items if pivot_dataset[i]["item_key"] not in position]
        if missing:
            raise KeyError(f"{len(missing)} items not found in this language, e.g. {missing[:3]}")
        return [position[pivot_dataset[i]["item_key"]] for i in pivot_items]

    if len(dataset) != len(pivot_dataset):
        raise ValueError(
            f"Row counts differ ({len(dataset)} vs pivot {len(pivot_dataset)}); set align_key in config/datasets.yaml"
        )
    return list(pivot_items)


class DataProcessor:
    """Process datasets according to configuration"""
    
    def __init__(self, dataset_name):
        self.name = dataset_name
        config = load_config("datasets")
        self.config = config["datasets"].get(dataset_name, {})
        self.columns = self.config.get("columns", {})
        self.preprocessing = self.config.get("preprocessing", {})
        
    def process_example(self, example, language=None):
        """Process a single example to standardized format"""
        processed = {
            "dataset": self.name,
            "language": language,
        }
        
        input_text = example["input1"]
        if "input1_prefix" in self.preprocessing:
            input_text = self.preprocessing["input1_prefix"] + input_text
            
        if "input2" in self.columns:
            input2 = example["input2"]
            
            if "input2_prefix" in self.preprocessing:
                input2_text = self.preprocessing["input2_prefix"]
                
                if isinstance(input2, list):
                    for i, choice in enumerate(input2):
                        option = chr(65 + i)  
                        input2_text += f"{option}. {choice}\n"
                else:
                    input2_text += str(input2)
                    
                input_text += "\n" + input2_text

        if "output_prefix" in self.preprocessing:
            input_text += self.preprocessing["output_prefix"]
        
        processed["processed_input"] = input_text
        reference = example["reference"]
            
        if self.preprocessing.get("reference_mapping") == "index_to_letter":
            try:
                if isinstance(reference, int) or (isinstance(reference, str) and reference.isdigit()):
                    idx = int(reference)
                    reference = chr(65 + idx)  
            except (ValueError, TypeError):
                pass
                
        processed["reference"] = reference
        
        generation = self.config.get("generation", {})
        
        processed["max_new_tokens"] = generation.get("max_new_tokens", 100)
        processed["stop_sequence"] = str(generation.get("stop_sequence", ["\n"]))
        
        extraction = self.config.get("extraction", {})
        extraction_method = extraction.get("method", "raw")

        if extraction_method == "regex":
            extraction_method = f"{extraction_method}_{extraction.get('pattern', '')}"
            
        processed["extraction_method"] = extraction_method
        
        processed["evaluation_metric"] = self.config.get("evaluation_metric", "exact_match")
        
        return processed
        
    def process_dataset(self, dataset, language, indices, pivot_items):
        """Process the selected rows of one language and convert to DataFrame.

        indices are row positions in this language; pivot_items are the matching
        pivot-language positions, used as the shared item id across languages.
        """
        processed_data = []
        for row, item in zip(indices, pivot_items):
            processed = self.process_example(dataset[row], language)
            processed["item_id"] = f"{self.name}_{item:04d}"
            processed["id"] = f"{self.name}_{language}_{item:04d}"
            processed_data.append(processed)

        # Convert to DataFrame
        return pd.DataFrame(processed_data)
    
    def save_to_csv(self, df, output_dir=None):
        """Save processed dataset to CSV"""
        if output_dir is None:
            general_config = load_config("general")
            output_dir = general_config.get("preprocessed_dir", "preprocessed")
            
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{self.name}.csv")
        df.to_csv(output_path, index=False)
        print(f"Saved {len(df)} samples to {output_path}")
        return output_path
        
    # def extract_answer(self, prediction):
    #     """Extract answer from model prediction using configured method"""
    #     extraction = self.config.get("extraction", {})
    #     method = extraction.get("method", "raw")
        
    #     if method == "multiple_choice":
    #         pattern = extraction.get("pattern", "([A-D])")
    #         match = re.search(pattern, prediction)
    #         return match.group(1) if match else None
            
    #     elif method == "regex":
    #         pattern = extraction.get("pattern", "(.+)")
    #         match = re.search(pattern, prediction)
    #         return match.group(1) if match else None
        
    #     elif method == "raw":
    #         return prediction.strip()
            
    #     return prediction.strip()


def main():
    """Download, process and save datasets as CSV"""
    parser = argparse.ArgumentParser(description="Process datasets into CSV files")
    parser.add_argument("--datasets", nargs="*", help="Specific datasets to process")
    parser.add_argument("--languages", nargs="*", help="Specific languages to process (pivot is always loaded)")
    parser.add_argument("--samples", type=int, help="Override sampling.n for every dataset (e.g. a small dry run)")

    args = parser.parse_args()

    # Get config
    general_config = load_config("general")
    datasets_config = load_config("datasets")
    seed = general_config.get("random_seed", 40)
    output_dir = general_config.get("preprocessed_dir", "data/preprocessed")
    pivot = datasets_config.get("pivot_language", "en")

    # Load datasets from HuggingFace
    languages = sorted(set(args.languages) | {pivot}) if args.languages else None
    datasets = load_datasets(args.datasets, languages=languages)

    all_data = []
    # Process each dataset
    for name, by_language in datasets.items():
        print(f"Processing {name}...")
        if pivot not in by_language:
            raise ValueError(f"{name}: pivot language '{pivot}' failed to load")

        # Apply dataset-specific preprocessing
        preprocessed = {lang: preprocess_dataset(name, ds) for lang, ds in by_language.items()}

        processor = DataProcessor(name)
        sampling = processor.config.get("sampling", {})
        n_samples = args.samples or sampling.get("n")

        # Choose items once on the pivot language, then take the same items everywhere
        pivot_items = select_items(preprocessed[pivot], n_samples, sampling.get("stratify"), seed)
        print(f"Selected {len(pivot_items)} {name} items (stratify={sampling.get('stratify')})")

        frames = []
        for lang, dataset in preprocessed.items():
            if args.languages and lang not in args.languages:
                continue
            indices = align_items(preprocessed[pivot], dataset, pivot_items)
            frames.append(processor.process_dataset(dataset, lang, indices, pivot_items))
        df = pd.concat(frames, ignore_index=True)
        print("df:", df.head())
        # Save individual dataset
        processor.save_to_csv(df, output_dir)
        all_data.append(df)
    
    # Create combined CSV with all samples
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        output_path = os.path.join(output_dir, "combined.csv")
        combined_df.to_csv(output_path, index=False)
        print(f"Saved combined dataset with {len(combined_df)} samples to {output_path}")

if __name__ == "__main__":
    main()