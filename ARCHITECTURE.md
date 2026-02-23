# Architecture

## Estilo

Clean Architecture com separação em:

- `domain/`: entidades, value objects, regras e ports
- `application/`: casos de uso (orquestração)
- `infrastructure/`: adapters concretos (DB, JWT, bcrypt, encoders, métricas, dataset)
- `infrastructure/api/`: delivery via FastAPI

## Principais Casos de Uso

- Auth: `SignUpUseCase`, `SignInUseCase`, `RequestPasswordResetUseCase`, `ConfirmPasswordResetUseCase`, `RefreshTokenUseCase`
- Chats: `CreateChatUseCase`, `ListChatsUseCase`, `GetChatUseCase`, `AddMessageUseCase`, `RenameChatUseCase`, `DeleteChatUseCase`
- IR: `IndexDatasetUseCase`, `SearchUseCase`, `UpsertGroundTruthUseCase`, `EvaluateUseCase`

## Princípios importantes aplicados

- Mesma função de encoding para indexação e busca por pipeline
- Não mistura espaços vetoriais (colunas separadas no banco)
- Dependências de framework ficam fora do domínio
- Rotas finais e rotas compatíveis coexistem sem quebrar o front

## Fluxo de Busca (compare)

1. API recebe query + dataset + `mode`
2. `SearchUseCase` chama `encode_embedding` e/ou `encode_quantum`
3. Repositório consulta apenas a coluna correspondente
4. Retorna ranking com score (cosine similarity)
5. Opcional: persistência de mensagem `assistant` no chat

## Observações

- Em PostgreSQL + pgvector, a busca usa `cosine_distance` quando disponível
- Em SQLite/testes, há fallback de cálculo de similaridade em Python
