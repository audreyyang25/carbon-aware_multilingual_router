"""Embed every preprocessed query with the router's encoders and cache the vectors.

The router's encoder only reads the query text, so this needs no model results and runs
locally (CPU or Apple GPU). Embeddings are full size; PCA happens at simulation time,
fit on training items only. Both the multilingual encoder and GreenServ's English one are
cached, so the simulation can compare them.

    python data/embed.py   ->   data/features/embeddings_<encoder>.npz (ids, embeddings)
    python data/embed.py --encoders multilingual_embedding
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
    args = parser.parse_args()

    feature_config = load_config("feature_extraction")["feature_extraction"]
    queries = pd.read_csv(args.input, keep_default_na=False)

    for section in args.encoders:
        config = feature_config[section]
        output_path = config["embeddings_path"]
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        extractor = MultilingualEmbeddingExtractor(config)

        start = time.time()
        # The router sees the full prompt, instruction included, as it would in deployment
        embeddings = extractor.encode(
            queries["processed_input"].tolist(), batch_size=args.batch_size, show_progress_bar=True
        )
        elapsed = time.time() - start

        np.savez_compressed(
            output_path,
            ids=queries["id"].to_numpy(dtype=str),
            embeddings=embeddings.astype(np.float16),
            encoder=np.array(config["encoder"]),
        )
        print(
            f"{config['encoder']}: embedded {len(queries)} queries ({embeddings.shape[1]} dims) "
            f"in {elapsed:.0f} s ({1000 * elapsed / len(queries):.1f} ms/query) -> {output_path}"
        )


if __name__ == "__main__":
    main()
