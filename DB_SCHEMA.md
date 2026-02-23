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

- `dataset`
- `doc_id`
- `text`
- `metadata` (JSON/JSONB)
- `embedding_vector`
- `quantum_vector`

Constraint:

- `UNIQUE(dataset, doc_id)`

### `ground_truth`

- `dataset`
- `query_id`
- `query_text`
- `relevant_doc_ids` (JSON/JSONB)
- `user_id` (opcional)
- `created_at`

Constraint:

- `UNIQUE(dataset, query_id)`

## Vetores

- Em PostgreSQL: `pgvector` via `VectorType`
- Em SQLite/testes: fallback JSON para facilitar execução local
