from dataclasses import dataclass
import re
from typing import Iterable, List

import numpy as np

from application.dtos import DocumentDTO, SearchResponseDTO
from application.interfaces import Embedder, QuantumComparator
from application.mappers.search import document_dto_to_entity, result_entity_to_dto
from domain.entities import Document


@dataclass(frozen=True)
class SearchResult:
    document: Document
    score: float


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [part.strip() for part in parts if part.strip()]


def _cosine_similarity(vector_a: np.ndarray, vector_b: np.ndarray) -> float:
    denom = np.linalg.norm(vector_a) * np.linalg.norm(vector_b)
    if denom == 0:
        return 0.0
    return float(np.dot(vector_a, vector_b) / denom)


class RealizarBuscaUseCase:
    def __init__(self, embedder: Embedder, comparator: QuantumComparator) -> None:
        self._embedder = embedder
        self._comparator = comparator

    def execute(self, query: str, documents: Iterable[DocumentDTO]) -> SearchResponseDTO:
        docs_dto = list(documents)
        if not docs_dto:
            return SearchResponseDTO(query=query, results=[], answer=None)

        docs = [document_dto_to_entity(dto) for dto in docs_dto]
        query_vector = self._embedder.embed_texts([query])[0]
        doc_vectors = self._embedder.embed_texts([doc.text for doc in docs])

        results = [
            SearchResult(document=doc, score=self._comparator.compare(query_vector, vector))
            for doc, vector in zip(docs, doc_vectors)
        ]
        results.sort(key=lambda item: item.score, reverse=True)

        answer = self._build_answer(query, results)
        return result_entity_to_dto(query, results, answer=answer)

    def _build_answer(self, query: str, results: List[SearchResult]) -> str | None:
        if not results:
            return None

        candidates: List[str] = []
        for item in results[:3]:
            text = _normalize_text(item.document.text)
            for sentence in _split_sentences(text):
                if len(sentence) < 30:
                    continue
                candidates.append(sentence)
                if len(candidates) >= 30:
                    break
            if len(candidates) >= 30:
                break

        if not candidates:
            return None

        query_vector = self._embedder.embed_texts([query])[0]
        sentence_vectors = self._embedder.embed_texts(candidates)
        scores = [
            _cosine_similarity(query_vector, np.array(vector, dtype=float))
            for vector in sentence_vectors
        ]

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
        top_sentences = [candidates[i] for i in top_indices]

        return "Com base no documento, " + " ".join(top_sentences)
