from application.dtos import DocumentDTO
from application.interfaces import Embedder, QuantumComparator
from application.use_cases import RealizarBuscaUseCase


class FakeEmbedder(Embedder):
    def embed_texts(self, texts):
        # simple 2D embeddings: length and vowel count
        vowels = set('aeiouAEIOU')
        return [[len(t), sum(1 for c in t if c in vowels)] for t in texts]


class FakeComparator(QuantumComparator):
    def compare(self, vector_a, vector_b):
        # simple similarity: inverse of manhattan distance
        dist = abs(vector_a[0] - vector_b[0]) + abs(vector_a[1] - vector_b[1])
        return 1.0 / (1.0 + dist)


def test_realizar_busca_orders_results():
    use_case = RealizarBuscaUseCase(FakeEmbedder(), FakeComparator())
    docs = [
        DocumentDTO(doc_id='1', text='abc'),
        DocumentDTO(doc_id='2', text='abcd'),
        DocumentDTO(doc_id='3', text='ab'),
    ]

    response = use_case.execute('abc', docs)

    assert response.query == 'abc'
    assert len(response.results) == 3
    # Expect the exact match to be first
    assert response.results[0].doc_id == '1'


def test_prepare_with_indexed_vectors_uses_existing_doc_embeddings():
    use_case = RealizarBuscaUseCase(FakeEmbedder(), FakeComparator())
    docs = [
        DocumentDTO(doc_id='1', text='doc 1'),
        DocumentDTO(doc_id='2', text='doc 2'),
    ]
    indexed_vectors = [[0.9, 0.1], [0.1, 0.9]]

    prepared = use_case.prepare_with_indexed_vectors('query', docs, indexed_vectors)

    assert prepared is not None
    assert prepared.doc_vectors == indexed_vectors
    assert len(prepared.query_vector) == 2
