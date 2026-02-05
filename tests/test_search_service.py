from application.dtos import DocumentDTO, SearchFileRequestDTO, SearchRequestDTO
from application.services import SearchService
from application.use_cases import BuscarPorArquivoUseCase, RealizarBuscaUseCase
from application.interfaces import DocumentTextExtractor, Embedder, QuantumComparator


class FakeEmbedder(Embedder):
    def embed_texts(self, texts):
        return [[len(t)] for t in texts]


class FakeComparator(QuantumComparator):
    def compare(self, vector_a, vector_b):
        return 1.0 if vector_a == vector_b else 0.0


class FakeExtractor(DocumentTextExtractor):
    def extract(self, filename: str, content: bytes) -> str:
        return content.decode("utf-8")


def _build_service():
    buscar_use_case = RealizarBuscaUseCase(FakeEmbedder(), FakeComparator())
    buscar_por_arquivo_use_case = BuscarPorArquivoUseCase(FakeExtractor())
    return SearchService(buscar_use_case, buscar_por_arquivo_use_case)


def test_search_service_text():
    service = _build_service()
    request = SearchRequestDTO(
        query="abc",
        documents=[DocumentDTO(doc_id="1", text="abc"), DocumentDTO(doc_id="2", text="ab")],
    )

    response = service.buscar_por_texto(request)

    assert response.query == "abc"
    assert response.results[0].doc_id == "1"


def test_search_service_file():
    service = _build_service()
    request = SearchFileRequestDTO(query="abc", filename="doc.txt", content=b"abc")

    response = service.buscar_por_arquivo(request)

    assert response.query == "abc"
    assert response.results[0].doc_id == "uploaded-1"
