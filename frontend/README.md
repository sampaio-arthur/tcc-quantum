# Quantum Search Frontend

Interface web do projeto de busca semantica comparativa.

O frontend:

- autentica usuarios
- cria e persiste conversas
- dispara indexacao do dataset Reuters
- executa busca comparativa entre:
  - pipeline classico por embeddings (sBERT)
  - pipeline quantico-inspirado por vetorizacao quantica simulada (PennyLane)
- exibe resultados, scores e latencia dos dois pipelines

## Executar localmente

```bash
npm install
npm run dev
```

Aplicacao padrao em `http://localhost:5173` quando executada via Docker Compose deste projeto.

## Build

```bash
npm run build
```

## Testes

```bash
npm run test
```
