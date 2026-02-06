import math
from typing import Iterable, Sequence

from application.dtos import SearchMetricsDTO
from application.use_cases.search.realizar_busca_use_case import SearchResult


def compute_ranking_metrics(
    results: Sequence[SearchResult],
    relevant_doc_ids: Iterable[str] | None,
    k: int,
    latency_ms: float,
    candidate_k: int,
) -> SearchMetricsDTO:
    relevant_set = set(relevant_doc_ids or [])
    has_labels = len(relevant_set) > 0

    recall_at_k = None
    mrr = None
    ndcg_at_k = None

    if has_labels:
        top_k = results[:k]
        hits = [item for item in top_k if item.document.doc_id in relevant_set]
        recall_at_k = len(hits) / len(relevant_set)

        mrr = 0.0
        for index, item in enumerate(results, start=1):
            if item.document.doc_id in relevant_set:
                mrr = 1.0 / index
                break

        gains = [1.0 if item.document.doc_id in relevant_set else 0.0 for item in top_k]
        dcg = sum(gain / math.log2(idx + 2) for idx, gain in enumerate(gains))
        ideal_gains = [1.0] * min(k, len(relevant_set))
        idcg = sum(gain / math.log2(idx + 2) for idx, gain in enumerate(ideal_gains))
        ndcg_at_k = dcg / idcg if idcg > 0 else 0.0

    return SearchMetricsDTO(
        recall_at_k=recall_at_k,
        mrr=mrr,
        ndcg_at_k=ndcg_at_k,
        latency_ms=latency_ms,
        k=k,
        candidate_k=candidate_k,
        has_labels=has_labels,
    )
