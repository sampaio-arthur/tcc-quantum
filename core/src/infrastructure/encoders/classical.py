from __future__ import annotations

from typing import Any

from domain.exceptions import ValidationError
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
        if self._model is not None:
            return self._model
        if SentenceTransformer is None:
            raise ValidationError(
                "Classical encoder unavailable: sentence-transformers is not installed/loaded."
            )
        try:
            self._model = SentenceTransformer(self.model_name)
        except Exception as exc:
            raise ValidationError(
                f"Failed to load classical encoder model '{self.model_name}': {exc}"
            ) from exc
        inferred_dim = int(getattr(self._model, "get_sentence_embedding_dimension")())
        if inferred_dim:
            self.dim = inferred_dim
        return self._model

    def encode(self, text: str) -> list[float]:
        model = self._load_model()
        try:
            vec = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        except Exception as exc:
            raise ValidationError(f"Classical encoder failed to encode text: {exc}") from exc
        vector = [float(x) for x in vec.tolist()]
        self.dim = len(vector)
        return l2_normalize(vector)
