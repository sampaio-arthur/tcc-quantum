import time
from collections import defaultdict, deque

from fastapi import APIRouter, File, Form, HTTPException, Request, UploadFile

from application.dtos import DocumentDTO, SearchFileRequestDTO, SearchRequestDTO
from application.services import SearchService
from application.use_cases import BuscarPorArquivoUseCase, RealizarBuscaUseCase
from infrastructure.api.search.file_reader import PdfTxtDocumentTextExtractor
from infrastructure.api.search.schemas import (
    DatasetSearchRequest as DatasetSearchRequestSchema,
    SearchRequest as SearchRequestSchema,
    SearchResponse as SearchResponseSchema,
    SearchResponseLite as SearchResponseLiteSchema,
)
from infrastructure.datasets import PublicDatasetRepository
from infrastructure.embeddings import LocalEmbedder
from infrastructure.quantum import CosineSimilarityComparator, SwapTestQuantumComparator

router = APIRouter(prefix="/search", tags=["search"])

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 10
_RATE_LIMIT_BUCKETS: dict[str, deque[float]] = defaultdict(deque)


def _build_service() -> SearchService:
    embedder = LocalEmbedder()
    classical = CosineSimilarityComparator()
    quantum = SwapTestQuantumComparator()
    buscar_use_case = RealizarBuscaUseCase(embedder, classical, quantum)
    buscar_por_arquivo_use_case = BuscarPorArquivoUseCase(PdfTxtDocumentTextExtractor())
    return SearchService(buscar_use_case, buscar_por_arquivo_use_case)


def _enforce_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    key = f"{client_host}:search"
    now = time.time()
    bucket = _RATE_LIMIT_BUCKETS[key]
    while bucket and now - bucket[0] > RATE_LIMIT_WINDOW_SECONDS:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT_MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Muitas requisicoes, tente novamente")
    bucket.append(now)


def _read_upload(file: UploadFile) -> bytes:
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Arquivo excede o limite de tamanho")
    if not content:
        raise HTTPException(status_code=400, detail="Arquivo vazio")
    return content


def _to_response_schema(response) -> SearchResponseSchema:
    comparison = None
    if response.comparison:
        comparison = {
            "classical": _to_response_lite_schema(response.comparison.classical),
            "quantum": _to_response_lite_schema(response.comparison.quantum),
        }

    return SearchResponseSchema(
        query=response.query,
        mode=response.mode,
        results=[
            {"doc_id": item.doc_id, "text": item.text, "score": item.score}
            for item in response.results
        ],
        answer=response.answer,
        metrics=_metrics_to_schema(response.metrics),
        comparison=comparison,
    )


def _to_response_lite_schema(response) -> SearchResponseLiteSchema:
    return SearchResponseLiteSchema(
        results=[
            {"doc_id": item.doc_id, "text": item.text, "score": item.score}
            for item in response.results
        ],
        answer=response.answer,
        metrics=_metrics_to_schema(response.metrics),
    )


def _metrics_to_schema(metrics):
    if metrics is None:
        return None
    return {
        "recall_at_k": metrics.recall_at_k,
        "mrr": metrics.mrr,
        "ndcg_at_k": metrics.ndcg_at_k,
        "latency_ms": metrics.latency_ms,
        "k": metrics.k,
        "candidate_k": metrics.candidate_k,
        "has_labels": metrics.has_labels,
    }


@router.post("", response_model=SearchResponseSchema)
def search(payload: SearchRequestSchema, request: Request) -> SearchResponseSchema:
    _enforce_rate_limit(request)
    docs = [DocumentDTO(doc_id=f"doc-{i+1}", text=text) for i, text in enumerate(payload.documents)]
    service = _build_service()
    dto = SearchRequestDTO(query=payload.query, documents=docs)

    if payload.mode == "compare":
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


@router.post("/file", response_model=SearchResponseSchema)
def search_file(
    request: Request,
    query: str = Form(""),
    file: UploadFile | None = File(None),
    mode: str = Form("classical"),
    top_k: int = Form(5),
    candidate_k: int = Form(20),
) -> SearchResponseSchema:
    if file is None:
        raise HTTPException(status_code=400, detail="Arquivo nao enviado")
    _enforce_rate_limit(request)
    if not query or not query.strip():
        query = "Resumo do documento"
    content = _read_upload(file)
    service = _build_service()
    dto = SearchFileRequestDTO(query=query, filename=file.filename or "", content=content)

    if mode == "compare":
        response = service.comparar_por_arquivo(dto, top_k=top_k, candidate_k=candidate_k)
    else:
        response = service.buscar_por_arquivo(
            dto,
            mode=mode,
            top_k=top_k,
            candidate_k=candidate_k,
        )

    return _to_response_schema(response)


@router.post("/dataset", response_model=SearchResponseSchema)
def search_dataset(payload: DatasetSearchRequestSchema, request: Request) -> SearchResponseSchema:
    _enforce_rate_limit(request)
    repository = PublicDatasetRepository()
    dataset = repository.get_dataset(payload.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset nao encontrado")

    query_info = repository.get_query(payload.dataset_id, payload.query_id)
    if not query_info:
        raise HTTPException(status_code=404, detail="Query nao encontrada")

    docs = [
        DocumentDTO(doc_id=item["doc_id"], text=item["text"])
        for item in dataset.get("documents", [])
    ]
    dto = SearchRequestDTO(query=query_info["query"], documents=docs)

    relevant_doc_ids = query_info.get("relevant_doc_ids", [])
    service = _build_service()

    if payload.mode == "compare":
        response = service.comparar_por_texto(
            dto,
            top_k=payload.top_k,
            candidate_k=payload.candidate_k,
            relevant_doc_ids=relevant_doc_ids,
        )
    else:
        response = service.buscar_por_texto(
            dto,
            mode=payload.mode,
            top_k=payload.top_k,
            candidate_k=payload.candidate_k,
            relevant_doc_ids=relevant_doc_ids,
        )

    return _to_response_schema(response)

