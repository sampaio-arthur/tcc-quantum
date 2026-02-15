# Quantum Search (TCC)

Plataforma academica para comparar busca semantica classica com abordagem quantico-inspirada (swap test com PennyLane), aplicada a um fluxo RAG simples.

## Resumo
- Upload de PDF/TXT ou uso de dataset publico.
- Embeddings gerados por API externa (Gemini), sem modelo local.
- Comparacao de ranking: classico (cosine) vs quantico-inspirado.
- Persistencia de historico (auth/chat) e de rastros de busca (embeddings + estados quanticos) em PostgreSQL com pgvector.

## Pipeline atual
1. Ingestao: extrai texto de PDF/TXT e divide em chunks.
2. Embeddings: gera vetores por API Gemini (`EMBEDDER_PROVIDER=gemini`).
3. Ranking classico: cosine similarity.
4. Ranking quantico: reranking (swap test) sobre candidatos prefiltrados.
5. Modo `compare`: executa classico e quantico com o mesmo conjunto de embeddings para comparacao fiel.
6. Persistencia de busca: salva run, embeddings e rastros quanticos no banco.

## Persistencia (PostgreSQL + pgvector)
Tabelas principais:
- `users`, `conversations`, `messages`
- `search_runs`
- `search_vector_records`

Registros de `search_vector_records` incluem:
- `query_embedding`
- `document_embedding`
- `quantum_query_state`
- `quantum_doc_state`

## Como rodar
1. Crie o arquivo `.env` a partir do `.env.example`.
2. Preencha o `.env` com os valores reais (segredos, URLs e chaves).
3. Suba o projeto com:
```bash
make setup
```

O alvo `make setup` executa:
- `docker compose build`
- `docker compose up -d`

Acessos locais:
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`

## Variaveis de ambiente
- `.env.example` deve servir apenas como modelo para o `.env`.
- O `.env.example` lista as variaveis esperadas, sem dados sensiveis reais.
- Os valores reais devem ficar somente no `.env`.

## API
Documentacao completa em `API.md`.
