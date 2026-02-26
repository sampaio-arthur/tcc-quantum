# Methods

## Pipeline 1 - Classico (sBERT)

- Encoder: `SbertEncoder` (`core/src/infrastructure/encoders/classical.py`)
- Funcao unica: `encode(text)` usada para documentos e queries
- Saida: vetor real denso
- Normalizacao: L2 explicita

## Pipeline 2 - Quantico-inspirado (PennyLane)

- Encoder: `PennyLaneQuantumEncoder` (`core/src/infrastructure/encoders/quantum.py`)
- Funcao unica: `encode(text)` usada para documentos e queries
- Nao usa embeddings sBERT

### Especificacao atual

- `n_qubits`: configuravel (default `4`)
- Dimensao da saida: `2 ** n_qubits` (default `16`)
- Mapeamento texto -> parametros:
  - hash SHA-256 por token
  - agregacao deterministica em angulos
- Circuito:
  - `AngleEmbedding` (Y)
  - cadeia de `CNOT`
  - `RZ` por qubit
  - medicao de probabilidades (`qml.probs`)
- Vetor final:
  - probabilidades reais `float32`
  - L2-normalizado

## Similaridade / Score

- Vetores L2-normalizados
- Similaridade alvo no banco: cosseno via pgvector (`cosine_distance`)
- `score = 1 - cosine_distance`

## Metricas (implementacao)

- `precision@k` e `recall@k`: `sklearn.metrics.precision_score` / `recall_score`
  - construcao de vetores binarios sobre a uniao `top-k recuperado U relevantes`
- `ndcg@k`: `sklearn.metrics.ndcg_score` (ganho binario)
- `spearman`: `scipy.stats.spearmanr`

Observacao:

- metricas de IR canonicas sao calculadas no fluxo de avaliacao batch com `ground_truth`
- no chat, a comparacao usa proxies (latencia e mean score@k)

## Reprodutibilidade

- `encode_quantum` deterministico
- Sem amostragem aleatoria
- Hashes e mapeamento fixos

## Formulas e Calculos (Algoritmos e Metricas)

Este arquivo descreve as formulas realmente usadas no codigo atual para encoding, score e metricas.

## 1. Normalizacao L2

Arquivo: `core/src/domain/ir.py`

Para um vetor `v = [v1, v2, ..., vn]`:

- Norma L2: `||v||2 = sqrt(sum(vi^2))`
- Vetor normalizado: `v_hat = v / ||v||2`

Caso especial:

- Se `||v||2 = 0`, o codigo retorna vetor de zeros com o mesmo tamanho.

## 2. Similaridade / score de busca

### 2.1 Em PostgreSQL + pgvector

Arquivo: `core/src/infrastructure/repositories/sqlalchemy_repositories.py`

O banco ordena por `cosine_distance` e o backend expoe:

- `score = 1 - cosine_distance(query_vector, doc_vector)`

## 3. Encoder classico (sBERT)

Arquivo: `core/src/infrastructure/encoders/classical.py`

Pipeline:

1. `SentenceTransformer(model_name)`
2. `model.encode(text, convert_to_numpy=True, normalize_embeddings=True)`
3. Conversao para `list[float]`
4. Normalizacao L2 adicional via `l2_normalize(...)`

Resultado:

- Vetor denso em `embedding_vector`
- Dimensao esperada pelo schema atual: `384` (`all-MiniLM-L6-v2`)

## 4. Encoder quantico-inspirado (PennyLane)

Arquivo: `core/src/infrastructure/encoders/quantum.py`

### 4.1 Texto -> angulos

Para cada token `t`:

1. `digest = SHA256(t)`
2. Para cada qubit `i` (`0` ate `n_qubits-1`), acumula:

`angle_i += (digest[i] / 255) * pi`

`angle_i += ((digest[i + n_qubits] / 255) - 0.5) * 0.25`

Ao final:

- `angle_i = angle_i mod (2*pi)`

### 4.2 Circuito

Com `n_qubits` (default `4`):

1. `AngleEmbedding(angles, rotation='Y')`
2. Cadeia de `CNOT` entre qubits vizinhos
3. `RZ(angle_i / 2)` em cada qubit
4. Medicao `qml.probs(...)`

### 4.3 Vetor final

- Saida bruta: probabilidades da base computacional
- Dimensao: `2^n_qubits` (default `16`)
- Conversao para `float32`
- Normalizacao L2 final

## 5. Busca em modo compare (comparacao entre pipelines)

Arquivo: `core/src/application/ir_use_cases.py` (`_compare_rankings`)

Sejam:

- `Ck` = `doc_ids` do top-k classico
- `Qk` = `doc_ids` do top-k quantico

### 5.1 `common_doc_ids`

- `common_doc_ids = intersecao(Ck, Qk)` (lista ordenada dos ids em comum no top-k)

### 5.2 Media de score@k

Para uma lista `Rk`:

- `mean_score@k = sum(score_i) / max(len(Rk), 1)`

## 6. Metricas de avaliacao batch (IR)

Arquivo: `core/src/infrastructure/metrics/sklearn_metrics.py`

Sejam:

- `topk_retrieved = retrieved_doc_ids[:k]`
- `relevant_set = set(relevant_doc_ids)`
- `U = uniao(topk_retrieved, relevant_set)` (ordem preservada)

### 6.1 Vetores binarios para precision/recall

Para cada `doc` em `U`:

- `y_true(doc) = 1` se `doc in relevant_set`, senao `0`
- `y_pred(doc) = 1` se `doc in topk_retrieved`, senao `0`

O codigo aplica:

- `precision_score(y_true_cls, y_pred_cls, zero_division=0)`
- `recall_score(y_true_cls, y_pred_cls, zero_division=0)`

Observacao:

- Isso equivale ao calculo sobre o conjunto efetivamente recuperado.
- Se vierem menos de `k` resultados, a precisao nao usa denominador `k` fixo.

### 6.2 NDCG@k (ganho binario)

- `y_true`: relevancia binaria para os docs do `topk_retrieved`
- `y_score`: scores dos docs recuperados
- Se tamanho < `k`, o codigo faz `pad` com zeros
- Formula calculada pela lib: `ndcg_score(y_true, y_score, k=k)`

### 6.3 Spearman top-k com rank padrao para ausentes

Sejam:

- `retrieved_ref = retrieved_doc_ids[:k]`
- `reference_ref = relevant_doc_ids[:k]`
- `union_ids = uniao(retrieved_ref, reference_ref)`
- `default_rank = k + 1`

Ranks usados:

- `r_rank(doc)` = posicao em `retrieved_ref` (1-based), ou `k+1` se ausente
- `g_rank(doc)` = posicao em `reference_ref` (1-based), ou `k+1` se ausente

O codigo calcula:

- `spearman = scipy.stats.spearmanr(a, b).correlation`

Tratamento de borda:

- Se `len(union_ids) < 2`, retorna `1.0`
- Se correlacao vier `None` ou `NaN`, retorna `0.0`

## 7. Validacoes de dimensao na inicializacao

Arquivo: `core/src/infrastructure/api/fastapi_app.py`

Ao subir a API, o codigo valida:

- `embedding_dim == 384`
- `quantum_dim == 2 ** quantum_n_qubits`

Esses valores precisam bater com o schema atual em `documents`:

- `embedding_vector = VectorType(384)`
- `quantum_vector = VectorType(16)`

## 8. Lote de indexacao

Arquivo: `core/src/application/ir_use_cases.py`

A indexacao faz persistencia em lotes de:

- `64` documentos por flush/upsert

Impacto:

- reduz numero de commits
- atualiza progresso do job de indexacao compativel por lote
