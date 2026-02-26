# Architecture

## Estilo

Clean Architecture com separacao em:

- `domain/`: entidades, value objects, regras e ports
- `application/`: casos de uso (orquestracao)
- `infrastructure/`: adapters concretos (DB, JWT, bcrypt, encoders, metricas, dataset)
- `infrastructure/api/`: delivery via FastAPI

## Principais Casos de Uso

- Auth: `SignUpUseCase`, `SignInUseCase`, `RequestPasswordResetUseCase`, `ConfirmPasswordResetUseCase`, `RefreshTokenUseCase`
- Chats: `CreateChatUseCase`, `ListChatsUseCase`, `GetChatUseCase`, `AddMessageUseCase`, `RenameChatUseCase`, `DeleteChatUseCase`
- IR: `IndexDatasetUseCase`, `SearchUseCase`, `UpsertGroundTruthUseCase`, `EvaluateUseCase`

## Principios importantes aplicados

- Mesma funcao de encoding para indexacao e busca dentro de cada pipeline
- Nao mistura espacos vetoriais (colunas separadas no banco)
- Comparacao metodologica entre representacoes (classica vs quantico-inspirada) usando o mesmo criterio de ranking (cosseno)
- Dependencias de framework ficam fora do dominio
- Rotas finais e rotas compativeis coexistem sem quebrar o front

## Fluxo de Busca (compare)

1. API recebe query + dataset + `mode`
2. `SearchUseCase` chama `encode_embedding` e/ou `encode_quantum`
3. Repositorio consulta apenas a coluna correspondente (`embedding_vector` ou `quantum_vector`)
4. Retorna ranking com score (cosine similarity)
5. Opcional: persistencia de mensagem `assistant` no chat

## Observacoes

- A busca usa PostgreSQL + pgvector com `cosine_distance`
- Os pipelines diferem na representacao vetorial (sBERT vs vetorizacao quantico-inspirada em PennyLane), nao no mecanismo de ranking
