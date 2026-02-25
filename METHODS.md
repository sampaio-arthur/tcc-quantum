# Methods

## Pipeline 1 - Clássico (sBERT)

- Encoder: `SbertEncoder` (`core/src/infrastructure/encoders/classical.py`)
- Função única: `encode(text)` usada para documentos e queries
- Saída: vetor real denso
- Normalização: L2 explícita

## Pipeline 2 - Quântico-inspirado (PennyLane)

- Encoder: `PennyLaneQuantumEncoder` (`core/src/infrastructure/encoders/quantum.py`)
- Função única: `encode(text)` usada para documentos e queries
- Não usa embeddings sBERT

### Especificação atual

- `n_qubits`: configurável (default `4`)
- Dimensão da saída: `2 ** n_qubits` (default `16`)
- Mapeamento texto -> parâmetros:
  - hash SHA-256 por token
  - agregação determinística em ângulos
- Circuito:
  - `AngleEmbedding` (Y)
  - cadeia de `CNOT`
  - `RZ` por qubit
  - medição de probabilidades (`qml.probs`)
- Vetor final:
  - probabilidades reais `float32`
  - L2-normalizado

## Similaridade / Score

- Vetores L2-normalizados
- Similaridade alvo no banco: cosseno via pgvector (`cosine_distance`)
- `score = 1 - cosine_distance`

## Métricas (implementação)

- `precision@k` e `recall@k`: `sklearn.metrics.precision_score` / `recall_score`
  - construção de vetores binários sobre a união `top-k recuperado ∪ relevantes`
- `ndcg@k`: `sklearn.metrics.ndcg_score` (ganho binário)
- `spearman`: `scipy.stats.spearmanr`

Observação:

- métricas de IR canônicas são calculadas no fluxo de avaliação batch com `ground_truth`
- no chat, a comparacao usa proxies (latencia e mean score@k)

## Reprodutibilidade

- `encode_quantum` determinístico
- Sem amostragem aleatória
- Hashes e mapeamento fixos
