# API Documentation - Quantum Search (TCC)

## Visao geral
- Base URL (local): `http://localhost:8000`
- Backend: FastAPI
- Banco: PostgreSQL + pgvector
- Autenticacao: Bearer JWT (rotas de conversas e mensagens)
- CORS: liberado para todas as origens

## Setup rapido
1. Copie `.env.example` para `.env` e preencha valores.
2. Suba servicos:
```bash
docker compose build
docker compose up -d
```
3. API disponivel em `http://localhost:8000`.

## Autenticacao
Fluxo:
1. `POST /auth/register`
2. `POST /auth/login`
3. Enviar header:
```http
Authorization: Bearer <access_token>
```

## Parametros comuns de busca
- `mode`: `classical`, `quantum`, `compare`
- `top_k`: quantidade final de resultados (padrao 5)
- `candidate_k`: candidatos para reranking (padrao 20)

## Persistencia de busca
Cada busca grava rastros no banco:
- `search_runs`: metadados da execucao
- `search_vector_records`: embeddings e, no modo quantico, estados preparados

Tipos de `kind` esperados:
- `query_embedding`
- `document_embedding`
- `quantum_query_state`
- `quantum_doc_state`

## Endpoints

### Health
**GET** `/health`
- Auth: nao
- 200:
```json
{ "status": "ok" }
```

### Auth
#### POST `/auth/register`
- Auth: nao
- Body:
```json
{ "email": "user@email.com", "password": "senha" }
```
- 201:
```json
{ "id": 1, "email": "user@email.com", "created_at": "2026-02-05T12:00:00Z" }
```

#### POST `/auth/login`
- Auth: nao
- Form URL encoded:
```text
username=<email>&password=<senha>
```
- 200:
```json
{ "access_token": "<jwt>", "token_type": "bearer" }
```

#### GET `/auth/me`
- Auth: Bearer
- 200:
```json
{ "id": 1, "email": "user@email.com", "created_at": "2026-02-05T12:00:00Z" }
```

### Search
#### POST `/search`
- Auth: nao
- Body:
```json
{
  "query": "texto da pergunta",
  "documents": ["doc 1", "doc 2"],
  "mode": "classical",
  "top_k": 5,
  "candidate_k": 20
}
```
- 200: retorna `query`, `mode`, `results`, `answer`, `metrics`, `comparison` (quando `mode=compare`).

#### POST `/search/file`
- Auth: nao
- Multipart form-data:
  - `query` (opcional; default "Resumo do documento")
  - `file` (PDF/TXT, obrigatorio)
  - `mode` (opcional)
  - `top_k` (opcional)
  - `candidate_k` (opcional)
- 200: mesmo formato de `/search`.
- Erros comuns:
  - 400 `Arquivo nao enviado`
  - 400 `Arquivo vazio`
  - 413 `Arquivo excede o limite de tamanho`

#### POST `/search/dataset`
- Auth: nao
- Body:
```json
{
  "dataset_id": "mini-rag",
  "query_id": "q1",
  "mode": "compare",
  "top_k": 5,
  "candidate_k": 20
}
```
- 200: inclui metricas com rotulos quando disponiveis.

### Datasets
#### GET `/datasets`
- Auth: nao
- Lista datasets disponiveis.

#### GET `/datasets/{dataset_id}`
- Auth: nao
- Detalha dataset e queries.

### Conversas (Bearer JWT)
#### POST `/conversations`
Cria conversa.

#### GET `/conversations`
Lista conversas do usuario.

#### GET `/conversations/{conversation_id}`
Detalha conversa com mensagens.

#### POST `/conversations/{conversation_id}/messages`
Adiciona mensagem (`role`: `user`, `assistant`, `system`).

#### DELETE `/conversations/{conversation_id}`
Remove conversa.

## Observacoes operacionais
- `.env.example` contem somente nomes de variaveis.
- Segredos e valores reais devem existir apenas em `.env`.
- Embeddings sao gerados via API externa e persistidos para rastreabilidade.
