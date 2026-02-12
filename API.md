# API Documentation - Quantum Search (TCC)

Esta documentacao descreve todos os endpoints, formatos de request/response e o passo a passo para uso.

## Visao geral
- Base URL (local): `http://localhost:8000`
- Servidor: FastAPI
- Autenticacao: Bearer JWT (somente rotas de conversas e mensagens)
- CORS: liberado para todas as origens

## Como rodar o backend
1. Copie `.env.example` para `.env` e ajuste se necessario.
2. Suba os servicos:
```
docker compose build
docker compose up -d
```
3. API disponivel em `http://localhost:8000`.

## Passo a passo (API)
1. Crie um usuario com `POST /auth/register`.
2. Faca login com `POST /auth/login` e guarde o `access_token`.
3. Use `Authorization: Bearer <access_token>` nas rotas de conversas.
4. Para buscar:
   - Use `POST /search/file` para PDF/TXT (com `mode=compare` para comparar).
   - Use `POST /search` para enviar textos em JSON.
   - Use `POST /search/dataset` para consultas em datasets publicos.

## Autenticacao
Fluxo:
1. `POST /auth/register` para criar usuario.
2. `POST /auth/login` para obter `access_token`.
3. Usar o token no header:
```
Authorization: Bearer <access_token>
```

O token expira em `ACCESS_TOKEN_EXPIRE_MINUTES` (padrao 1440 minutos).

## Parametros comuns de busca
- `mode`: `classical`, `quantum`, `compare`
- `top_k`: numero de resultados finais (padrao 5)
- `candidate_k`: numero de candidatos para reranking (padrao 20)

## Endpoints

### Health Check
**GET** `/health`
- Auth: nao
- Response 200:
```json
{ "status": "ok" }
```

### Auth
#### Registrar usuario
**POST** `/auth/register`
- Auth: nao
- Body (JSON):
```json
{
  "email": "user@email.com",
  "password": "senha"
}
```
- Response 201:
```json
{
  "id": 1,
  "email": "user@email.com",
  "created_at": "2026-02-05T12:00:00Z"
}
```
- Erros:
  - 400: `Email already registered`
  - 400: `Password too long (max 72 bytes)`

#### Login
**POST** `/auth/login`
- Auth: nao
- Content-Type: `application/x-www-form-urlencoded`
- Body (form):
```
username=<email>&password=<senha>
```
- Response 200:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```
- Erros:
  - 401: `Invalid credentials`

#### Usuario logado
**GET** `/auth/me`
- Auth: Bearer JWT
- Response 200:
```json
{
  "id": 1,
  "email": "user@email.com",
  "created_at": "2026-02-05T12:00:00Z"
}
```
- Erros:
  - 401: `Could not validate credentials`

### Search
#### Busca por texto
**POST** `/search`
- Auth: nao
- Body (JSON):
```json
{
  "query": "texto da pergunta",
  "documents": [
    "documento 1",
    "documento 2"
  ],
  "mode": "classical",
  "top_k": 5,
  "candidate_k": 20
}
```
- Response 200:
```json
{
  "query": "texto da pergunta",
  "mode": "classical",
  "results": [
    { "doc_id": "doc-1", "text": "documento 1", "score": 0.87 }
  ],
  "metrics": {
    "recall_at_k": null,
    "mrr": null,
    "ndcg_at_k": null,
    "latency_ms": 12.4,
    "k": 5,
    "candidate_k": 20,
    "has_labels": false
  }
}
```

#### Busca por arquivo
**POST** `/search/file`
- Auth: nao
- Content-Type: `multipart/form-data`
- Body (form-data):
  - `query` (string, opcional; se vazio, usa "Resumo do documento")
  - `file` (UploadFile: PDF ou TXT, obrigatorio)
  - `mode` (opcional; padrao `classical`)
  - `top_k` (opcional; padrao 5)
  - `candidate_k` (opcional; padrao 20)
- Response 200:
```json
{
  "query": "texto da pergunta",
  "mode": "compare",
  "results": [
    { "doc_id": "doc-1", "text": "trecho do documento", "score": 0.91 }
  ],
  "comparison": {
    "classical": {
      "results": [{ "doc_id": "doc-1", "text": "trecho", "score": 0.91 }],
      "metrics": { "latency_ms": 10.2, "k": 5, "candidate_k": 20, "has_labels": false }
    },
    "quantum": {
      "results": [{ "doc_id": "doc-1", "text": "trecho", "score": 0.88 }],
      "metrics": { "latency_ms": 18.6, "k": 5, "candidate_k": 20, "has_labels": false }
    }
  }
}
```
- Erros:
  - 400: `Arquivo nao enviado`

#### Busca em dataset publico
**POST** `/search/dataset`
- Auth: nao
- Body (JSON):
```json
{
  "dataset_id": "mini-rag",
  "query_id": "q1",
  "mode": "compare",
  "top_k": 5,
  "candidate_k": 20
}
```
- Response 200 inclui `metrics` com rotulos de relevancia quando disponiveis.
- Erros:
  - 404: `Dataset nao encontrado`
  - 404: `Query nao encontrada`

### Datasets
#### Listar datasets
**GET** `/datasets`
- Auth: nao
- Response 200:
```json
[
  {
    "dataset_id": "mini-rag",
    "name": "Mini RAG/Quantum",
    "description": "Conjunto reduzido para avaliacao",
    "document_count": 5,
    "query_count": 5
  }
]
```

#### Detalhar dataset
**GET** `/datasets/{dataset_id}`
- Auth: nao
- Response 200:
```json
{
  "dataset_id": "mini-rag",
  "name": "Mini RAG/Quantum",
  "description": "Conjunto reduzido para avaliacao",
  "queries": [
    { "query_id": "q1", "query": "Como o RAG usa busca semantica?", "relevant_count": 2 }
  ]
}
```
- Erros:
  - 404: `Dataset nao encontrado`

### Conversas (chat)
Todas as rotas abaixo exigem Bearer JWT.

#### Criar conversa
**POST** `/conversations`
- Auth: Bearer JWT
- Body (JSON):
```json
{ "title": "Minha conversa" }
```
- Response 201:
```json
{ "id": 10, "title": "Minha conversa", "created_at": "2026-02-05T12:00:00Z" }
```

#### Listar conversas do usuario
**GET** `/conversations`
- Auth: Bearer JWT
- Response 200:
```json
[
  { "id": 10, "title": "Minha conversa", "created_at": "2026-02-05T12:00:00Z" }
]
```

#### Detalhar conversa
**GET** `/conversations/{conversation_id}`
- Auth: Bearer JWT
- Response 200:
```json
{
  "id": 10,
  "title": "Minha conversa",
  "created_at": "2026-02-05T12:00:00Z",
  "messages": [
    { "id": 100, "role": "user", "content": "Oi", "created_at": "2026-02-05T12:05:00Z" }
  ]
}
```
- Erros:
  - 404: `Conversation not found`

#### Adicionar mensagem
**POST** `/conversations/{conversation_id}/messages`
- Auth: Bearer JWT
- Body (JSON):
```json
{ "role": "user", "content": "Oi" }
```
- Roles permitidos: `user`, `assistant`, `system`
- Response 201:
```json
{ "id": 101, "role": "user", "content": "Oi", "created_at": "2026-02-05T12:06:00Z" }
```
- Erros:
  - 400: `Invalid role`
  - 404: `Conversation not found`

#### Remover conversa
**DELETE** `/conversations/{conversation_id}`
- Auth: Bearer JWT
- Response 204 (sem corpo)
- Erros:
  - 404: `Conversation not found`