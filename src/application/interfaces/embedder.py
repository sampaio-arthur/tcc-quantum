from abc import ABC, abstractmethod
from typing import Iterable, List


class Embedder(ABC):
    @abstractmethod
    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        # Transform texts into numeric vectors.
        raise NotImplementedError
