API Documentation - Quantum Search (TCC)

Informacoes gerais
- Base URL local: http://localhost:8000
- Framework: FastAPI
- Banco: PostgreSQL com pgvector
- Autenticacao: JWT Bearer

Formato de payload
- JSON para endpoints de dados estruturados.
- multipart/form-data para upload em /search/file.

Codigos de resposta comuns
- 200 sucesso
- 201 criado
- 204 removido sem corpo
- 400 erro de validacao
- 401 nao autenticado
- 404 recurso nao encontrado
- 413 arquivo acima do limite
- 429 limite de requisicoes excedido

Endpoint de health
GET /health
Resposta:
- status: ok

Autenticacao
POST /auth/register
Finalidade
- Cria um usuario.

Body
- email
- password

Regras
- email unico
- password com limite de 72 bytes para compatibilidade bcrypt

POST /auth/login
Finalidade
- Gera token JWT.

Entrada
- form-urlencoded com username e password

Saida
- access_token
- token_type

GET /auth/me
Finalidade
- Retorna usuario autenticado.

Header obrigatorio
- Authorization Bearer token

Conversas
POST /conversations
Finalidade
- Cria conversa para usuario autenticado.

Body
- title opcional

GET /conversations
Finalidade
- Lista conversas do usuario autenticado.

GET /conversations/{conversation_id}
Finalidade
- Retorna conversa e mensagens.

POST /conversations/{conversation_id}/messages
Finalidade
- Adiciona mensagem na conversa.

Body
- role
- content

Roles permitidos
- user
- assistant
- system

DELETE /conversations/{conversation_id}
Finalidade
- Remove conversa.

Datasets
GET /datasets
Finalidade
- Lista datasets disponiveis.

GET /datasets/{dataset_id}
Finalidade
- Detalha dataset, queries e doc_ids.

Benchmarks e gabaritos
GET /benchmarks/labels
Query param
- dataset_id

Finalidade
- Lista gabaritos salvos para um dataset.

POST /benchmarks/labels
Finalidade
- Cria ou atualiza gabarito.

Body
- dataset_id
- query_text
- ideal_answer

Regra importante
- relevant_doc_ids e inferido automaticamente pelo backend.

DELETE /benchmarks/labels/{dataset_id}/{benchmark_id}
Finalidade
- Remove gabarito.

Busca geral por lista de documentos
POST /search
Finalidade
- Busca sobre lista de textos enviada na propria requisicao.

Body
- query
- documents lista de strings
- mode: classical, quantum, compare
- top_k
- candidate_k

Busca por arquivo
POST /search/file
Finalidade
- Busca sobre conteudo de arquivo enviado pelo usuario.

Entrada multipart
- query
- file
- mode
- top_k
- candidate_k

Regras
- arquivo obrigatorio
- limite de 5 MB
- formatos aceitos: TXT e PDF
- fallback de query vazia: Resumo do documento

Comportamento de avaliacao
- Se existir gabarito salvo para a pergunta no dataset padrao, aplica ideal_answer e calcula metricas.
- relevant_doc_ids para ranking sao inferidos sobre os chunks do arquivo.

Indexacao de dataset
POST /search/dataset/index
Finalidade
- Gera ou reusa indice vetorial persistente para dataset.

Body
- dataset_id
- force_reindex

Resposta
- dataset_id
- indexed_documents
- reused_existing
- embedder_provider
- embedder_model

Busca em dataset indexado
POST /search/dataset
Finalidade
- Busca no dataset com comparacao classica vs quantica e avaliacao por gabarito.

Body
- dataset_id
- query opcional
- query_id opcional
- mode
- top_k
- candidate_k

Resolucao de gabarito
- Se query_id existir, backend busca benchmark salvo por id.
- Se nao encontrar benchmark salvo, tenta query pre-definida no dataset.
- Se query texto existir, backend tenta benchmark salvo por texto normalizado.

Campos de resposta de busca
- query
- mode
- results
- answer
- metrics
- comparison quando modo compare
- algorithm_details

Estrutura de metrics
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

Estrutura de algorithm_details
- algorithm
- comparator
- candidate_strategy
- description
- debug

Comportamento de fallback
- Quando a consulta nao atinge relevancia minima, answer retorna Nao foi possivel consultar.

Rate limit nas rotas de busca
- Janela: 60 segundos
- Limite: 10 requisicoes por host
- Rotas afetadas: /search, /search/file, /search/dataset/index, /search/dataset

Resumo de endpoints principais
- POST /auth/register
- POST /auth/login
- GET /auth/me
- POST /conversations
- GET /conversations
- GET /conversations/{conversation_id}
- POST /conversations/{conversation_id}/messages
- DELETE /conversations/{conversation_id}
- GET /datasets
- GET /datasets/{dataset_id}
- GET /benchmarks/labels
- POST /benchmarks/labels
- DELETE /benchmarks/labels/{dataset_id}/{benchmark_id}
- POST /search
- POST /search/file
- POST /search/dataset/index
- POST /search/dataset
- GET /health
