import pytest
from fastapi.testclient import TestClient

from application.dtos import (
    SearchComparisonDTO,
    SearchMetricsDTO,
    SearchResponseDTO,
    SearchResponseLiteDTO,
    SearchResultDTO,
)
from infrastructure.api.fastapi_app import app


class FakeSearchService:
    def _build_metrics(self) -> SearchMetricsDTO:
        return SearchMetricsDTO(
            recall_at_k=1.0,
            mrr=1.0,
            ndcg_at_k=1.0,
            latency_ms=1.0,
            k=5,
            candidate_k=20,
            has_labels=True,
        )

    def buscar_por_texto(self, request, mode="classical", **_kwargs) -> SearchResponseDTO:
        return SearchResponseDTO(
            query=request.query,
            mode=mode,
            results=[SearchResultDTO(doc_id="doc-1", text="texto", score=0.9)],
            answer="ok",
            metrics=self._build_metrics(),
        )

    def comparar_por_texto(self, request, **_kwargs) -> SearchResponseDTO:
        base = SearchResponseLiteDTO(
            results=[SearchResultDTO(doc_id="doc-1", text="texto", score=0.9)],
            answer="ok",
            metrics=self._build_metrics(),
        )
        return SearchResponseDTO(
            query=request.query,
            mode="compare",
            results=base.results,
            answer=base.answer,
            metrics=base.metrics,
            comparison=SearchComparisonDTO(classical=base, quantum=base),
        )


@pytest.fixture(autouse=True)
def _patch_service(monkeypatch):
    from infrastructure.api.search import search_controller

    monkeypatch.setattr(search_controller, "_build_service", lambda: FakeSearchService())


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_dataset_endpoint():
    payload = {
        "dataset_id": "mini-rag",
        "query_id": "q1",
        "mode": "compare",
        "top_k": 5,
        "candidate_k": 20,
    }

    response = client.post("/search/dataset", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["query"]
    assert data["mode"] == "compare"
    assert data["comparison"]
