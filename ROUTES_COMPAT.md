# ROUTES_COMPAT

Mapeamento das rotas encontradas no front (`frontend/src/lib/api.ts`) para o backend final.

## Base URL do front atual

- `VITE_API_BASE_URL` (default `http://localhost:8000`)
- O front **não** usa prefixo `/api`

## Mapeamento (Front -> Backend final)

- `POST /auth/register` -> `POST /api/auth/signup` (alias compatível mantido)
- `POST /auth/login` -> `POST /api/auth/login` (alias compatível mantido)
- `GET /auth/me` -> `GET /api/auth/me` (alias compatível mantido)

- `GET /conversations` -> `GET /api/chats` (alias compatível mantido)
- `POST /conversations` -> `POST /api/chats` (alias compatível mantido)
- `GET /conversations/{id}` -> `GET /api/chats/{chat_id}` (alias compatível mantido)
- `PATCH /conversations/{id}` -> `PATCH /api/chats/{chat_id}` (alias compatível mantido)
- `DELETE /conversations/{id}` -> `DELETE /api/chats/{chat_id}` (alias compatível mantido)
- `POST /conversations/{id}/messages` -> `POST /api/chats/{chat_id}/messages` (alias compatível mantido)

- `POST /search/file` -> removido no produto (endpoint compatível responde `410 Gone`)
- `POST /search/dataset/index` -> `POST /api/index` (alias compatível mantido)
- `POST /search/dataset` -> `POST /api/search` (alias compatível mantido)

- `GET /datasets` -> provider de datasets (compatível mantido; sem `/api` na especificação alvo)
- `GET /datasets/{dataset_id}` -> detalhes do dataset (compatível mantido)

- `GET /benchmarks/labels` -> leitura de `ground_truth` (alias compatível mantido)
- `POST /benchmarks/labels` -> upsert em `ground_truth` (alias compatível mantido)
- `DELETE /benchmarks/labels/{dataset_id}/{benchmark_id}` -> delete em `ground_truth` (alias compatível mantido)

## Decisão de compatibilidade

Preferência adotada:

- manter rotas finais `/api/*` como canônicas para documentação e evolução
- expor aliases compatíveis para o front atual sem exigir mudanças no frontend

## Exemplos (compatíveis)

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'username=user@example.com&password=12345678'
```

### Criar conversa

```bash
curl -X POST http://localhost:8000/conversations \
  -H \"Authorization: Bearer $TOKEN\" \
  -H 'Content-Type: application/json' \
  -d '{\"title\":\"Teste\"}'
```

### Busca em dataset (modo compare)

```bash
curl -X POST http://localhost:8000/search/dataset \
  -H \"Authorization: Bearer $TOKEN\" \
  -H 'Content-Type: application/json' \
  -d '{\"dataset_id\":\"reuters\",\"query\":\"oil prices opec\",\"mode\":\"compare\",\"top_k\":5}'
```

## Formato de resposta (exemplo `/search/dataset`)

```json
{
  "query": "oil prices opec",
  "mode": "compare",
  "results": [{ "doc_id": "id", "text": "...", "score": 0.91 }],
  "comparison": {
    "classical": { "results": [{ "doc_id": "id", "text": "...", "score": 0.91 }] },
    "quantum": { "results": [{ "doc_id": "id2", "text": "...", "score": 0.77 }] }
  }
}
```
