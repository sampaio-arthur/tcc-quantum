# Documentacao do Projeto - Quantum Search (TCC)

## Objetivo
Comparar busca semantica classica e abordagem quantico-inspirada no contexto de RAG, medindo qualidade de ranking e latencia.

## O que a plataforma faz
- Recebe PDF/TXT ou usa dataset publico.
- Executa busca classica, quantica ou `compare`.
- Gera resposta textual baseada em sentencas relevantes.
- Calcula metricas (Recall@K, MRR, NDCG@K quando houver rotulos) e latencia.
- Persiste execucoes de busca para auditoria e reproducao.

## Fluxo principal
1. Ingestao e chunking de documentos.
2. Geracao de embeddings via API Gemini (sem transformer local).
3. Ranking classico por cosine similarity.
4. Reranking quantico-inspirado por swap test.
5. Montagem de resposta e metricas.
6. Persistencia dos rastros no PostgreSQL com pgvector.

## Modos de busca
- `classical`: ranking direto por cosine.
- `quantum`: prefiltra candidatos por score classico e reranqueia com swap test.
- `compare`: executa os dois modos com o mesmo conjunto de embeddings.

## Persistencia de experimentos
Banco: PostgreSQL com extensao `vector` (pgvector).

Tabelas:
- `search_runs`: metadados da execucao (query, modo, top_k, candidate_k, modelo de embedding).
- `search_vector_records`: vetores e tra?os por execucao.

Tipos de registro (`kind`):
- `query_embedding`
- `document_embedding`
- `quantum_query_state`
- `quantum_doc_state`

Observacao sobre estados quanticos:
- O sistema persiste o estado preparado para o circuito (amplitudes normalizadas/padded) e metadados do trace.
- Em dimensoes altas, pode ocorrer fallback para cosine por custo computacional.

## Tecnologias
Backend:
- Python + FastAPI
- Gemini Embeddings API
- PennyLane (simulacao quantica)
- SQLAlchemy + PostgreSQL
- pgvector

Frontend:
- React + Vite
- TailwindCSS

## Estrutura de codigo (resumo)
- `core/src/application/use_cases/search/realizar_busca_use_case.py`
- `core/src/application/services/search/search_service.py`
- `core/src/infrastructure/quantum/swap_test_comparator.py`
- `core/src/infrastructure/persistence/search_trace_repository.py`
- `core/src/infrastructure/persistence/models.py`
- `core/src/infrastructure/api/search/search_controller_pg.py`

## Execucao
1. Copie `.env.example` para `.env` e preencha os valores.
2. Suba com Docker:
```bash
docker compose build
docker compose up -d
```

## Limitacoes conhecidas
- Swap test simulado fica caro em alta dimensionalidade.
- Em cenarios de custo alto, o comparador quantico pode usar fallback classico.
- A resposta textual e extrativa (nao usa LLM gerador dedicado para resposta final).

## Proximos passos sugeridos
- Endpoint de auditoria para listar `search_runs` e rastros.
- Benchmark automatizado por dataset com relatorio reproducivel.
- Indices vetoriais adicionais e tuning de performance no Postgres.
