from application.use_cases import RealizarBuscaUseCase
from domain.entities import Document
from infrastructure.embeddings import LocalEmbedder
from infrastructure.quantum import SwapTestQuantumComparator


def main() -> None:
    query = "Algoritmos de IA"
    documents = [
        Document(doc_id="doc-1", text="Redes Neurais"),
        Document(doc_id="doc-2", text="Algoritmos Geneticos e Otimizacao"),
        Document(doc_id="doc-3", text="Sistemas Embarcados"),
    ]

    embedder = LocalEmbedder()
    comparator = SwapTestQuantumComparator()
    use_case = RealizarBuscaUseCase(embedder, comparator)

    results = use_case.execute(query, documents)

    print(f"Consulta: {query}")
    for item in results:
        print(f"{item.document.doc_id} | {item.document.text} -> Similaridade: {item.score:.2%}")


if __name__ == "__main__":
    main()
