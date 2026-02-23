# Changelog

## 2026-02-23

- Criado backend `core/` do zero com Clean Architecture
- Implementados módulos de auth JWT + bcrypt + reset de senha
- Implementados chats salvos e mensagens
- Implementados encoders clássico (sBERT/fallback) e quântico (PennyLane/fallback)
- Implementados indexação/busca/ground-truth/avaliação
- Adicionadas rotas finais `/api/*` e rotas compatíveis do front legado
- Adicionada documentação técnica (`API`, `ARCHITECTURE`, `METHODS`, `DB_SCHEMA`, `EVALUATION`, `DEPENDENCIES`, `ROUTES_COMPAT`)
- Adicionado teste mínimo de fluxo (`core/tests/test_api_flow.py`)
