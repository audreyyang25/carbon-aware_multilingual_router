"""Build each router's context vectors from its feature list (config/routers.yaml).

Everything learned from data (PCA, k-means, scaling) is fit on training queries only, so test
queries and a held-out language never shape the features.
"""
import logging

import numpy as np
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from src.feature_extractor.complexity import ComplexityExtractor
from src.feature_extractor.language import LanguageOneHotExtractor, load_embeddings

logger = logging.getLogger(__name__)

ENCODER_FEATURES = {"semantic_cluster", "embedding"}


class ContextBuilder:
    """Static per-query blocks are built once; carbon intensity is appended per step."""

    def __init__(self, profile, table, feature_config, ci_bounds, holdout_language=None, n_clusters=3,
                 pca_dim=None):
        self.features = profile["features"]
        self.uses_ci = "carbon_intensity" in self.features
        self.ci_min, self.ci_max = ci_bounds
        train = (table["split"] == "train").to_numpy()
        if holdout_language:
            train &= (table["language"] != holdout_language).to_numpy()

        blocks = [np.ones((len(table), 1))]  # bias
        for feature in self.features:
            if feature == "dataset":
                datasets = sorted(table["dataset"].unique())
                blocks.append(one_hot(table["dataset"], datasets))
            elif feature == "complexity":
                extractor = ComplexityExtractor(feature_config["complexity"])
                bins = [extractor.extract(text)["bin"] for text in table["text"]]
                blocks.append(one_hot(bins, list(range(len(extractor.complexity_bins) + 1))))
            elif feature == "semantic_cluster":
                X = cached_embeddings(feature_config["english_embedding"], table.index)
                kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=0).fit(X[train])
                blocks.append(one_hot(kmeans.predict(X), list(range(n_clusters))))
            elif feature == "embedding":
                section = profile["encoder"]
                X = cached_embeddings(feature_config[section], table.index)
                n_components = pca_dim or feature_config[section]["pca_dim"]
                pca = PCA(n_components=n_components, random_state=0).fit(X[train])
                Z = pca.transform(X)
                Z /= Z[train].std(axis=0)  # unit scale, like the one-hot blocks
                logger.info(f"{section}: PCA to {n_components} dims keeps {pca.explained_variance_ratio_.sum():.0%} of variance")
                blocks.append(Z)
            elif feature == "language":
                languages = list(feature_config["language"]["languages"])
                if holdout_language in languages:
                    languages.remove(holdout_language)  # unseen language -> all zeros
                extractor = LanguageOneHotExtractor({"languages": languages})
                blocks.append(np.stack([extractor.extract(metadata={"language": l}) for l in table["language"]]))
            elif feature == "carbon_intensity":
                continue  # appended per step
            else:
                raise ValueError(f"Unknown feature '{feature}' in routers.yaml")

        self.static = np.hstack(blocks).astype(np.float64)
        self.row = {sid: i for i, sid in enumerate(table.index)}
        self.dim = self.static.shape[1] + int(self.uses_ci)

    @property
    def uses_encoder(self):
        return bool(ENCODER_FEATURES & set(self.features))

    def context(self, source_id, ci):
        """Context vector for one query at grid intensity ci (gCO2eq/kWh)."""
        static = self.static[self.row[source_id]]
        if not self.uses_ci:
            return static
        scaled = (ci - self.ci_min) / (self.ci_max - self.ci_min)
        return np.append(static, scaled)


def one_hot(values, categories):
    index = {c: i for i, c in enumerate(categories)}
    out = np.zeros((len(values), len(categories)))
    for row, value in enumerate(values):
        if value in index:
            out[row, index[value]] = 1.0
    return out


def cached_embeddings(section_config, source_ids):
    path = section_config["embeddings_path"]
    try:
        cache = load_embeddings(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"{path} not found; run `python data/embed.py` first")
    return np.stack([cache[sid] for sid in source_ids]).astype(np.float64)
