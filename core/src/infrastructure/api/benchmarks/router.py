import re

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from infrastructure.api.benchmarks.schemas import BenchmarkLabelIn, BenchmarkLabelListOut, BenchmarkLabelOut
from infrastructure.datasets import PublicDatasetRepository
from infrastructure.persistence.benchmark_label_repository import BenchmarkLabelRepository
from infrastructure.persistence.database import get_db

router = APIRouter(prefix='/benchmarks', tags=['benchmarks'])


def _tokenize(text: str) -> set[str]:
    return {
        token
        for token in re.findall(r'[a-z0-9]+', text.lower())
        if len(token) >= 3
    }


def _infer_relevant_doc_ids(dataset: dict, query_text: str, ideal_answer: str, limit: int = 3) -> list[str]:
    query_tokens = _tokenize(query_text)
    answer_tokens = _tokenize(ideal_answer)

    if not query_tokens and not answer_tokens:
        return []

    scored: list[tuple[float, str]] = []
    for item in dataset.get('documents', []):
        doc_id = item.get('doc_id')
        text = item.get('text', '')
        if not doc_id or not text:
            continue

        doc_tokens = _tokenize(text)
        if not doc_tokens:
            continue

        query_overlap = len(doc_tokens & query_tokens) / max(1, len(query_tokens))
        answer_overlap = len(doc_tokens & answer_tokens) / max(1, len(answer_tokens))
        score = (0.3 * query_overlap) + (0.7 * answer_overlap)
        if score <= 0:
            continue
        scored.append((score, doc_id))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc_id for _, doc_id in scored[:limit]]


@router.get('/labels', response_model=BenchmarkLabelListOut)
def list_labels(dataset_id: str = Query(...), db: Session = Depends(get_db)) -> BenchmarkLabelListOut:
    repository = BenchmarkLabelRepository(db)
    labels = repository.list_labels(dataset_id=dataset_id)
    return BenchmarkLabelListOut(
        items=[
            BenchmarkLabelOut(
                benchmark_id=item.benchmark_id,
                dataset_id=item.dataset_id,
                query_text=item.query_text,
                ideal_answer=item.ideal_answer,
                relevant_doc_ids=item.relevant_doc_ids,
            )
            for item in labels
        ]
    )


@router.post('/labels', response_model=BenchmarkLabelOut)
def upsert_label(payload: BenchmarkLabelIn, db: Session = Depends(get_db)) -> BenchmarkLabelOut:
    query_text = payload.query_text.strip()
    ideal_answer = payload.ideal_answer.strip()

    if not query_text:
        raise HTTPException(status_code=400, detail='Pergunta do gabarito nao pode ser vazia')
    if not ideal_answer:
        raise HTTPException(status_code=400, detail='Resposta ideal do gabarito nao pode ser vazia')

    dataset = PublicDatasetRepository().get_dataset(payload.dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail='Dataset nao encontrado')

    relevant_doc_ids = _infer_relevant_doc_ids(dataset, query_text=query_text, ideal_answer=ideal_answer)

    repository = BenchmarkLabelRepository(db)
    try:
        item = repository.upsert_label(
            dataset_id=payload.dataset_id,
            query_text=query_text,
            ideal_answer=ideal_answer,
            relevant_doc_ids=relevant_doc_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return BenchmarkLabelOut(
        benchmark_id=item.benchmark_id,
        dataset_id=item.dataset_id,
        query_text=item.query_text,
        ideal_answer=item.ideal_answer,
        relevant_doc_ids=item.relevant_doc_ids,
    )


@router.delete('/labels/{dataset_id}/{benchmark_id}')
def delete_label(dataset_id: str, benchmark_id: str, db: Session = Depends(get_db)) -> dict:
    repository = BenchmarkLabelRepository(db)
    removed = repository.delete_label(dataset_id=dataset_id, benchmark_id=benchmark_id)
    if not removed:
        raise HTTPException(status_code=404, detail='Gabarito nao encontrado')
    return {'status': 'ok'}
