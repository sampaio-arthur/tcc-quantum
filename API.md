# API

## Base URL

- Backend: `http://localhost:8000`
- Prefixo oficial: `/api`
- Compatibilidade com front legado: rotas sem `/api` (ver `ROUTES_COMPAT.md`)

## Auth

### `POST /api/auth/signup`

```json
{ "email": "user@example.com", "password": "12345678", "name": "User" }
```

### `POST /api/auth/login` (OAuth2 form)

`application/x-www-form-urlencoded`

- `username`
- `password`

Resposta:

```json
{ "access_token": "...", "token_type": "bearer", "refresh_token": "..." }
```

### `GET /api/auth/me`

`Authorization: Bearer <token>`

### `POST /api/auth/forgot-password`

Mensagem neutra (anti enumeração). Em dev, token é logado.

### `POST /api/auth/reset-password`

```json
{ "token": "reset_token", "new_password": "newStrongPass123" }
```

### `POST /api/auth/refresh`

```json
{ "refresh_token": "..." }
```

## Chats

### `POST /api/chats`

```json
{ "title": "Meu chat" }
```

### `GET /api/chats?page=1&page_size=20`

### `GET /api/chats/{chat_id}`

Retorna chat + mensagens.

### `POST /api/chats/{chat_id}/messages`

```json
{ "role": "user", "content": "Pergunta" }
```

Roles: `user`, `assistant`, `system`.

### `PATCH /api/chats/{chat_id}`

```json
{ "title": "Novo título" }
```

### `DELETE /api/chats/{chat_id}`

Soft delete.

## Core IR

### `GET /api/health`

### `POST /api/index`

```json
{ "dataset_id": "reuters", "force_reindex": false }
```

Indexa com:

- `encode_embedding(text)` -> `embedding_vector`
- `encode_quantum(text)` -> `quantum_vector`

### `POST /api/search`

```json
{
  "dataset_id": "reuters",
  "query": "trade tariffs imports exports",
  "mode": "compare",
  "top_k": 5,
  "chat_id": 1
}
```

`mode`: `classical`, `quantum`, `compare`

Se `chat_id` for enviado, o backend salva uma mensagem `assistant` com payload estruturado do retrieval.

### `POST /api/ground-truth`

```json
{
  "dataset_id": "reuters",
  "query_id": "q1",
  "query_text": "trade tariffs imports exports",
  "relevant_doc_ids": ["docA", "docB"]
}
```

### `POST /api/evaluate`

```json
{ "dataset_id": "reuters", "pipeline": "compare", "k": 5 }
```

Métricas:

- `precision@k`
- `recall@k`
- `ndcg@k`
- `spearman`

## Compatibilidade com Front (rotas legado)

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET|POST /conversations`
- `GET|PATCH|DELETE /conversations/{id}`
- `POST /conversations/{id}/messages`
- `POST /search/file`
- `POST /search/dataset/index`
- `POST /search/dataset`
- `GET /datasets`
- `GET /datasets/{dataset_id}`
- `GET|POST|DELETE /benchmarks/labels...`

## Exemplos `curl`

### Signup + Login

```bash
curl -X POST http://localhost:8000/api/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"user@example.com","password":"12345678"}'

curl -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user@example.com&password=12345678'
```

### Index + Search

```bash
curl -X POST http://localhost:8000/api/index \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"dataset_id":"reuters"}'

curl -X POST http://localhost:8000/api/search \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"dataset_id":"reuters","query":"oil prices opec","mode":"compare","top_k":5}'
```
