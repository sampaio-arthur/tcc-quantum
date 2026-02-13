from dataclasses import dataclass
import re
from typing import Iterable, List

from application.dtos import DocumentDTO, SearchResponseDTO
from application.interfaces import Embedder, QuantumComparator
from application.mappers.search import document_dto_to_entity, results_to_dtos
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


class RealizarBuscaUseCase:
    def __init__(
        self,
        embedder: Embedder,
        classical_comparator: QuantumComparator,
        quantum_comparator: QuantumComparator | None = None,
    ) -> None:
        self._embedder = embedder
        self._classical_comparator = classical_comparator
        self._quantum_comparator = quantum_comparator or classical_comparator

    def execute(
        self,
        query: str,
        documents: Iterable[DocumentDTO],
        mode: str = "classical",
        top_k: int = 5,
        candidate_k: int = 20,
    ) -> SearchResponseDTO:
        results = self.score(query, documents, mode=mode, candidate_k=candidate_k)
        limited_results = list(results)[:top_k]
        answer = self.build_answer(query, limited_results)
        return SearchResponseDTO(
            query=query,
            mode=mode,
            results=results_to_dtos(limited_results),
            answer=answer,
        )

    def score(
        self,
        query: str,
        documents: Iterable[DocumentDTO],
        mode: str = "classical",
        candidate_k: int = 20,
    ) -> List[SearchResult]:
        docs_dto = list(documents)
        if not docs_dto:
            return []

        docs = [document_dto_to_entity(dto) for dto in docs_dto]
        query_vector = self._embedder.embed_texts([query])[0]
        doc_vectors = self._embedder.embed_texts([doc.text for doc in docs])

        base_scores = [
            self._classical_comparator.compare(query_vector, vector)
            for vector in doc_vectors
        ]

        if mode == "quantum":
            candidate_k = max(1, min(candidate_k, len(docs)))
            candidate_indices = sorted(
                range(len(base_scores)),
                key=lambda i: base_scores[i],
                reverse=True,
            )[:candidate_k]
            results = [
                SearchResult(
                    document=docs[i],
                    score=self._quantum_comparator.compare(query_vector, doc_vectors[i]),
                )
                for i in candidate_indices
            ]
        else:
            results = [
                SearchResult(document=doc, score=score)
                for doc, score in zip(docs, base_scores)
            ]

        results.sort(key=lambda item: item.score, reverse=True)
        return results

    def build_answer(self, query: str, results: List[SearchResult]) -> str | None:
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
            top_text = _normalize_text(results[0].document.text)
            if not top_text:
                return None
            return "Com base no documento, " + top_text

        query_vector = self._embedder.embed_texts([query])[0]
        sentence_vectors = self._embedder.embed_texts(candidates)
        scores = [
            self._classical_comparator.compare(query_vector, vector)
            for vector in sentence_vectors
        ]

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
        top_sentences = [candidates[i] for i in top_indices]

        return "Com base no documento, " + " ".join(top_sentences)
