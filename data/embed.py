"""Embed every preprocessed query with the router's encoders and cache the vectors.

The router's encoder reads the query text and runs locally.
Both the multilingual encoder and GreenServ's English one are
cached, so the simulation can compare them.

    python data/embed.py   ->   data/features/embeddings_<encoder>.npz (ids, embeddings)
    python data/embed.py --encoders multilingual_embedding
    python data/embed.py --input data/preprocessed/belebele_lowres.csv --append
        # adds queries not yet in the cache (e.g. the low-resource languages), keeps the rest
"""
import argparse
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.manager import load_config
from src.feature_extractor.language import MultilingualEmbeddingExtractor


def main():
    parser = argparse.ArgumentParser(description="Cache multilingual query embeddings")
    parser.add_argument("--input", default="data/preprocessed/combined.csv")
    parser.add_argument(
        "--encoders", nargs="*", default=["multilingual_embedding", "english_embedding"],
        help="Sections of config/feature_extraction.yaml to embed with",
    )
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--append", action="store_true",
                        help="Embed only queries missing from the existing cache and add them to it")
    args = parser.parse_args()

    feature_config = load_config("feature_extraction")["feature_extraction"]
    queries = pd.read_csv(args.input, keep_default_na=False)

    for section in args.encoders:
        config = feature_config[section]
        output_path = config["embeddings_path"]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        todo = queries
        old_ids, old_embeddings = np.array([], dtype=str), None
        if args.append and os.path.exists(output_path):
            cache = np.load(output_path, allow_pickle=False)
            if str(cache["encoder"]) != config["encoder"]:
                sys.exit(f"{output_path} was made with {cache['encoder']}, not {config['encoder']}")
            old_ids, old_embeddings = cache["ids"], cache["embeddings"]
            todo = queries[~queries["id"].isin(set(old_ids.tolist()))]
            if todo.empty:
                print(f"{config['encoder']}: all {len(queries)} queries already in {output_path}")
                continue
        extractor = MultilingualEmbeddingExtractor(config)

        start = time.time()
        # The router sees the full prompt, instruction included, as it would in deployment
        embeddings = extractor.encode(
            todo["processed_input"].tolist(), batch_size=args.batch_size, show_progress_bar=True
        ).astype(np.float16)
        elapsed = time.time() - start

        ids = todo["id"].to_numpy(dtype=str)
        if old_embeddings is not None:
            ids = np.concatenate([old_ids, ids])
            embeddings = np.concatenate([old_embeddings, embeddings])
        np.savez_compressed(output_path, ids=ids, embeddings=embeddings, encoder=np.array(config["encoder"]))
        print(
            f"{config['encoder']}: embedded {len(todo)} queries ({embeddings.shape[1]} dims) "
            f"in {elapsed:.0f} s ({1000 * elapsed / len(todo):.1f} ms/query); "
            f"{len(ids)} in {output_path}"
        )


if __name__ == "__main__":
    main()
