import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

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

MAX_UPLOAD_BYTES = int(os.getenv("UPLOAD_MAX_BYTES", "5242880"))
ALLOWED_PDF_TYPES = {"application/pdf", "application/x-pdf"}
ALLOWED_TXT_TYPES = {"text/plain"}


def _build_service() -> SearchService:
    embedder = LocalEmbedder()
    classical = CosineSimilarityComparator()
    quantum = SwapTestQuantumComparator()
    buscar_use_case = RealizarBuscaUseCase(embedder, classical, quantum)
    buscar_por_arquivo_use_case = BuscarPorArquivoUseCase(PdfTxtDocumentTextExtractor())
    return SearchService(buscar_use_case, buscar_por_arquivo_use_case)


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
def search(payload: SearchRequestSchema) -> SearchResponseSchema:
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
    query: str = Form(""),
    file: UploadFile | None = File(None),
    mode: str = Form("classical"),
    top_k: int = Form(5),
    candidate_k: int = Form(20),
) -> SearchResponseSchema:
    if file is None:
        raise HTTPException(status_code=400, detail="Arquivo nao enviado")
    if not file.filename:
        raise HTTPException(status_code=400, detail="Nome do arquivo invalido")
    filename = file.filename
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        if file.content_type and file.content_type not in ALLOWED_PDF_TYPES:
            raise HTTPException(status_code=400, detail="Tipo de arquivo PDF invalido")
    elif filename_lower.endswith(".txt"):
        if file.content_type and file.content_type not in ALLOWED_TXT_TYPES:
            raise HTTPException(status_code=400, detail="Tipo de arquivo TXT invalido")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt or .pdf")
    if not query or not query.strip():
        query = "Resumo do documento"
    content = file.file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Arquivo excede o tamanho maximo")
    if not content:
        raise HTTPException(status_code=400, detail="Arquivo vazio ou invalido")
    service = _build_service()
    dto = SearchFileRequestDTO(query=query, filename=filename, content=content)

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
def search_dataset(payload: DatasetSearchRequestSchema) -> SearchResponseSchema:
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

