from fastapi.testclient import TestClient
import pytest

from application.services import SearchService
from application.use_cases import BuscarPorArquivoUseCase, RealizarBuscaUseCase
from infrastructure.api.fastapi_app import app
from infrastructure.api.search.file_reader import PdfTxtDocumentTextExtractor
from infrastructure.api.search import search_controller_pg
from infrastructure.persistence.database import get_db
from infrastructure.quantum import CosineSimilarityComparator


class _FakeEmbedder:
    def embed_texts(self, texts):
        # Simple deterministic vectors for tests.
        return [[float(len(text)), 0.0, 0.0, 1.0] for text in texts]


class _DummyLabelRepository:
    def __init__(self, _db):
        pass

    def find_by_query_text(self, _dataset_id: str, _query_text: str):
        return None


client = TestClient(app)


@pytest.fixture(autouse=True)
def _override_dependencies(monkeypatch):
    def _fake_build_runtime(_db):
        embedder = _FakeEmbedder()
        classical = CosineSimilarityComparator()
        buscar_use_case = RealizarBuscaUseCase(embedder, classical, classical)
        buscar_por_arquivo = BuscarPorArquivoUseCase(PdfTxtDocumentTextExtractor())
        service = SearchService(buscar_use_case, buscar_por_arquivo)
        return service, embedder

    def _fake_get_db():
        yield None

    monkeypatch.setattr(search_controller_pg, "_build_runtime", _fake_build_runtime)
    monkeypatch.setattr(search_controller_pg, "BenchmarkLabelRepository", _DummyLabelRepository)
    app.dependency_overrides[get_db] = _fake_get_db
    yield
    app.dependency_overrides.clear()


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
