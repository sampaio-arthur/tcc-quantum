# Documentacao da API (TCC Quantum Search)

Esta documentacao descreve todos os endpoints, formatos de request/response e instrucoes de uso para integrar o frontend.

## Visao Geral
- Base URL (local): `http://localhost:8000`
- Servidor: FastAPI
- Autenticacao: Bearer JWT
- CORS: liberado para todas as origens

## Como rodar o backend
1. Copie `.env.example` para `.env` e ajuste se necessario.
1. Suba os servicos:
```
docker compose build
docker compose up -d
```
1. API disponivel em `http://localhost:8000`.

## Autenticacao
Fluxo:
1. `POST /auth/register` para criar usuario.
1. `POST /auth/login` para obter `access_token`.
1. Usar o token no header:
```
Authorization: Bearer <access_token>
```

O token expira em `ACCESS_TOKEN_EXPIRE_MINUTES` (padrao 1440 minutos).

## Endpoints

### Health Check
**GET** `/health`
- Auth: nao
- Response:
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
- Response 201 (JSON):
```json
{
  "id": 1,
  "email": "user@email.com",
  "created_at": "2026-02-05T12:00:00Z"
}
```
- Erros:
  - 400: `Email already registered`

#### Login
**POST** `/auth/login`
- Auth: nao
- Content-Type: `application/x-www-form-urlencoded`
- Body (form):
```
username=<email>&password=<senha>
```
- Response 200 (JSON):
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
- Response 200 (JSON):
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
  ]
}
```
- Response 200 (JSON):
```json
{
  "query": "texto da pergunta",
  "results": [
    {
      "doc_id": "doc-1",
      "text": "documento 1",
      "score": 0.87
    }
  ]
}
```

#### Busca por arquivo
**POST** `/search/file`
- Auth: nao
- Content-Type: `multipart/form-data`
- Body (form-data):
  - `query` (string)
  - `file` (UploadFile: PDF ou TXT)
- Response 200 (JSON):
```json
{
  "query": "texto da pergunta",
  "results": [
    {
      "doc_id": "doc-1",
      "text": "trecho do documento",
      "score": 0.91
    }
  ]
}
```

### Conversas (chat)
Todas as rotas abaixo exigem Bearer JWT.

#### Criar conversa
**POST** `/conversations`
- Auth: Bearer JWT
- Body (JSON):
```json
{
  "title": "Minha conversa"
}
```
- Response 201 (JSON):
```json
{
  "id": 10,
  "title": "Minha conversa",
  "created_at": "2026-02-05T12:00:00Z"
}
```

#### Listar conversas do usuario
**GET** `/conversations`
- Auth: Bearer JWT
- Response 200 (JSON):
```json
[
  {
    "id": 10,
    "title": "Minha conversa",
    "created_at": "2026-02-05T12:00:00Z"
  }
]
```

#### Detalhar conversa
**GET** `/conversations/{conversation_id}`
- Auth: Bearer JWT
- Response 200 (JSON):
```json
{
  "id": 10,
  "title": "Minha conversa",
  "created_at": "2026-02-05T12:00:00Z",
  "messages": [
    {
      "id": 100,
      "role": "user",
      "content": "Oi",
      "created_at": "2026-02-05T12:05:00Z"
    }
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
{
  "role": "user",
  "content": "Minha mensagem"
}
```
- Roles aceitas: `user`, `assistant`, `system`
- Response 201 (JSON):
```json
{
  "id": 101,
  "role": "user",
  "content": "Minha mensagem",
  "created_at": "2026-02-05T12:06:00Z"
}
```
- Erros:
  - 400: `Invalid role`
  - 404: `Conversation not found`

## Observacoes para o Frontend
- Prefixo base: `http://localhost:8000`
- Endpoints protegidos: `/auth/me`, `/conversations*`
- Login usa `application/x-www-form-urlencoded` (nao JSON)
- Upload de arquivo deve ser `multipart/form-data`

