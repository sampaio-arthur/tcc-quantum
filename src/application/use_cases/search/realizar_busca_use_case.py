from dataclasses import dataclass
from typing import Iterable, List

from application.interfaces import Embedder, QuantumComparator
from domain.entities import Document


@dataclass(frozen=True)
class SearchResult:
    document: Document
    score: float


class RealizarBuscaUseCase:
    def __init__(self, embedder: Embedder, comparator: QuantumComparator) -> None:
        self._embedder = embedder
        self._comparator = comparator

    def execute(self, query: str, documents: Iterable[Document]) -> List[SearchResult]:
        docs = list(documents)
        if not docs:
            return []

        query_vector = self._embedder.embed_texts([query])[0]
        doc_vectors = self._embedder.embed_texts([doc.text for doc in docs])

        results = [
            SearchResult(document=doc, score=self._comparator.compare(query_vector, vector))
            for doc, vector in zip(docs, doc_vectors)
        ]
        results.sort(key=lambda item: item.score, reverse=True)
        return results
