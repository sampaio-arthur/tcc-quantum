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
            has_labels=False,
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

    def buscar_por_arquivo(self, request, mode="classical", **_kwargs) -> SearchResponseDTO:
        return SearchResponseDTO(
            query=request.query,
            mode=mode,
            results=[SearchResultDTO(doc_id="uploaded-1", text="texto", score=0.9)],
            answer="ok",
            metrics=self._build_metrics(),
        )

    def comparar_por_arquivo(self, request, **_kwargs) -> SearchResponseDTO:
        base = SearchResponseLiteDTO(
            results=[SearchResultDTO(doc_id="uploaded-1", text="texto", score=0.9)],
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


def test_search_endpoint():
    payload = {
        "query": "algoritmos",
        "documents": ["algoritmos", "outra coisa"],
    }

    response = client.post("/search", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "algoritmos"
    assert len(data["results"]) == 2
    assert data["answer"]


def test_search_file_endpoint_txt():
    response = client.post(
        "/search/file",
        data={"query": "algoritmos"},
        files={"file": ("doc.txt", b"algoritmos", "text/plain")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "algoritmos"
    assert len(data["results"]) == 1
    assert data["answer"]


def test_search_file_rejects_invalid_pdf_type():
    response = client.post(
        "/search/file",
        data={"query": "algoritmos"},
        files={"file": ("doc.pdf", b"%PDF-1.4 test", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Tipo de arquivo PDF invalido"
