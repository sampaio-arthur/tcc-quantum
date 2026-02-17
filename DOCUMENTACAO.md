Documentacao Tecnica - Quantum Search (TCC)

1. Escopo
- Comparar busca classica e busca quantico-inspirada em base unica.
- Foco principal: acuracia.
- Latencia: metrica auxiliar.

2. Pipeline ponta a ponta
2.1 Carga e indexacao
- Dataset em core/data/public_datasets.json.
- Cada documento e transformado em embedding.
- Persistencia no banco para reuso em buscas futuras na tabela dataset_document_index.

2.2 Consulta
- Usuario envia pergunta livre.
- Pergunta e transformada em embedding para busca vetorial e semantica.
- Sistema executa classico e quantico no modo compare.

2.3 Gabarito
- Tela de gabaritos recebe dataset, pergunta e resposta ideal.
- Backend salva o gabarito e infere automaticamente documentos relevantes.
- Usuario nao precisa informar IDs tecnicos.

2.4 Avaliacao
Metricas de ranking (baseadas em relevant_doc_ids inferidos):
- accuracy_at_k
- recall_at_k
- mrr
- ndcg_at_k

Metrica de resposta (baseada em resposta ideal):
- answer_similarity

Metrica auxiliar:
- latency_ms

3. Persistencia
- dataset_document_index: documentos e embeddings indexados.
- benchmark_ground_truths: gabaritos (query_text, ideal_answer, relevant_doc_ids).
- search_runs e search_vector_records: rastros de execucao.

4. Fallback
- Quando a consulta nao tem relevancia suficiente, resposta: Nao foi possivel consultar.

5. Endpoints chave
- POST /search/dataset/index
- POST /search/dataset
- GET /benchmarks/labels
- POST /benchmarks/labels
- DELETE /benchmarks/labels/{dataset_id}/{benchmark_id}
