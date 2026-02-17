from application.services.search.metrics import compute_ranking_metrics
from application.use_cases.search.realizar_busca_use_case import SearchResult
from domain.entities import Document


def _result(doc_id: str, score: float) -> SearchResult:
    return SearchResult(document=Document(doc_id=doc_id, text=doc_id), score=score)


def test_metrics_include_accuracy_at_k_with_labels():
    results = [_result('doc-1', 0.9), _result('doc-2', 0.8), _result('doc-3', 0.1)]

    metrics = compute_ranking_metrics(
        results=results,
        relevant_doc_ids=['doc-2'],
        k=1,
        latency_ms=12.0,
        candidate_k=3,
    )

    assert metrics.has_labels is True
    assert metrics.accuracy_at_k == 0.0

    metrics_k2 = compute_ranking_metrics(
        results=results,
        relevant_doc_ids=['doc-2'],
        k=2,
        latency_ms=12.0,
        candidate_k=3,
    )

    assert metrics_k2.accuracy_at_k == 1.0
    assert metrics_k2.recall_at_k == 1.0
