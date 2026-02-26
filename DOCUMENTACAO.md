Documentacao Tecnica - Quantum Search (estado atual do codigo)

## Objetivo

Comparar retrieval semantico em dois pipelines no mesmo dataset:

- Classico (`SbertEncoder` + cosseno em `embedding_vector`)
- Quantico-inspirado (`PennyLaneQuantumEncoder` + cosseno em `quantum_vector`)

O sistema tambem inclui:

- autenticacao JWT com refresh token
- chats persistidos (sem LLM; mensagens do assistant sao resumos/payloads de retrieval)
- cadastro de ground truth
- avaliacao batch com metricas de IR

## Arquitetura (aderente ao projeto)

### Camadas

- `core/src/domain`: entidades, enums, excecoes e ports
- `core/src/application`: casos de uso (auth, chats, IR)
- `core/src/infrastructure`: API FastAPI, banco, repositorios, encoders, metricas, seguranca, dataset provider
- `frontend`: SPA React/Vite consumindo rotas compativeis sem prefixo `/api`

### Servicos em runtime

- `core`: FastAPI + Uvicorn
- `frontend`: Vite
- `db`: PostgreSQL com imagem `pgvector/pgvector:pg16`

### Persistencia vetorial

- PostgreSQL + pgvector via `VectorType` e `cosine_distance`

## Fluxo ponta a ponta

### 1) Dataset (Reuters)

- Provider implementado: `core/src/infrastructure/datasets/reuters_provider.py`
- Fonte: `nltk.corpus.reuters` (Reuters-21578)
- O provider tenta `nltk.download("reuters")` automaticamente se o corpus nao estiver instalado
- Sem mini-dataset local interno: se o corpus continuar indisponivel, a API falha com erro de validacao
- Aliases aceitos: `reuters`, `reuters-21578`, `reuters21578`, `nltk-reuters`, etc.
- Configuracao atual do provider no codigo: snapshot completo (`max_docs=None`, `max_queries=None`)

### 2) Indexacao

Caso de uso: `IndexDatasetUseCase`

Passos reais:

1. Busca metadados do dataset no provider
2. Itera documentos do Reuters
3. Gera `embedding_vector` com `SbertEncoder.encode(text)`
4. Gera `quantum_vector` com `PennyLaneQuantumEncoder.encode(text)`
5. Faz upsert em `documents` em lotes de 64
6. Persiste snapshot em `dataset_snapshots` (doc_ids, queries, metadados)

Observacoes:

- `POST /api/index` executa indexacao sincrona
- O frontend atual usa a rota compativel `POST /search/dataset/index`, que dispara job em thread + polling em `/search/dataset/index/status`
- O job assyncrono pode pular reindexacao se snapshot e contagem de docs coincidirem (`already_indexed`)

### 3) Busca

Caso de uso: `SearchUseCase`

Modos suportados:

- `classical`
- `quantum`
- `compare`

Pipeline classico:

1. Encode da query com `SbertEncoder`
2. Busca em `documents.embedding_vector`
3. Score por similaridade cosseno
4. Ordenacao descrescente por score

Pipeline quantico-inspirado:

1. Encode da query com `PennyLaneQuantumEncoder`
2. Busca em `documents.quantum_vector`
3. Score por similaridade cosseno
4. Ordenacao descrescente por score

Modo `compare` retorna tambem:

- `comparison.classical`
- `comparison.quantum`
- `comparison_metrics` com `common_doc_ids` e medias de score

### 4) Chat persistido

Fluxo usado pelo frontend (`frontend/src/pages/Chat.tsx`):

1. Cria conversa (se ainda nao houver uma ativa)
2. Salva mensagem do usuario
3. Garante indexacao do dataset Reuters (com polling)
4. Executa busca comparativa
5. Salva mensagem `assistant` textual resumindo resultados
6. Armazena ultima resposta completa em `localStorage` para renderizar os paineis

Tambem existe persistencia estruturada pelo backend:

- `POST /api/search` com `chat_id` salva um payload JSON de retrieval como mensagem `assistant`

## Avaliacao e gabaritos (estado real)

### Ground truth

Tabela: `ground_truth`

Campos usados:

- `dataset`
- `query_id`
- `query_text`
- `relevant_doc_ids`
- `user_id` (opcional)

