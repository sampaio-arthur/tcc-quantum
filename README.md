# TCC - Comparative Semantic Retrieval (Classical vs Quantum-Inspired)

Backend FastAPI com Clean Architecture para comparar retrieval semântico entre dois pipelines:

- Clássico (`sBERT`) -> `documents.embedding_vector`
- Quântico-inspirado (`PennyLane`) -> `documents.quantum_vector`

O projeto também inclui autenticação JWT, chats salvos (estilo GPT, sem LLM) e avaliação por métricas de IR.

## Status

- Backend `core/` implementado do zero (estrutura em camadas + persistência + API)
- Rotas compatíveis com o front legado mantidas
- Rotas finais `/api/*` documentadas

## Árvore do Projeto

```text
.
├── core/
│   ├── alembic/
│   ├── src/
│   │   ├── application/
│   │   ├── domain/
│   │   └── infrastructure/
│   │       ├── api/
│   │       ├── datasets/
│   │       ├── db/
│   │       ├── encoders/
│   │       ├── email/
│   │       ├── metrics/
│   │       ├── repositories/
│   │       └── security/
│   ├── tests/
│   ├── Dockerfile
│   ├── pytest.ini
│   └── requirements.txt
├── frontend/
├── API.md
├── ARCHITECTURE.md
├── METHODS.md
├── DB_SCHEMA.md
├── EVALUATION.md
├── DEPENDENCIES.md
├── CHANGELOG.md
└── ROUTES_COMPAT.md
```

## Execução

### Docker

```bash
docker compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- PostgreSQL/pgvector: `localhost:5432`

### Local (backend)

```bash
cd core
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn infrastructure.api.fastapi_app:app --host 0.0.0.0 --port 8000 --app-dir src
```

## Reuters (reprodutível)

- Provider: `nltk.corpus.reuters`
- Download automático tentado pelo backend (`nltk.download("reuters")`)
- Fallback pequeno local incluído para dev/teste se o corpus não estiver disponível

## Fluxo principal (mínimo)

1. `POST /auth/register` (compat) ou `POST /api/auth/signup`
2. `POST /auth/login` (compat) ou `POST /api/auth/login`
3. `POST /api/index` para indexar `reuters`
4. `POST /api/chats` para criar conversa
5. `POST /api/search` com `chat_id` para persistir mensagem do assistant (resultado estruturado)
6. `POST /api/ground-truth`
7. `POST /api/evaluate`

## Frontend e CORS

O front legado usa `VITE_API_BASE_URL=http://localhost:8000` e chama rotas sem prefixo `/api`.

Este backend expõe:

- Rotas finais: `/api/*`
- Rotas compatíveis: `/auth/*`, `/conversations`, `/search/*`, `/datasets`, `/benchmarks/labels`

Ver `ROUTES_COMPAT.md`.

## Testes

Teste de fluxo: `core/tests/test_api_flow.py`

```bash
cd core
pytest -q
```

Observação: no ambiente desta sessão, faltaram algumas dependências Python para executar a suíte completa (`pydantic_settings`, etc.).

## Documentação

- `ARCHITECTURE.md`
- `API.md`
- `METHODS.md`
- `DB_SCHEMA.md`
- `EVALUATION.md`
- `DEPENDENCIES.md`
- `ROUTES_COMPAT.md`
- `CHANGELOG.md`
