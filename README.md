# Quantum Search (TCC)

Plataforma para comparar busca classica e busca quantico-inspirada em RAG, com foco principal em acuracia.

## Objetivo
Medir se a arquitetura quantico-inspirada melhora a precisao de recuperacao e resposta versus a classica, no mesmo dataset.

## Fluxo implementado
1. Carrega dataset de core/data/public_datasets.json.
2. Transforma cada documento em embedding e persiste para reuso na tabela dataset_document_index.
3. Recebe pergunta do usuario e transforma em embedding para busca vetorial e semantica.
4. Executa classico e quantico no modo compare.
5. Compara resultado com gabarito salvo (pergunta + resposta ideal) para calcular:
- metricas de ranking: accuracy_at_k, recall_at_k, mrr, ndcg_at_k
- metrica de resposta: answer_similarity
- metrica auxiliar: latency_ms

## Gabarito de acuracia
- A tela de gabaritos recebe apenas dataset, pergunta e resposta ideal.
- O backend infere automaticamente os documentos relevantes para manter as metricas de ranking.
- Nao e necessario informar label_id ou doc_id manualmente.

## Fallback
Se a consulta nao tiver relacao suficiente com o dataset, o retorno e: Nao foi possivel consultar.

## Endpoints principais
- POST /search/dataset/index
- POST /search/dataset
- GET /benchmarks/labels?dataset_id=...
- POST /benchmarks/labels
- DELETE /benchmarks/labels/{dataset_id}/{benchmark_id}

## Execucao rapida
- make setup
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
