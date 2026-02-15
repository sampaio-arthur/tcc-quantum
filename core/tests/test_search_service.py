from application.dtos import DocumentDTO, SearchFileRequestDTO, SearchRequestDTO
from application.interfaces import DocumentTextExtractor, Embedder, QuantumComparator
from application.services import SearchService
from application.use_cases import BuscarPorArquivoUseCase, RealizarBuscaUseCase


class FakeEmbedder(Embedder):
    def __init__(self):
        self.calls = 0

    def embed_texts(self, texts):
        self.calls += 1
        return [[len(t)] for t in texts]


class FakeComparator(QuantumComparator):
    def compare(self, vector_a, vector_b):
        return 1.0 if vector_a == vector_b else 0.0


class FakeExtractor(DocumentTextExtractor):
    def extract(self, filename: str, content: bytes) -> str:
        return content.decode("utf-8")


def _build_service(embedder: FakeEmbedder | None = None):
    active_embedder = embedder or FakeEmbedder()
    buscar_use_case = RealizarBuscaUseCase(active_embedder, FakeComparator())
    buscar_por_arquivo_use_case = BuscarPorArquivoUseCase(FakeExtractor())
    return SearchService(buscar_use_case, buscar_por_arquivo_use_case), active_embedder


def test_search_service_text():
    service, _ = _build_service()
    request = SearchRequestDTO(
        query="abc",
        documents=[DocumentDTO(doc_id="1", text="abc"), DocumentDTO(doc_id="2", text="ab")],
    )

    response = service.buscar_por_texto(request)

    assert response.query == "abc"
    assert response.results[0].doc_id == "1"


def test_search_service_file():
    service, _ = _build_service()
    request = SearchFileRequestDTO(query="abc", filename="doc.txt", content=b"abc")

    response = service.buscar_por_arquivo(request)

    assert response.query == "abc"
    assert response.results[0].doc_id == "uploaded-1"


def test_compare_reuses_same_embeddings_for_classical_and_quantum(monkeypatch):
    embedder = FakeEmbedder()
    service, _ = _build_service(embedder=embedder)

    monkeypatch.setattr(
        service._buscar_use_case,
        "build_answer",
        lambda query, results, query_vector=None: "ok",
    )

    request = SearchRequestDTO(
        query="abc",
        documents=[
            DocumentDTO(doc_id="1", text="abc"),
            DocumentDTO(doc_id="2", text="ab"),
            DocumentDTO(doc_id="3", text="abcd"),
        ],
    )

    service.comparar_por_texto(request)

    # One call for query, one call for all document chunks.
    assert embedder.calls == 2
