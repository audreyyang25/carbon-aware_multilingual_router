# src/feature_extractor/language.py
import logging

import numpy as np

from src.feature_extractor.base import BaseFeatureExtractor

logger = logging.getLogger(__name__)


class LanguageOneHotExtractor(BaseFeatureExtractor):
    """One-hot of the query language, read from metadata["language"].

    In deployment the language would come from a language-ID model; in the benchmarks it is known.
    A language outside the configured list maps to all zeros (the router has never seen it).
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.languages = list(self.config.get("languages", []))

    @property
    def dim(self):
        return len(self.languages)

    def extract(self, query_text=None, metadata=None):
        """Return the one-hot vector for this query's language."""
        language = (metadata or {}).get("language")
        if language not in self.languages:
            logger.debug(f"Language '{language}' not in {self.languages}; using zeros")
        return np.array([1.0 if language == lang else 0.0 for lang in self.languages])


class MultilingualEmbeddingExtractor(BaseFeatureExtractor):
    """Multilingual sentence embedding of the query, reduced with PCA.

    The encoder runs once over all queries (data/embed.py) and the vectors are cached, so a
    simulation only loads them. PCA is fit on training items only, then applied to every query;
    refit it for each held-out-language experiment so the held-out language never shapes it.
    """

    def __init__(self, config=None):
        super().__init__(config)
        self.encoder_name = self.config.get("encoder", "intfloat/multilingual-e5-small")
        self.prefix = self.config.get("prefix", "")
        self.pca_dim = self.config.get("pca_dim", 16)
        self.encoder = None
        self.mean = None
        self.components = None

    @property
    def dim(self):
        return self.pca_dim

    def _load_encoder(self):
        if self.encoder is None:
            from sentence_transformers import SentenceTransformer

            logger.info(f"Loading encoder {self.encoder_name}")
            self.encoder = SentenceTransformer(self.encoder_name, device=self.config.get("device"))
        return self.encoder

    def encode(self, texts, batch_size=64, show_progress_bar=False):
        """Full-size, L2-normalized embeddings for a list of query texts."""
        return self._load_encoder().encode(
            [self.prefix + text for text in texts],
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=show_progress_bar,
        )

    def fit(self, train_embeddings):
        """Fit PCA on training-item embeddings only."""
        from sklearn.decomposition import PCA

        pca = PCA(n_components=self.pca_dim, random_state=0).fit(train_embeddings)
        self.mean, self.components = pca.mean_, pca.components_
        logger.info(
            f"PCA to {self.pca_dim} dims keeps {pca.explained_variance_ratio_.sum():.1%} of the variance"
        )
        return self

    def transform(self, embeddings):
        """Project full embeddings onto the fitted PCA components."""
        if self.components is None:
            raise RuntimeError("Call fit() on training embeddings before transform()")
        return (np.atleast_2d(embeddings) - self.mean) @ self.components.T

    def extract(self, query_text, metadata=None):
        """Reduced embedding for a single query (live routing; simulations use cached vectors)."""
        return self.transform(self.encode([query_text]))[0]


def load_embeddings(path):
    """Cached embeddings from data/embed.py as {source_id: vector}."""
    data = np.load(path, allow_pickle=False)
    return dict(zip(data["ids"].tolist(), data["embeddings"].astype(np.float32)))
