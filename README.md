Quantum Search (TCC)

Visao geral
- Quantum Search compara dois caminhos de recuperacao no mesmo conjunto de dados.
- Caminho classico: similaridade cosseno sobre embeddings.
- Caminho quantico-inspirado: pre-selecao classica e reordenacao com swap test em PennyLane.
- A plataforma mede qualidade de ranking e qualidade de resposta usando gabaritos.

Objetivo do projeto
- Avaliar se a arquitetura quantico-inspirada melhora a acuracia em relacao ao caminho classico.
- Medir desempenho com metrica auxiliar de latencia.

O que a aplicacao faz passo a passo
1) Carrega datasets de core/data/public_datasets.json.
2) Indexa documentos em embeddings e persiste no banco para reuso.
3) Recebe pergunta do usuario.
4) Executa busca classica e quantica no modo compare.
5) Compara com gabarito salvo quando houver.
6) Calcula metricas de ranking e similaridade de resposta.
7) Retorna detalhes tecnicos do algoritmo usado.

Fluxo de indexacao
- Endpoint: POST /search/dataset/index.
- Leitura de documentos do dataset selecionado.
- Geracao de embedding por documento.
- Persistencia em dataset_document_index.
- Reuso do indice quando provider e model de embedding forem os mesmos.

Fluxo de gabarito
- Tela de Benchmarks recebe pergunta e resposta ideal.
- Backend infere relevant_doc_ids automaticamente.
- Persistencia na tabela benchmark_ground_truths.
- Na interface atual, Benchmarks usa dataset padrao mini-rag.

Fluxo de busca em dataset
- Endpoint: POST /search/dataset.
- Entrada aceita query ou query_id.
- Resolve relevant_doc_ids e ideal_answer por benchmark salvo quando existir.
- Executa comparacao classica e quantica.
- Retorna resultados, metricas e algorithm_details.

Fluxo de busca por arquivo
- Endpoint: POST /search/file.
- Suporta TXT e PDF.
- Extrai texto e quebra em chunks com overlap.
- Busca sobre chunks.
- Se houver gabarito para a pergunta no dataset padrao, calcula metricas com ideal_answer.

Fallback
- Quando relevancia e baixa, answer retorna Nao foi possivel consultar.
- Limiar configuravel por SEARCH_MIN_RELEVANCE_SCORE.

Metricas retornadas
- accuracy_at_k
- recall_at_k
- mrr
- ndcg_at_k
- answer_similarity
- latency_ms
- has_labels
- has_ideal_answer
- k
- candidate_k

Detalhes de algoritmo retornados
- algorithm
- comparator
- candidate_strategy
- description
- debug

Tecnologias e bibliotecas
Backend
- Python 3
- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL com pgvector
- NumPy, SciPy, pandas, scikit-learn
- PennyLane
- Qiskit, Qiskit Aer
- pypdf
- python-jose
- passlib e bcrypt
- pytest

Frontend
- React 18
- TypeScript
- Vite
- React Router
- Tailwind CSS
- Radix UI
- TanStack React Query
- Vitest e Testing Library

Infra
- Docker Compose
- Servicos: core, frontend, db

Persistencia principal
- users
- conversations
- messages
- dataset_document_index
- benchmark_ground_truths
- search_runs
- search_vector_records

Como executar
Via Make
- make setup
- make up
- make down
- make logs
- make test

Via Docker Compose
- docker compose build
- docker compose up -d

URLs locais
- backend: http://localhost:8000
- frontend: http://localhost:5173
- health: http://localhost:8000/health

Variaveis de ambiente
Arquivo base: .env.example

App
- APP_ENV

Seguranca
- SECRET_KEY
- JWT_SECRET
- JWT_ALGORITHM
- ACCESS_TOKEN_EXPIRE_MINUTES

Banco
- DB_HOST
- DB_PORT
- DB_NAME
- DB_USER
- DB_PASSWORD
- DATABASE_URL

Frontend
- VITE_API_BASE_URL

Embeddings
- EMBEDDER_PROVIDER
- GEMINI_API_KEY
- GEMINI_EMBEDDING_MODEL

Variaveis funcionais importantes
- DEFAULT_DATASET_ID
- SEARCH_MIN_RELEVANCE_SCORE

Procedimento recomendado de uso
1) Registrar usuario.
2) Autenticar e abrir chat.
3) Cadastrar gabaritos em Benchmarks.
4) Indexar dataset.
5) Executar consultas em compare.
6) Avaliar metricas e detalhes do algoritmo.
7) Repetir com novas perguntas e novos arquivos.

Observacoes operacionais
- Rate limit de busca: 10 requisicoes por minuto por host.
- Upload maximo em busca por arquivo: 5 MB.
- CORS aberto para todos os origins no estado atual.

Arquivos complementares
- API.md
- DOCUMENTACAO.md