### Cadastro de gabaritos

- API canonica: `POST /api/ground-truth`
- API compativel usada pelo frontend: `POST /benchmarks/labels`

Importante sobre `ideal_answer`:

- O frontend envia `ideal_answer`
- A rota compativel atual NAO persiste `ideal_answer`
- Se `relevant_doc_ids` nao forem enviados, o backend infere um ground truth inicial usando busca classica top-5 e salva esses `doc_ids`

### Avaliacao batch

Caso de uso: `EvaluateUseCase`

Fluxo:

1. Le `ground_truth` do dataset
2. Executa busca por `query_text` no(s) pipeline(s)
3. Calcula metricas por query
4. Agrega medias por pipeline

Metricas realmente calculadas hoje:

- `precision_at_k`
- `recall_at_k`
- `ndcg_at_k`
- `spearman`

Campos existentes nas respostas de busca (`metrics`) mas ainda nao implementados como metrica real:

- `accuracy_at_k` -> `null`
- `f1_at_k` -> `null`
- `mrr` -> `null`
- `answer_similarity` -> `null`

## API (resumo de operacao)

### Rotas canonicas (`/api/*`)

- `GET /api/health`
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`
- `POST /api/auth/refresh`
- `POST|GET /api/chats`
- `GET|PATCH|DELETE /api/chats/{chat_id}`
- `POST /api/chats/{chat_id}/messages`
- `POST /api/index`
- `POST /api/search`
- `POST /api/ground-truth`
- `POST /api/evaluate`

### Rotas compativeis (sem `/api`) expostas para o frontend atual

- `/auth/*`
- `/conversations*`
- `/search/dataset/index`
- `/search/dataset/index/status`
- `/search/dataset`
- `/datasets*`
- `/benchmarks/labels*`

Rota descontinuada mantida apenas para compatibilidade de erro:

- `POST /search/file` -> `410 Gone`

## Seguranca

- Senhas com `passlib` (`bcrypt_sha256`/`bcrypt`)
- JWT access + refresh com `python-jose`
- `OAuth2PasswordBearer` no FastAPI
- Chats, indexacao e busca exigem usuario autenticado
- `require_admin_for_indexing` pode exigir admin na indexacao

## Configuracao (variaveis reais do backend)

Arquivo: `core/src/infrastructure/config.py`

### Aplicacao

- `APP_ENV`
- `APP_NAME`
- `CORS_ORIGINS`

### Banco

- `DB_SCHEME`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DATABASE_URL` (override opcional)

### Auth/JWT

- `JWT_SECRET`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_MINUTES`
- `PASSWORD_RESET_EXPIRE_MINUTES`

### Retrieval / encoders

- `EMBEDDING_DIM` (default `384`)
- `QUANTUM_DIM` (default `16`)
- `QUANTUM_N_QUBITS` (default `4`)
- `CLASSICAL_MODEL_NAME`
- `SEED`

### Controle de acesso

- `REQUIRE_AUTH_FOR_INDEXING`
- `REQUIRE_ADMIN_FOR_INDEXING`

### Frontend

- `VITE_API_BASE_URL` (consumido em `frontend/src/lib/api.ts`)

## Banco de dados (resumo)

Tabelas principais:

- `users`
- `password_resets`
- `chats`
- `chat_messages`
- `documents`
- `ground_truth`
- `dataset_snapshots`

Detalhes em `DB_SCHEMA.md`.

## Limitacoes atuais

- `ideal_answer` nao participa da avaliacao no backend atual
- `answer_similarity`, `mrr`, `f1_at_k`, `accuracy_at_k` ainda retornam `null`
- Custo de indexacao pode ser alto no Reuters completo (sBERT local + corpus inteiro)
- Pipeline quantico e quantico-inspirado em simulacao (PennyLane), nao hardware quantico real

## Referencias de implementacao

- Busca e avaliacao: `core/src/application/ir_use_cases.py`
- Metricas: `core/src/infrastructure/metrics/sklearn_metrics.py`
- Encoders: `core/src/infrastructure/encoders/classical.py`, `core/src/infrastructure/encoders/quantum.py`
- Rotas: `core/src/infrastructure/api/routers/api_router.py`
- Frontend API client: `frontend/src/lib/api.ts`
