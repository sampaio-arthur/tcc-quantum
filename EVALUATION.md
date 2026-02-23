# Evaluation

## Métricas obrigatórias

- `precision@k`
- `recall@k`
- `ndcg@k`
- `spearman`

## Definições

- `Precision@k = |relevantes ∩ recuperados| / k`
- `Recall@k = |relevantes ∩ recuperados| / |relevantes|`
- `NDCG@k` com ganho binário via `sklearn.metrics.ndcg_score`
- `Spearman`:
  1. união dos `doc_ids` do top-k recuperado e referência
  2. ausente recebe rank `k + 1`
  3. correlação via `scipy.stats.spearmanr`

## Implementação (bibliotecas)

- `precision@k`: `sklearn.metrics.precision_score`
- `recall@k`: `sklearn.metrics.recall_score`
- `ndcg@k`: `sklearn.metrics.ndcg_score`
- `spearman`: `scipy.stats.spearmanr`

Detalhe de modelagem para `precision@k`/`recall@k`:

- o backend constrói vetores binários sobre a união entre `top-k recuperado` e `relevant_doc_ids`
- `y_true`: relevância (ground truth)
- `y_pred`: pertencimento ao top-k recuperado

## Avaliação batch

Endpoint: `POST /api/evaluate`

Entrada:

```json
{ "dataset_id": "reuters", "pipeline": "compare", "k": 5 }
```

Saída inclui:

- agregados por pipeline (médias)
- métricas por query

## Gabaritos persistidos

Endpoint para cadastro/atualização:

- `POST /api/ground-truth`

Compatível com front (labels):

- `GET/POST/DELETE /benchmarks/labels...`
