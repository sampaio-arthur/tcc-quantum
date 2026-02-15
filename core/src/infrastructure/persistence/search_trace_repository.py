import math
import os
from typing import Iterable

from sqlalchemy.orm import Session

from application.use_cases.search.realizar_busca_use_case import PreparedSearchInput, SearchResult
from infrastructure.persistence.models import SearchRun, SearchVectorRecord


def _normalize(values: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return values
    return [value / norm for value in values]


def _project_vector(values: list[float], dim: int = 64) -> list[float]:
    if not values:
        return [0.0] * dim

    projected = values[:dim]
    if len(projected) < dim:
        projected = projected + ([0.0] * (dim - len(projected)))
    return _normalize(projected)


def _to_float_list(values: Iterable[float]) -> list[float]:
    return [float(value) for value in values]


class SearchTraceRepository:
    def __init__(self, db: Session) -> None:
        self._db = db
        self._provider = os.getenv('EMBEDDER_PROVIDER', 'gemini').strip().lower()
        self._model = os.getenv('GEMINI_EMBEDDING_MODEL', 'gemini-embedding-001').strip()

    def persist_run(
        self,
        query: str,
        mode: str,
        top_k: int,
        candidate_k: int,
        prepared: PreparedSearchInput,
        results: list[SearchResult],
    ) -> None:
        run = SearchRun(
            query=query,
            mode=mode,
            top_k=top_k,
            candidate_k=candidate_k,
            embedder_provider=self._provider,
            embedder_model=self._model,
        )
        self._db.add(run)
        self._db.flush()

        self._db.add(
            SearchVectorRecord(
                run_id=run.id,
                kind='query_embedding',
                vector=_project_vector(prepared.query_vector),
                payload={
                    'full_vector': _to_float_list(prepared.query_vector),
                    'dimension': len(prepared.query_vector),
                },
            )
        )

        score_by_doc_id = {result.document.doc_id: result.score for result in results}

        for doc, doc_vector in zip(prepared.documents, prepared.doc_vectors):
            vector_list = _to_float_list(doc_vector)
            self._db.add(
                SearchVectorRecord(
                    run_id=run.id,
                    kind='document_embedding',
                    doc_id=doc.doc_id,
                    score=score_by_doc_id.get(doc.doc_id),
                    vector=_project_vector(vector_list),
                    payload={
                        'full_vector': vector_list,
                        'dimension': len(vector_list),
                    },
                    text_excerpt=doc.text[:500],
                )
            )

        if mode == 'quantum':
            persisted_query_state = False
            for result in results:
                trace = result.quantum_trace
                if not trace:
                    continue

                query_state = trace.get('query_state')
                doc_state = trace.get('doc_state')

                if query_state and not persisted_query_state:
                    query_state_list = _to_float_list(query_state)
                    self._db.add(
                        SearchVectorRecord(
                            run_id=run.id,
                            kind='quantum_query_state',
                            vector=_project_vector(query_state_list),
                            payload={
                                'state': query_state_list,
                                'dimension': len(query_state_list),
                                'trace': trace,
                            },
                        )
                    )
                    persisted_query_state = True

                if doc_state:
                    doc_state_list = _to_float_list(doc_state)
                    self._db.add(
                        SearchVectorRecord(
                            run_id=run.id,
                            kind='quantum_doc_state',
                            doc_id=result.document.doc_id,
                            score=result.score,
                            vector=_project_vector(doc_state_list),
                            payload={
                                'state': doc_state_list,
                                'dimension': len(doc_state_list),
                                'trace': trace,
                            },
                            text_excerpt=result.document.text[:500],
                        )
                    )

        self._db.commit()
