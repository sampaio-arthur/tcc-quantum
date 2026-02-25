# TCC - Quantum Comparative Retrieval (Classical vs Quantum-Inspired)

Aplicacao full-stack para comparar retrieval semantico em dois pipelines sobre o dataset Reuters:

- Classico (`sBERT`) em `documents.embedding_vector`
- Quantico-inspirado (`PennyLane`) em `documents.quantum_vector`

Inclui:

- backend FastAPI (Clean Architecture)
- frontend React + Vite
- PostgreSQL + pgvector
- autenticacao JWT
- chats persistidos
- cadastro de ground truth e avaliacao batch (precision/recall/NDCG/Spearman)

## Como o `.env.example` deve ser usado

O arquivo `.env.example` e a base das variaveis da aplicacao.

Use assim:

- copie `.env.example` para `.env`
- preencha os valores
- use esse `.env` no `docker compose` e/ou no run local

Exemplos:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Observacao:

- o `docker-compose.yml` le o `.env` na raiz do repositorio
- se voce rodar o backend localmente a partir da raiz (com `--app-dir core/src`), o mesmo `.env` da raiz funciona como base para o backend

## Variaveis minimas recomendadas (`.env`)

Exemplo funcional para desenvolvimento local/Docker:

```env
APP_ENV=dev
APP_NAME=quantum-semantic-search
CORS_ORIGINS=["http://localhost:5173","http://localhost:8080"]

DATABASE_URL=postgresql+psycopg://tcc:tcc@db:5432/tcc

JWT_SECRET=troque-esta-chave
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_MINUTES=10080

CLASSICAL_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIM=384
QUANTUM_N_QUBITS=4
QUANTUM_DIM=16
SEED=42

PASSWORD_RESET_EXPIRE_MINUTES=30

REQUIRE_AUTH_FOR_INDEXING=true
REQUIRE_ADMIN_FOR_INDEXING=false

VITE_API_BASE_URL=http://localhost:8000
```

Se for rodar o backend fora do Docker e usar Postgres local (host da maquina), ajuste `DATABASE_URL`, por exemplo:

```env
DATABASE_URL=postgresql+psycopg://tcc:tcc@localhost:5432/tcc
```

Para testes rapidos locais, tambem pode usar SQLite:

```env
DATABASE_URL=sqlite:///./app.db
```

## Pre-requisitos

### Opcao A (recomendada): Docker

- Docker
- Docker Compose

### Opcao B (local)

- Python 3.11+ (recomendado)
- Node.js 20+
- npm
- PostgreSQL 16 + extensao `pgvector` (ou SQLite para teste local)
- acesso a internet para baixar:
  - corpus Reuters do NLTK
  - modelo `sentence-transformers`

## Executando com Docker (recomendado)

1. Criar e configurar `.env` a partir de `.env.example`
2. Subir os servicos

```bash
docker compose up --build
```

Servicos:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- PostgreSQL/pgvector: `localhost:5432`

### Fluxo inicial para validar que tudo funciona

1. Acesse `http://localhost:5173`
2. Crie uma conta
3. Entre
4. Abra o chat e envie uma consulta
5. O frontend vai:
   - criar conversa
   - garantir indexacao do dataset Reuters
   - executar busca comparativa classico x quantico
   - exibir paineis com latencia e scores

Observacoes:

- A primeira indexacao pode demorar (download do corpus Reuters + modelo sBERT + indexacao completa)
- O job de indexacao compativel usa polling em `/search/dataset/index/status`

## Executando localmente (sem Docker)

### 1) Preparar `.env`

Crie `.env` na raiz com base no `.env.example` e ajuste `DATABASE_URL` (Postgres local ou SQLite).

### 2) Backend (`core`)

A partir da raiz do repositorio:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r core/requirements.txt
uvicorn infrastructure.api.fastapi_app:app --host 0.0.0.0 --port 8000 --app-dir core/src
```

PowerShell (Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r core\requirements.txt
uvicorn infrastructure.api.fastapi_app:app --host 0.0.0.0 --port 8000 --app-dir core/src
```

### 3) Frontend (`frontend`)

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

Observacao:

- No dev local do frontend, `vite.config.ts` usa porta `8080`
- Ajuste `CORS_ORIGINS` e `VITE_API_BASE_URL` no `.env` se necessario

## Reuters (dataset usado)

- Provider: `nltk.corpus.reuters`
- O backend tenta `nltk.download("reuters")` automaticamente
- Se o download falhar (sem internet/permissao), a indexacao e listagem do dataset vao falhar
- O backend persiste snapshot do dataset em `dataset_snapshots` durante a indexacao (doc_ids + queries + metadados) para rastreabilidade

Referencias:

- `https://www.nltk.org/howto/corpus.html`
- `https://www.nltk.org/book/ch02.html`
- `http://kdd.ics.uci.edu/databases/reuters21578/reuters21578.html`

## Endpoints principais

### Canonicos (`/api/*`)

- `GET /api/health`
- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`
- `POST /api/index`
- `POST /api/search`
- `POST /api/ground-truth`
- `POST /api/evaluate`

### Compativeis com o frontend atual (sem `/api`)

- `/auth/*`
- `/conversations*`
- `/search/dataset/index`
- `/search/dataset/index/status`
- `/search/dataset`
- `/datasets*`
- `/benchmarks/labels*`

## Testes

### Backend

```bash
pytest -q core/tests/test_api_flow.py
```

Ou:

```bash
cd core
pytest -q
```

### Frontend

```bash
cd frontend
npm test
```

## Troubleshooting rapido

### 1) Erro de Reuters indisponivel

Sintoma:

- falha ao listar/indexar dataset `reuters`

Causas comuns:

- sem internet
- download do corpus bloqueado
- ambiente sem permissao de escrita para cache do NLTK

### 2) Erro ao carregar modelo sBERT

Sintoma:

- falha na indexacao com erro do `sentence-transformers`

Causas comuns:

- sem internet no primeiro download
- dependencias Python incompletas
- cache corrompido

### 3) Erro de CORS no frontend

Verifique:

- `CORS_ORIGINS` no `.env`
- `VITE_API_BASE_URL` no `.env`
- porta real do frontend (`5173` no Docker, `8080` no dev local por padrao)

### 4) Erro de dimensao de vetores na inicializacao

O backend valida ao subir:

- `EMBEDDING_DIM == 384`
- `QUANTUM_DIM == 2 ** QUANTUM_N_QUBITS`

Isso precisa bater com o schema atual da tabela `documents`.

## Estrutura resumida

```text
.
+-- core/
|   +-- alembic/
|   +-- src/
|   |   +-- application/
|   |   +-- domain/
|   |   +-- infrastructure/
|   +-- tests/
+-- frontend/
+-- docker-compose.yml
+-- .env.example
+-- *.md
```

## Documentacao adicional

- `DOCUMENTACAO.md` (visao tecnica aderente ao codigo)
- `FORMULAS_E_CALCULOS.md` (formulas/metricas implementadas)
- `API.md`
- `ARCHITECTURE.md`
- `METHODS.md`
- `DB_SCHEMA.md`
- `EVALUATION.md`
- `DEPENDENCIES.md`
- `ROUTES_COMPAT.md`
- `CHANGELOG.md`

