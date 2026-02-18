Documentacao Tecnica - Quantum Search (TCC)

Escopo tecnico
- Comparar busca classica e busca quantico-inspirada no mesmo pipeline.
- Medir acuracia de ranking, similaridade de resposta e latencia.

Arquitetura

Camadas
- domain: entidades e contratos de dominio.
- application: DTOs, servicos e use cases.
- infrastructure: API, persistencia, embeddings, comparadores quanticos e classicos.
- frontend: SPA React para operacao da plataforma.

Servicos em runtime
- core: API FastAPI.
- frontend: aplicacao React com Vite.
- db: Postgres com pgvector.

Topologia
- frontend chama core por HTTP.
- core consulta base relacional e vetorial no Postgres.
- core utiliza provedor de embeddings configurado por ambiente.

Pipeline ponta a ponta

Etapa 1 - Dataset
- Fonte: core/data/public_datasets.json.
- Estrutura: datasets, documents, queries.

Etapa 2 - Indexacao
1) Ler documentos do dataset.
2) Gerar embeddings.
3) Persistir em dataset_document_index.
4) Reusar indice existente quando provider e model coincidirem.

Etapa 3 - Consulta
1) Receber pergunta.
2) Gerar embedding da pergunta.
3) Executar ramo classico e ramo quantico quando mode compare.
4) Gerar resposta final com trechos mais relevantes.

Etapa 4 - Avaliacao
1) Resolver gabarito por query_id ou query_text.
2) Calcular metricas de ranking usando relevant_doc_ids.
3) Calcular answer_similarity com resposta ideal quando existir.
4) Retornar metrics e algorithm_details.

Fluxo classico
- Calcula similaridade cosseno pergunta x todos documentos.
- Ordena por score descrescente.
- Usa top resultados para resposta e metricas.

Fluxo quantico-inspirado
- Calcula score classico inicial para todos documentos.
- Seleciona candidate_k melhores candidatos classicos.
- Reavalia candidatos com swap test (PennyLane).
- Reordena por score quantico final.

Dimensionalidade quantica
- Simulacao trabalha com limite pratico de 64 dimensoes.
- Vetores maiores sao projetados para 64 antes do circuito.
- O retorno inclui debug com method, used_projection e n_qubits.

Custo de vetores (embeddings)

Pipeline de custo
1) PDF/TXT -> extracao de texto.
2) Chunking -> gera n_chunks.
3) Embedding -> custo por chamada (API ou local).
4) Armazenamento vetorial -> custo de RAM/disco e indices.
5) Busca -> custo de CPU/latencia (ex.: HNSW vs full scan).

Estimativas basicas
- Tokens ~= caracteres / 4 (regra pratica).
- n_chunks ~= tokens / (chunk_size - overlap).
- Vetores (float32): tamanho_bytes ~= n_chunks x dimensao x 4.
- Armazenamento real com metadados e indices tende a 1.3x a 1.8x do tamanho bruto.

Exemplo rapido (768 dims)
- 10.000 chunks x 768 x 4 bytes ~= 30,7 MB (so vetores).
- Com overhead de indices e metadados: ~40-55 MB.

Exemplo pratico com chunking atual (max_chars=800, overlap=150)
- Passo efetivo ~= 650 chars por chunk.

| Tamanho do texto | n_chunks (aprox) | Vetores (768D) | Vetores + overhead |
| --- | --- | --- | --- |
| 50 KB | 79 | ~0,23 MB | ~0,30-0,41 MB |
| 500 KB | 788 | ~2,31 MB | ~3,0-4,2 MB |
| 1 MB | 1.614 | ~4,73 MB | ~6,1-8,5 MB |
| 5 MB | 8.066 | ~23,6 MB | ~30-43 MB |

Custos diretos
- Geracao (API paga): custo = embeddings x preco_por_embedding.
- Armazenamento: custo mensal do Postgres/pgvector conforme GB.
- Busca: depende de indice (HNSW reduz latencia e CPU; full scan custa mais em CPU).

Boas praticas de custo
- Cache de embeddings para evitar recomputar.
- Ajustar chunk_size/overlap conforme recall vs custo.
- Monitorar n_chunks por documento para evitar explodir o custo.

Busca por arquivo

Entrada
- Arquivo TXT ou PDF.
- Pergunta opcional.

Processamento
1) Extrair texto.
2) Chunking por sentencas com overlap.
3) Buscar sobre os chunks.
4) Se existir gabarito para a pergunta no dataset padrao, usar ideal_answer.
5) Inferir relevant_doc_ids nos chunks para ranking.

Persistencia

Tabelas funcionais
- users
- conversations
- messages
- dataset_document_index
- benchmark_ground_truths
- search_runs
- search_vector_records

Gabarito e inferencia de relevantes
- Entrada do usuario: query_text e ideal_answer.
- Backend tokeniza texto e calcula overlap com documentos.
- Score ponderado por pergunta e resposta ideal.
- Seleciona top documentos como relevant_doc_ids.

Metricas

Ranking
- accuracy_at_k
- recall_at_k
- mrr
- ndcg_at_k

Resposta
- answer_similarity

Operacao
- latency_ms

Campos de controle
- has_labels
- has_ideal_answer
- k
- candidate_k

Fallbacks e limites
- Resposta fallback por baixa relevancia: Nao foi possivel consultar.
- Limiar: SEARCH_MIN_RELEVANCE_SCORE.
- Rate limit: 10 requisicoes por minuto por host nas rotas de busca.
- Upload em /search/file limitado a 5 MB.

Seguranca
- Autenticacao JWT.
- Hash de senha com bcrypt.
- Endpoints de conversa e mensagens protegidos por usuario autenticado.

Configuracao

Variaveis principais
- APP_ENV
- SECRET_KEY
- JWT_SECRET
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD
- DATABASE_URL
- VITE_API_BASE_URL
- EMBEDDER_PROVIDER
- GEMINI_API_KEY
- GEMINI_EMBEDDING_MODEL

Variaveis funcionais
- DEFAULT_DATASET_ID
- SEARCH_MIN_RELEVANCE_SCORE

Procedimento operacional recomendado
1) Subir servicos.
2) Registrar e autenticar usuario.
3) Cadastrar gabaritos.
4) Indexar dataset.
5) Executar compare classico x quantico.
6) Avaliar metrics e algorithm_details.
7) Repetir com novos casos de teste.

Tecnologias e bibliotecas

Backend
- Python, FastAPI, Uvicorn.
- SQLAlchemy, psycopg, pgvector.
- NumPy, SciPy, pandas, scikit-learn.
- PennyLane, Qiskit, Qiskit Aer.
- pypdf.
- python-jose, passlib, bcrypt.

Frontend
- React, TypeScript, Vite.
- React Router.
- Tailwind CSS.
- Radix UI.
- TanStack React Query.

Infra
- Docker Compose.
- Container Postgres com imagem pgvector/pgvector:pg16.

Limitacoes atuais
- Dataset ainda pequeno para inferencias estatisticas amplas.
- Simulacao quantica em software, nao hardware quantico real.
- CORS aberto para qualquer origem no ambiente atual.

Evolucoes recomendadas
- Ampliar base de dados e variedade de gabaritos.
- Criar benchmark batch para regressao continua.
- Construir dashboard historico de runs e metricas.
- Endurecer configuracao de seguranca para producao.
