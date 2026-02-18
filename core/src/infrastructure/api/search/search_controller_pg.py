import os
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy.orm import Session

from application.dtos import DocumentDTO, SearchFileRequestDTO, SearchRequestDTO
from application.services import SearchService
from application.use_cases import BuscarPorArquivoUseCase, RealizarBuscaUseCase
from infrastructure.api.search.file_reader import PdfTxtDocumentTextExtractor
from infrastructure.api.search.schemas import (
    DatasetIndexRequest as DatasetIndexRequestSchema,
    DatasetIndexResponse as DatasetIndexResponseSchema,
    DatasetSearchRequest as DatasetSearchRequestSchema,
    SearchRequest as SearchRequestSchema,
    SearchResponse as SearchResponseSchema,
    SearchResponseLite as SearchResponseLiteSchema,
)
from infrastructure.datasets import PublicDatasetRepository
from infrastructure.embeddings import build_embedder_from_env
from infrastructure.persistence.benchmark_label_repository import BenchmarkLabelRepository
from infrastructure.persistence.database import get_db
from infrastructure.persistence.dataset_index_repository import DatasetIndexRepository, IndexedDocument
from infrastructure.persistence.search_trace_repository import SearchTraceRepository
from infrastructure.quantum import CosineSimilarityComparator, SwapTestQuantumComparator

router = APIRouter(prefix='/search', tags=['search'])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 10
_RATE_LIMIT_BUCKETS: dict[str, deque[float]] = defaultdict(deque)


def _build_runtime(db: Session) -> tuple[SearchService, object]:
    embedder = build_embedder_from_env()
    classical = CosineSimilarityComparator()
    quantum = SwapTestQuantumComparator()
    buscar_use_case = RealizarBuscaUseCase(embedder, classical, quantum)
    buscar_por_arquivo_use_case = BuscarPorArquivoUseCase(PdfTxtDocumentTextExtractor())
    trace_repository = SearchTraceRepository(db)
    service = SearchService(
        buscar_use_case,
        buscar_por_arquivo_use_case,
        trace_repository,
        answer_embedder=embedder,
        answer_comparator=classical,
    )
    return service, embedder


def _build_dataset_index_repository(db: Session) -> tuple[DatasetIndexRepository, str, str]:
    provider = os.getenv('EMBEDDER_PROVIDER', 'gemini').strip().lower()
    model = os.getenv('GEMINI_EMBEDDING_MODEL', 'gemini-embedding-001').strip()
    return DatasetIndexRepository(db, provider=provider, model=model), provider, model


def _enforce_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else 'unknown'
    key = f'{client_host}:search'
    now = time.time()
    bucket = _RATE_LIMIT_BUCKETS[key]
    while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail='Muitas requisicoes, tente novamente')
    bucket.append(now)


def _read_upload(file: UploadFile) -> bytes:
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail='Arquivo excede o limite de tamanho')
    if not content:
        raise HTTPException(status_code=400, detail='Arquivo vazio')
    return content


def _to_response_schema(response) -> SearchResponseSchema:
    comparison = None
    if response.comparison:
        comparison = {
            'classical': _to_response_lite_schema(response.comparison.classical),
            'quantum': _to_response_lite_schema(response.comparison.quantum),
        }

    return SearchResponseSchema(
        query=response.query,
        mode=response.mode,
        results=[
            {'doc_id': item.doc_id, 'text': item.text, 'score': item.score}
            for item in response.results
        ],
        answer=response.answer,
        metrics=_metrics_to_schema(response.metrics),
        comparison=comparison,
        algorithm_details=_algorithm_details_to_schema(response.algorithm_details),
    )


def _to_response_lite_schema(response) -> SearchResponseLiteSchema:
    return SearchResponseLiteSchema(
        results=[
            {'doc_id': item.doc_id, 'text': item.text, 'score': item.score}
            for item in response.results
        ],
        answer=response.answer,
        metrics=_metrics_to_schema(response.metrics),
        algorithm_details=_algorithm_details_to_schema(response.algorithm_details),
    )


