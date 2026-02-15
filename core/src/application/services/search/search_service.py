from __future__ import annotations

import logging
import time
from typing import Iterable, Sequence

from application.dtos import (
    SearchComparisonDTO,
    SearchFileRequestDTO,
    SearchRequestDTO,
    SearchResponseDTO,
    SearchResponseLiteDTO,
)
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
    ) -> None:
        self._buscar_use_case = buscar_use_case
        self._buscar_por_arquivo_use_case = buscar_por_arquivo_use_case
        self._trace_repository = trace_repository

    def buscar_por_texto(
        self,
        request: SearchRequestDTO,
        mode: str = "classical",
        top_k: int = 5,
        candidate_k: int = 20,
        relevant_doc_ids: Iterable[str] | None = None,
    ) -> SearchResponseDTO:
        response, _ = self._run_search(
            request.query,
            request.documents,
            mode=mode,
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
        )
        return SearchResponseDTO(
            query=request.query,
            mode=mode,
            results=response.results,
            answer=response.answer,
            metrics=response.metrics,
        )

    def comparar_por_texto(
        self,
        request: SearchRequestDTO,
        top_k: int = 5,
        candidate_k: int = 20,
        relevant_doc_ids: Iterable[str] | None = None,
    ) -> SearchResponseDTO:
        prepared = self._buscar_use_case.prepare_vectors(request.query, request.documents)

        classical, _ = self._run_search(
            request.query,
            request.documents,
            mode="classical",
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            prepared=prepared,
        )
        quantum, _ = self._run_search(
            request.query,
            request.documents,
            mode="quantum",
            top_k=top_k,
            candidate_k=candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            prepared=prepared,
        )

        comparison = SearchComparisonDTO(classical=classical, quantum=quantum)
        return SearchResponseDTO(
            query=request.query,
            mode="compare",
            results=classical.results,
            answer=classical.answer,
            metrics=classical.metrics,
            comparison=comparison,
        )

    def buscar_por_arquivo(
        self,
        request: SearchFileRequestDTO,
        mode: str = "classical",
        top_k: int = 5,
        candidate_k: int = 20,
    ) -> SearchResponseDTO:
        docs = self._buscar_por_arquivo_use_case.execute(request.filename, request.content)
        if not docs:
            return SearchResponseDTO(query=request.query, mode=mode, results=[])
        return self.buscar_por_texto(
            SearchRequestDTO(query=request.query, documents=docs),
            mode=mode,
            top_k=top_k,
            candidate_k=candidate_k,
        )

    def comparar_por_arquivo(
        self,
        request: SearchFileRequestDTO,
        top_k: int = 5,
        candidate_k: int = 20,
    ) -> SearchResponseDTO:
        docs = self._buscar_por_arquivo_use_case.execute(request.filename, request.content)
        if not docs:
            return SearchResponseDTO(query=request.query, mode="compare", results=[])
        return self.comparar_por_texto(
            SearchRequestDTO(query=request.query, documents=docs),
            top_k=top_k,
            candidate_k=candidate_k,
        )

    def _run_search(
        self,
        query: str,
        documents,
        mode: str,
        top_k: int,
        candidate_k: int,
        relevant_doc_ids: Iterable[str] | None,
        prepared: PreparedSearchInput | None = None,
    ) -> tuple[SearchResponseLiteDTO, Sequence[SearchResult]]:
        start = time.perf_counter()
        prepared_input = prepared or self._buscar_use_case.prepare_vectors(query, documents)

        if prepared_input is None:
            results: Sequence[SearchResult] = []
        else:
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

        response = SearchResponseLiteDTO(
            results=results_to_dtos(list(results)[:top_k]),
            answer=answer,
            metrics=metrics,
        )
        return response, results
