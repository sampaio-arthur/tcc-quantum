# Dependencies

## Runtime (core)

- `fastapi`
- `uvicorn`
- `sqlalchemy`
- `psycopg`
- `alembic`
- `pydantic`, `pydantic-settings`
- `python-jose`
- `passlib[bcrypt]`
- `python-multipart`
- `numpy`
- `scipy`
- `scikit-learn`
- `pgvector`
- `nltk`
- `sentence-transformers`
- `pennylane`

## Testes

- `pytest`
- `httpx` / `fastapi.testclient`

## Observações

- `sentence-transformers` e `pennylane` têm fallback determinístico local quando indisponíveis, para desenvolvimento/testes.
- Em produção, instalar ambos para cumprir o desenho experimental completo.
