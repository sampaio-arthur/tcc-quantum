# Documentacao do Projeto - Quantum Search (TCC)

## Objetivo
Plataforma academica para comparar busca semantica classica e uma abordagem quantico-inspirada (simulada com PennyLane), no contexto de GenAI e RAG. O foco e a analise de ranking, latencia e qualidade da recuperacao.

## O que a plataforma faz
- Permite escolher a fonte de dados (PDF/TXT ou dataset publico).
- Executa busca semantica classica e/ou quantica.
- Exibe resposta baseada em RAG simples (selecao de sentencas) e fontes.
- Gera metricas de qualidade (Recall@K, MRR, NDCG@K) quando existem rotulos de relevancia.
- Mostra comparacao visual entre modo classico e quantico.

## Fluxo principal
1. Ingestao de documentos (PDF/TXT ou dataset).
2. Chunking do texto para melhorar a recuperacao.
3. Embeddings com Sentence Transformers.
4. Busca classica (cosine similarity) e modo quantico (reranking com swap test).
5. Resposta com trechos mais relevantes.
6. Metricas e comparacao visual.

## Modos de busca
- Classico: ranking direto por similaridade de embeddings.
- Quantico: prefiltra por similaridade classica e reordena candidatos com swap test (PennyLane).
- Comparar: executa os dois modos e exibe metricas lado a lado.

## Fonte de dados
### PDF/TXT
- O usuario envia um arquivo.
- O backend extrai o texto e quebra em trechos (chunks).
- A busca semantica e feita sobre esses trechos, entao as respostas sao baseadas no conteudo do PDF/TXT.

### Dataset publico
- Consultas predefinidas com rotulos de relevancia.
- Permite avaliar metricas de ranking com comparacao classico vs quantico.

## Metricas utilizadas
- Recall@K
- MRR
- NDCG@K
- Latencia (ms)

As metricas de ranking aparecem apenas quando a consulta possui rotulos de relevancia.

## Tecnologias utilizadas
Backend:
- Python
- FastAPI
- Sentence Transformers (embeddings)
- PennyLane (simulacao quantica)
- SQLAlchemy (auth/chat)

Frontend:
- React + Vite
- TailwindCSS

## Estrutura do backend (resumo)
- `core/src/application/use_cases/search/realizar_busca_use_case.py`: motor de busca com modo classico/quantico
- `core/src/infrastructure/quantum/swap_test_comparator.py`: comparador quantico
- `core/src/infrastructure/quantum/cosine_comparator.py`: comparador classico
- `core/src/infrastructure/api/search/search_controller.py`: endpoints de busca
- `core/src/infrastructure/datasets/public_dataset_repository.py`: datasets publicos

## Estrutura do frontend (resumo)
- `frontend/src/pages/Chat.tsx`: tela principal com controles
- `frontend/src/components/chat/ComparisonPanel.tsx`: painel de metricas e comparacao
- `frontend/src/components/chat/ChatInput.tsx`: envio de mensagens e upload

## Como executar
Backend:
1. Copie `.env.example` para `.env`.
2. Suba com Docker:
```
docker compose build
docker compose up -d
```

Frontend:
1. Instale dependencias:
```
npm install
```
2. Rode o frontend:
```
npm run dev
```

## Limitacoes conhecidas
- A simulacao quantica (swap test) e mais lenta para muitos documentos.
- Os datasets publicos sao reduzidos por padrao para rodar em notebook comum.
- A geracao de resposta e baseada em sentencas, nao em LLM remoto.

## Extensoes futuras
- Reranker classico com cross-encoder.
- Mais datasets publicos e consultas.
- Persistencia de experimentos no banco.
