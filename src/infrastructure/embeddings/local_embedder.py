from typing import Iterable, List

from sentence_transformers import SentenceTransformer

from application.interfaces import Embedder


class LocalEmbedder(Embedder):
    def __init__(self, model_name: str = all-MiniLM-L6-v2) -> None:
        self._model = SentenceTransformer(model_name)

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        embeddings = self._model.encode(list(texts), normalize_embeddings=True)
        return embeddings.tolist()
