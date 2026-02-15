from application.dtos import DocumentDTO, SearchRequestDTO
from application.services import SearchService
from application.use_cases import BuscarPorArquivoUseCase, RealizarBuscaUseCase
from infrastructure.api.search.file_reader import PdfTxtDocumentTextExtractor
from infrastructure.embeddings import build_embedder_from_env
from infrastructure.quantum import CosineSimilarityComparator, SwapTestQuantumComparator


def main() -> None:
    query = "Algoritmos de IA"
    documents = [
        DocumentDTO(doc_id="doc-1", text="Redes Neurais"),
        DocumentDTO(doc_id="doc-2", text="Algoritmos Geneticos e Otimizacao"),
        DocumentDTO(doc_id="doc-3", text="Sistemas Embarcados"),
    ]

    embedder = build_embedder_from_env()
    classical = CosineSimilarityComparator()
    quantum = SwapTestQuantumComparator()
    buscar_use_case = RealizarBuscaUseCase(embedder, classical, quantum)
    buscar_por_arquivo_use_case = BuscarPorArquivoUseCase(PdfTxtDocumentTextExtractor())
    service = SearchService(buscar_use_case, buscar_por_arquivo_use_case)

    request = SearchRequestDTO(query=query, documents=documents)
    response = service.buscar_por_texto(request, mode="classical")

    print(f"Consulta: {response.query}")
    for item in response.results:
        print(f"{item.doc_id} | {item.text} -> Similaridade: {item.score:.2%}")


if __name__ == "__main__":
    main()
