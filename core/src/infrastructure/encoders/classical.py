from __future__ import annotations

import hashlib
from typing import Any

from domain.ir import l2_normalize

try:
    from sentence_transformers import SentenceTransformer  # type: ignore
except Exception:  # pragma: no cover
    SentenceTransformer = None


class SbertEncoder:
    def __init__(self, model_name: str, dim: int) -> None:
        self.model_name = model_name
        self.dim = dim
        self._model: Any | None = None

    def _load_model(self):
        if self._model is None and SentenceTransformer is not None:
            self._model = SentenceTransformer(self.model_name)
            inferred_dim = int(getattr(self._model, "get_sentence_embedding_dimension")())
            if inferred_dim:
                self.dim = inferred_dim
        return self._model

    def _fallback(self, text: str) -> list[float]:
        buckets = [0.0] * self.dim
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for i in range(0, min(len(digest), 32), 4):
                idx = int.from_bytes(digest[i : i + 2], "big") % self.dim
                sign = 1.0 if digest[i + 2] % 2 == 0 else -1.0
                buckets[idx] += sign * ((digest[i + 3] / 255.0) + 0.1)
        return l2_normalize(buckets)

    def encode(self, text: str) -> list[float]:
        model = self._load_model()
        if model is None:
            return self._fallback(text)
        vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        vector = [float(x) for x in vec.tolist()]
        self.dim = len(vector)
        return l2_normalize(vector)
