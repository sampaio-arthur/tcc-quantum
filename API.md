API Documentation - Quantum Search (TCC)

Base
- URL: http://localhost:8000
- Framework: FastAPI
- Banco: PostgreSQL com pgvector

Dataset e indexacao
POST /search/dataset/index
Body exemplo:
{ dataset_id: mini-rag, force_reindex: false }

Resposta exemplo:
{ dataset_id: mini-rag, indexed_documents: 4, reused_existing: true, embedder_provider: gemini, embedder_model: gemini-embedding-001 }

Busca comparativa classico x quantico
POST /search/dataset
Body exemplo:
{ dataset_id: mini-rag, query: qual o impacto das nanoparticulas, mode: compare, top_k: 5, candidate_k: 20 }

Tambem aceita query_id.

Campos de metricas retornados:
- accuracy_at_k
- recall_at_k
- mrr
- ndcg_at_k
- answer_similarity
- has_ideal_answer
- latency_ms
- k
- candidate_k
- has_labels

Fallback de baixa relevancia:
- answer: Nao foi possivel consultar.

Gabaritos de acuracia
GET /benchmarks/labels?dataset_id=mini-rag
Retorna lista com benchmark_id, dataset_id, query_text, ideal_answer e relevant_doc_ids.

POST /benchmarks/labels
Body exemplo:
{ dataset_id: mini-rag, query_text: qual o impacto das nanoparticulas, ideal_answer: resposta ideal para avaliacao }

Regra:
- relevant_doc_ids e inferido automaticamente pelo backend usando pergunta e resposta ideal.

DELETE /benchmarks/labels/{dataset_id}/{benchmark_id}
Remove o gabarito.

Outros endpoints
- GET /datasets
- GET /datasets/{dataset_id}
- POST /search
- POST /search/file
- GET /health
