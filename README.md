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

## Variaveis minimas recomendadas (`.env`)

Exemplo funcional para desenvolvimento local/Docker:

```env
APP_ENV=dev
APP_NAME=quantum-semantic-search
CORS_ORIGINS=["http://localhost:5173","http://localhost:8080"]

DB_SCHEME=postgresql+psycopg
DB_HOST=db
DB_PORT=5432
DB_NAME=tcc
DB_USER=tcc
DB_PASSWORD=tcc

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

## Pre-requisitos

### Opcao A (recomendada): Docker

- Docker
- Docker Compose

## Executando com Docker 

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

## Reuters (dataset usado)

- Provider: `nltk.corpus.reuters`
- O backend tenta `nltk.download("reuters")` automaticamente
- Se o download falhar (sem internet/permissao), a indexacao e listagem do dataset vao falhar
- O backend persiste snapshot do dataset em `dataset_snapshots` durante a indexacao (doc_ids + queries + metadados) para rastreabilidade

Referencias:

- `https://www.nltk.org/howto/corpus.html`
- `https://www.nltk.org/book/ch02.html`
- `http://kdd.ics.uci.edu/databases/reuters21578/reuters21578.html`

## Documentacao adicional

- `DOCUMENTACAO.md` (visao tecnica aderente ao codigo)
- `ARCHITECTURE.md`
- `METHODS.md`
- `DB_SCHEMA.md`
- `DEPENDENCIES.md`

## Duvidas

- email: `arthurbarrasampaio@gmail.com`