def _metrics_to_schema(metrics):
    if metrics is None:
        return None
    return {
        'accuracy_at_k': metrics.accuracy_at_k,
        'precision_at_k': metrics.precision_at_k,
        'recall_at_k': metrics.recall_at_k,
        'f1_at_k': metrics.f1_at_k,
        'mrr': metrics.mrr,
        'ndcg_at_k': metrics.ndcg_at_k,
        'answer_similarity': metrics.answer_similarity,
        'has_ideal_answer': metrics.has_ideal_answer,
        'latency_ms': metrics.latency_ms,
        'k': metrics.k,
        'candidate_k': metrics.candidate_k,
        'has_labels': metrics.has_labels,
    }


def _algorithm_details_to_schema(details):
    if details is None:
        return None
    return {
        'algorithm': details.algorithm,
        'comparator': details.comparator,
        'candidate_strategy': details.candidate_strategy,
        'description': details.description,
        'debug': details.debug,
    }

def _dataset_documents(dataset: dict) -> list[DocumentDTO]:
    return [
        DocumentDTO(doc_id=item['doc_id'], text=item['text'])
        for item in dataset.get('documents', [])
    ]

def _to_docs_and_vectors(indexed_docs: list[IndexedDocument]) -> tuple[list[DocumentDTO], list[list[float]]]:
    docs = [DocumentDTO(doc_id=item.doc_id, text=item.text) for item in indexed_docs]
    vectors = [item.embedding for item in indexed_docs]
    return docs, vectors


def _ensure_dataset_indexed(
    dataset_id: str,
    dataset: dict,
    embedder,
    index_repository: DatasetIndexRepository,
    force_reindex: bool,
) -> tuple[list[DocumentDTO], list[list[float]], bool]:
    cached = index_repository.get_documents(dataset_id)
    if cached and not force_reindex:
        docs, vectors = _to_docs_and_vectors(cached)
        return docs, vectors, True

    docs = _dataset_documents(dataset)
    embeddings = embedder.embed_texts([doc.text for doc in docs]) if docs else []
    index_repository.replace_documents(dataset_id, docs, embeddings)

    refreshed = index_repository.get_documents(dataset_id)
    docs_indexed, vectors_indexed = _to_docs_and_vectors(refreshed)
    return docs_indexed, vectors_indexed, False


@router.post('', response_model=SearchResponseSchema)
def search(
    payload: SearchRequestSchema,
    request: Request,
    db: Session = Depends(get_db),
) -> SearchResponseSchema:
    _enforce_rate_limit(request)
    docs = [DocumentDTO(doc_id=f'doc-{i + 1}', text=text) for i, text in enumerate(payload.documents)]
    service, _ = _build_runtime(db)
    dto = SearchRequestDTO(query=payload.query, documents=docs)

    if payload.mode == 'compare':
        response = service.comparar_por_texto(
            dto,
            top_k=payload.top_k,
            candidate_k=payload.candidate_k,
        )
    else:
        response = service.buscar_por_texto(
            dto,
            mode=payload.mode,
            top_k=payload.top_k,
            candidate_k=payload.candidate_k,
        )

    return _to_response_schema(response)


@router.post('/file', response_model=SearchResponseSchema)
def search_file(
    request: Request,
    query: str = Form(''),
    file: UploadFile | None = File(None),
    mode: str = Form('classical'),
    top_k: int = Form(5),
    candidate_k: int = Form(20),
    db: Session = Depends(get_db),
) -> SearchResponseSchema:
    if file is None:
        raise HTTPException(status_code=400, detail='Arquivo nao enviado')
    _enforce_rate_limit(request)

    query_text = (query or '').strip()
    if not query_text:
        query_text = 'Resumo do documento'

    content = _read_upload(file)
    service, _ = _build_runtime(db)
    dto = SearchFileRequestDTO(query=query_text, filename=file.filename or '', content=content)

    default_dataset_id = os.getenv('DEFAULT_DATASET_ID', 'mini-rag').strip() or 'mini-rag'
    ideal_answer: str | None = None
    label_repository = BenchmarkLabelRepository(db)
    db_label = label_repository.find_by_query_text(default_dataset_id, query_text)
    if db_label:
        ideal_answer = db_label.ideal_answer

    if mode == 'compare':
        response = service.comparar_por_arquivo(
            dto,
            top_k=top_k,
            candidate_k=candidate_k,
            ideal_answer=ideal_answer,
        )
    else:
        response = service.buscar_por_arquivo(
            dto,
            mode=mode,
            top_k=top_k,
            candidate_k=candidate_k,
            ideal_answer=ideal_answer,
        )

    return _to_response_schema(response)
