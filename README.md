# Quantum Search (TCC)

Plataforma academica para comparar busca semantica classica com uma abordagem quantico-inspirada (swap test via PennyLane) aplicada a RAG simples. O foco e comparar ranking e latencia entre os modos.

## Funcao principal do app
- Receber um PDF/TXT (ou usar dataset publico via API), extrair texto e dividir em chunks.
- Gerar embeddings e buscar trechos relevantes.
- Executar modo classico (cosine similarity) e/ou modo quantico (prefiltro classico + reranking por swap test).
- Exibir resultados, pipeline e comparacao de metricas quando houver rotulos de relevancia.

## O que ele compara, para que e como
- Compara dois metodos de ranking: classico vs quantico-inspirado.
- Objetivo: medir qualidade de recuperacao (Recall@K, MRR, NDCG@K quando disponivel) e latencia (ms).
- Como: o modo quantico usa o ranking classico para selecionar candidatos e reordena com swap test; o modo comparar executa ambos e mostra os resultados lado a lado.

## Como usar (passo a passo na interface)
1. Suba o backend e o frontend (ver passos abaixo).
2. Abra o frontend no navegador e faca login/cadastro.
3. Crie ou selecione uma conversa.
4. Anexe um arquivo PDF/TXT e clique em enviar.
5. Veja os resultados, a pipeline e o painel de comparacao.
6. Use o historico para voltar a conversas anteriores.

## Como rodar localmente
### Backend
1. Copie `.env.example` para `.env` e ajuste se necessario.
2. Suba os servicos:
```
docker compose build
docker compose up -d
```
3. API disponivel em `http://localhost:8000`.

### Frontend
1. Instale dependencias:
```
npm install
```
2. Rode o frontend:
```
npm run dev
```

## API
Documentacao completa em `API.md`.