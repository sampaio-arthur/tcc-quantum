# DB Schema

## Tabelas

### `users`

- `id`
- `email` (UNIQUE)
- `password_hash`
- `name`
- `is_active`
- `is_admin`
- `created_at`

### `password_resets`

- `id`
- `user_id` (FK -> `users`)
- `token_hash`
- `expires_at`
- `used_at`
- `created_at`

### `chats`

- `id`
- `user_id` (FK -> `users`)
- `title`
- `created_at`
- `updated_at`
- `deleted_at` (soft delete)

### `chat_messages`

- `id`
- `chat_id` (FK -> `chats`)
- `role` (`user|assistant|system`)
- `content` (texto; payload JSON serializado é permitido para resultado de retrieval)
- `created_at`

### `documents`

- `id`
- `dataset`
- `doc_id`
- `title` (opcional)
- `text`
- `metadata` (JSON/JSONB)
- `embedding_vector`
- `quantum_vector`

Constraint:

- `UNIQUE(dataset, doc_id)`

### `queries`

- `id`
- `dataset`
- `split`
- `query_id`
- `query_text`
- `user_id` (opcional)
- `created_at`

Constraint:

- `UNIQUE(dataset, split, query_id)`

### `qrels`

- `id`
- `dataset`
- `split`
- `query_id`
- `doc_id`
- `relevance` (int)

Constraint:

- `UNIQUE(dataset, split, query_id, doc_id)`

### `dataset_snapshots`

- `id`
- `dataset_id` (UNIQUE)
- `name`
- `provider`
- `description`
- `source_url` (opcional)
- `reference_urls` (JSON/JSONB)
- `max_docs` / `max_queries` (recorte persistido)
- `document_count` / `query_count`
- `document_ids` (JSON/JSONB; lista exata de docs indexados)
- `queries` (JSON/JSONB; snapshot das queries e `relevant_doc_ids`)
- `created_at`
- `updated_at`

Constraint:

- `UNIQUE(dataset_id)`

## Vetores

- PostgreSQL + pgvector via `VectorType`