@router.post('/dataset/index', response_model=DatasetIndexResponseSchema)
def index_dataset(
    payload: DatasetIndexRequestSchema,
    request: Request,
    db: Session = Depends(get_db),
) -> DatasetIndexResponseSchema:
    _enforce_rate_limit(request)
    repository = PublicDatasetRepository()
    dataset = repository.get_dataset(payload.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail='Dataset nao encontrado')

    _, embedder = _build_runtime(db)
    index_repository, provider, model = _build_dataset_index_repository(db)
    docs, vectors, reused_existing = _ensure_dataset_indexed(
        dataset_id=payload.dataset_id,
        dataset=dataset,
        embedder=embedder,
        index_repository=index_repository,
        force_reindex=payload.force_reindex,
    )

    return DatasetIndexResponseSchema(
        dataset_id=payload.dataset_id,
        indexed_documents=min(len(docs), len(vectors)),
        reused_existing=reused_existing,
        embedder_provider=provider,
        embedder_model=model,
    )

@router.post('/dataset', response_model=SearchResponseSchema)
def search_dataset(
    payload: DatasetSearchRequestSchema,
    request: Request,
    db: Session = Depends(get_db),
) -> SearchResponseSchema:
    _enforce_rate_limit(request)
    repository = PublicDatasetRepository()
    dataset = repository.get_dataset(payload.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail='Dataset nao encontrado')

    query_text = (payload.query or '').strip()
    relevant_doc_ids: list[str] = []
    ideal_answer: str | None = None

    label_repository = BenchmarkLabelRepository(db)

    if payload.query_id:
        db_label = label_repository.find_by_benchmark_id(payload.dataset_id, payload.query_id)
        if db_label:
            if not query_text:
                query_text = db_label.query_text.strip()
            relevant_doc_ids = db_label.relevant_doc_ids
            ideal_answer = db_label.ideal_answer
        else:
            query_info = repository.get_query(payload.dataset_id, payload.query_id)
            if not query_info:
                raise HTTPException(status_code=404, detail='Query nao encontrada')
            if not query_text:
                query_text = query_info.get('query', '').strip()
            relevant_doc_ids = query_info.get('relevant_doc_ids', [])
    elif query_text:
        db_label = label_repository.find_by_query_text(payload.dataset_id, query_text)
        if db_label:
            relevant_doc_ids = db_label.relevant_doc_ids
            ideal_answer = db_label.ideal_answer

    if not query_text:
        raise HTTPException(
            status_code=400,
            detail='Informe query ou query_id para executar a busca no dataset',
        )

    service, embedder = _build_runtime(db)
    index_repository, _, _ = _build_dataset_index_repository(db)
    docs, vectors, _ = _ensure_dataset_indexed(
        dataset_id=payload.dataset_id,
        dataset=dataset,
        embedder=embedder,
        index_repository=index_repository,
        force_reindex=False,
    )

    if payload.mode == 'compare':
        response = service.comparar_dataset_indexado(
            query=query_text,
            indexed_documents=docs,
            indexed_vectors=vectors,
            top_k=payload.top_k,
            candidate_k=payload.candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
        )
    else:
        response = service.buscar_dataset_indexado(
            query=query_text,
            indexed_documents=docs,
            indexed_vectors=vectors,
            mode=payload.mode,
            top_k=payload.top_k,
            candidate_k=payload.candidate_k,
            relevant_doc_ids=relevant_doc_ids,
            ideal_answer=ideal_answer,
        )

    return _to_response_schema(response)
