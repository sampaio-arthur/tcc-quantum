from __future__ import annotations

import logging
import re
import time
from dataclasses import replace
from typing import Iterable, Sequence

from application.dtos import (
    DocumentDTO,
    SearchAlgorithmDetailsDTO,
    SearchComparisonDTO,
    SearchFileRequestDTO,
    SearchRequestDTO,
    SearchResponseDTO,
    SearchResponseLiteDTO,
)
from application.interfaces import Embedder, QuantumComparator
from application.mappers.search import results_to_dtos
from application.services.search.metrics import compute_ranking_metrics
from application.use_cases import BuscarPorArquivoUseCase, RealizarBuscaUseCase
from application.use_cases.search.realizar_busca_use_case import PreparedSearchInput, SearchResult
from infrastructure.persistence.search_trace_repository import SearchTraceRepository

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(
        self,
        buscar_use_case: RealizarBuscaUseCase,
        buscar_por_arquivo_use_case: BuscarPorArquivoUseCase,
        trace_repository: SearchTraceRepository | None = None,
        answer_embedder: Embedder | None = None,
        answer_comparator: QuantumComparator | None = None,
    ) -> None:
        self._buscar_use_case = buscar_use_case
        self._buscar_por_arquivo_use_case = buscar_por_arquivo_use_case
        self._trace_repository = trace_repository
        self._answer_embedder = answer_embedder
        self._answer_comparator = answer_comparator

    def buscar_por_texto(
        self,
        request: SearchRequestDTO,
        mode: str = 'classical',
        top_k: int = 5,
        candidate_k: int = 20,
        relevant_doc_ids: Iterable[str] | None = None,
        ideal_answer: str | None = None,
    ) -> SearchResponseDTO:
        response, _ = self._run_search(
            request.query,
            request.documents,
            mode=mode,
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
        )
        return SearchResponseDTO(
            query=request.query,
            mode=mode,
            results=response.results,
            answer=response.answer,
            metrics=response.metrics,
            algorithm_details=response.algorithm_details,
        )

    def comparar_por_texto(
        self,
        request: SearchRequestDTO,
        top_k: int = 5,
        candidate_k: int = 20,
        relevant_doc_ids: Iterable[str] | None = None,
        ideal_answer: str | None = None,
    ) -> SearchResponseDTO:
        prepared = self._buscar_use_case.prepare_vectors(request.query, request.documents)

        classical, _ = self._run_search(
            request.query,
            request.documents,
            mode='classical',
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
            prepared=prepared,
        )
        quantum, _ = self._run_search(
            request.query,
            request.documents,
            mode='quantum',
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
            prepared=prepared,
        )

        comparison = SearchComparisonDTO(classical=classical, quantum=quantum)
        return SearchResponseDTO(
            query=request.query,
            mode='compare',
            results=classical.results,
            answer=classical.answer,
            metrics=classical.metrics,
            comparison=comparison,
        )

    def buscar_dataset_indexado(
        self,
        query: str,
        indexed_documents: Sequence[DocumentDTO],
        indexed_vectors: Sequence[Sequence[float]],
        mode: str = 'classical',
        top_k: int = 5,
        candidate_k: int = 20,
        relevant_doc_ids: Iterable[str] | None = None,
        ideal_answer: str | None = None,
    ) -> SearchResponseDTO:
        prepared = self._buscar_use_case.prepare_with_indexed_vectors(
            query,
            indexed_documents,
            indexed_vectors,
        )

        response, _ = self._run_search(
            query,
            indexed_documents,
            mode=mode,
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
            prepared=prepared,
        )
        return SearchResponseDTO(
            query=query,
            mode=mode,
            results=response.results,
            answer=response.answer,
            metrics=response.metrics,
            algorithm_details=response.algorithm_details,
        )

    def comparar_dataset_indexado(
        self,
        query: str,
        indexed_documents: Sequence[DocumentDTO],
        indexed_vectors: Sequence[Sequence[float]],
        top_k: int = 5,
        candidate_k: int = 20,
        relevant_doc_ids: Iterable[str] | None = None,
        ideal_answer: str | None = None,
    ) -> SearchResponseDTO:
        prepared = self._buscar_use_case.prepare_with_indexed_vectors(
            query,
            indexed_documents,
            indexed_vectors,
        )

        classical, _ = self._run_search(
            query,
            indexed_documents,
            mode='classical',
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
            prepared=prepared,
        )
        quantum, _ = self._run_search(
            query,
            indexed_documents,
            mode='quantum',
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
            prepared=prepared,
        )

        comparison = SearchComparisonDTO(classical=classical, quantum=quantum)
        return SearchResponseDTO(
            query=query,
            mode='compare',
            results=classical.results,
            answer=classical.answer,
            metrics=classical.metrics,
            comparison=comparison,
        )

    def buscar_por_arquivo(
        self,
        request: SearchFileRequestDTO,
        mode: str = 'classical',
        top_k: int = 5,
        candidate_k: int = 20,
        ideal_answer: str | None = None,
    ) -> SearchResponseDTO:
        docs = self._buscar_por_arquivo_use_case.execute(request.filename, request.content)
        if not docs:
            return SearchResponseDTO(query=request.query, mode=mode, results=[])

        relevant_doc_ids = self._infer_relevant_doc_ids(docs, request.query, ideal_answer)
        return self.buscar_por_texto(
            SearchRequestDTO(query=request.query, documents=docs),
            mode=mode,
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
        )

    def comparar_por_arquivo(
        self,
        request: SearchFileRequestDTO,
        top_k: int = 5,
        candidate_k: int = 20,
        ideal_answer: str | None = None,
    ) -> SearchResponseDTO:
        docs = self._buscar_por_arquivo_use_case.execute(request.filename, request.content)
        if not docs:
            return SearchResponseDTO(query=request.query, mode='compare', results=[])

        relevant_doc_ids = self._infer_relevant_doc_ids(docs, request.query, ideal_answer)
        return self.comparar_por_texto(
            SearchRequestDTO(query=request.query, documents=docs),
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
        )

    @staticmethod
    def _infer_relevant_doc_ids(
        documents: Sequence[DocumentDTO],
        query_text: str,
        ideal_answer: str | None,
        limit: int = 3,
    ) -> list[str]:
        if not ideal_answer or not ideal_answer.strip():
            return []

        def tokenize(text: str) -> set[str]:
            return {
                token
                for token in re.findall(r'[a-z0-9]+', text.lower())
                if len(token) >= 3
            }

        query_tokens = tokenize(query_text)
        answer_tokens = tokenize(ideal_answer)
        if not query_tokens and not answer_tokens:
            return []

        scored: list[tuple[float, str]] = []
        for item in documents:
            doc_tokens = tokenize(item.text)
            if not doc_tokens:
                continue

            query_overlap = len(doc_tokens & query_tokens) / max(1, len(query_tokens))
            answer_overlap = len(doc_tokens & answer_tokens) / max(1, len(answer_tokens))
            score = (0.3 * query_overlap) + (0.7 * answer_overlap)
            if score <= 0:
                continue
            scored.append((score, item.doc_id))

        scored.sort(key=lambda row: row[0], reverse=True)
        return [doc_id for _, doc_id in scored[:limit]]

    @staticmethod
    def _build_algorithm_details(
        mode: str,
        candidate_k: int,
        total_documents: int,
        results: Sequence[SearchResult],
    ) -> SearchAlgorithmDetailsDTO:
        if mode != 'quantum':
            return SearchAlgorithmDetailsDTO(
                algorithm='classical',
                comparator='cosine_similarity',
                candidate_strategy='Avalia similaridade em todos os documentos',
                description='Calcula similaridade coseno entre embedding da pergunta e embedding de cada documento.',
                debug={
                    'total_documents': int(total_documents),
                    'rescored_count': int(len(results)),
                },
            )

        traces = [item.quantum_trace for item in results if item.quantum_trace]
        methods = sorted({str(trace.get('method')) for trace in traces if trace.get('method')})
        used_projection = any(bool(trace.get('used_projection')) for trace in traces)
        sample_trace = traces[0] if traces else {}
        selected_candidates = max(1, min(candidate_k, total_documents)) if total_documents > 0 else 0

        description = (
            'Pre-seleciona candidatos pelo score classico e reordena com swap test quantico no PennyLane.'
        )
        if used_projection:
            description += ' Como o embedding excede 64 dimensoes, ocorre projecao para simular o circuito.'

        return SearchAlgorithmDetailsDTO(
            algorithm='quantum',
            comparator='swap_test (PennyLane)',
            candidate_strategy=f'Pre-seleciona top-{selected_candidates} classico e reavalia com swap test',
            description=description,
            debug={
                'methods': methods,
                'used_projection': used_projection,
                'total_documents': int(total_documents),
                'selected_candidates': int(selected_candidates),
                'rescored_count': int(len(results)),
                'original_dim': sample_trace.get('original_dim'),
                'prepared_dim': sample_trace.get('prepared_dim'),
                'n_qubits': sample_trace.get('n_qubits'),
            },
        )

    def _run_search(
        self,
        query: str,
        documents,
        mode: str,
        top_k: int,
        candidate_k: int,
        relevant_doc_ids: Iterable[str] | None,
        ideal_answer: str | None,
        prepared: PreparedSearchInput | None = None,
    ) -> tuple[SearchResponseLiteDTO, Sequence[SearchResult]]:
        start = time.perf_counter()
        prepared_input = prepared or self._buscar_use_case.prepare_vectors(query, documents)

        if prepared_input is None:
            results: Sequence[SearchResult] = []
            total_documents = 0
        else:
            total_documents = len(prepared_input.documents)
            results = self._buscar_use_case.score(
                query,
                documents,
                mode=mode,
                candidate_k=candidate_k,
                prepared=prepared_input,
            )

        latency_ms = (time.perf_counter() - start) * 1000

        answer = self._buscar_use_case.build_answer(
            query,
            list(results),
            query_vector=prepared_input.query_vector if prepared_input else None,
        )
        metrics = compute_ranking_metrics(
            results,
            relevant_doc_ids=relevant_doc_ids,
            k=top_k,
            latency_ms=latency_ms,
            candidate_k=candidate_k,
        )

        answer_similarity = self._compute_answer_similarity(answer, ideal_answer)
        metrics = replace(
            metrics,
            answer_similarity=answer_similarity,
            has_ideal_answer=bool(ideal_answer and ideal_answer.strip()),
        )

        if self._trace_repository and prepared_input:
            try:
                self._trace_repository.persist_run(
                    query=query,
                    mode=mode,
                    top_k=top_k,
                    candidate_k=candidate_k,
                    prepared=prepared_input,
                    results=list(results),
                )
            except Exception as exc:  # pragma: no cover - persistence must not break search
                logger.warning('Failed to persist search trace: %s', exc)

        algorithm_details = self._build_algorithm_details(
            mode=mode,
            candidate_k=candidate_k,
            total_documents=total_documents,
            results=results,
        )

        response = SearchResponseLiteDTO(
            results=results_to_dtos(list(results)[:top_k]),
            answer=answer,
            metrics=metrics,
            algorithm_details=algorithm_details,
        )
        return response, results

    def _compute_answer_similarity(self, answer: str | None, ideal_answer: str | None) -> float | None:
        if not answer or not ideal_answer:
            return None
        if not self._answer_embedder or not self._answer_comparator:
            return None

        try:
            vectors = self._answer_embedder.embed_texts([answer, ideal_answer])
            if len(vectors) != 2:
                return None
            return float(self._answer_comparator.compare(vectors[0], vectors[1]))
        except Exception as exc:  # pragma: no cover - similarity failure must not break search
            logger.warning('Failed to compute answer similarity: %s', exc)
            return None
