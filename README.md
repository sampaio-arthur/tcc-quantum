# TCC - Quantum Comparative Retrieval (Classical vs Quantum-Inspired)

Aplicacao full-stack para comparar busca semantica em dois tipos de vetorizacao sobre datasets BEIR:

- Busca semantica classica por embeddings (`sBERT`) em `documents.embedding_vector`
- Busca semantica por vetorizacao quantica simulada / quantico-inspirada (`PennyLane`) em `documents.quantum_vector`

## Objetivo do projeto

Implementar e comparar dois fluxos de busca semantica sobre o mesmo dataset e com o mesmo criterio de ranking (similaridade cosseno), mudando a representacao vetorial:

- Pipeline classico: texto -> embedding denso real via `sentence-transformers` (`sBERT`)
- Pipeline quantico-inspirado: texto -> vetor real deterministico derivado de simulacao quantica no `PennyLane` (probabilidades do circuito), sem usar embedding sBERT

Objetivo da comparacao:

- analisar diferencas de retrieval entre representacao por embeddings e representacao quantica-inspirada
- comparar proxies de custo (latencia)
- permitir avaliacao batch com ground truth (precision/recall/NDCG/Spearman)

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
   - garantir indexacao do dataset `beir/trec-covid`
   - executar busca comparativa classico x quantico-inspirado
   - exibir paineis com latencia e scores

Observacoes:

- A primeira indexacao pode demorar (modelo sBERT + indexacao completa do corpus BEIR local)
- O job de indexacao compativel usa polling em `/search/dataset/index/status`

## Dataset (BEIR)

Este projeto utiliza datasets do benchmark BEIR para avaliacao de busca semantica.

Os datasets NAO sao versionados no repositorio devido ao tamanho.

Exemplo usado:

- TREC-COVID (BEIR)

Fonte oficial:

- `https://github.com/beir-cellar/beir`
- `https://huggingface.co/collections/BeIR/beir-datasets-64e5c66c4a7c11a7c1f59f3e`

Estrutura esperada no projeto:

```text
core/data/beir/trec-covid/
├─ corpus.jsonl
├─ queries.jsonl
└─ qrels/test.tsv
```

O backend le os arquivos localmente (offline), sem download automatico.

Apos colocar os arquivos no local correto, o backend pode ser iniciado normalmente.

## Documentacao adicional

- `DOCUMENTACAO.md` (visao tecnica aderente ao codigo)
- `ARCHITECTURE.md`
- `METHODS.md`
- `DB_SCHEMA.md`
- `DEPENDENCIES.md`

## Duvidas

- email: `arthurbarrasampaio@gmail.com`

