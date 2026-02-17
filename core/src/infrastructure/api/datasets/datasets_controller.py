from fastapi import APIRouter, HTTPException

from infrastructure.api.datasets.schemas import DatasetDetailOut, DatasetSummaryOut
from infrastructure.datasets import PublicDatasetRepository

router = APIRouter(prefix='/datasets', tags=['datasets'])


@router.get('', response_model=list[DatasetSummaryOut])
def list_datasets() -> list[DatasetSummaryOut]:
    repository = PublicDatasetRepository()
    return [
        DatasetSummaryOut(
            dataset_id=item.dataset_id,
            name=item.name,
            description=item.description,
            document_count=item.document_count,
            query_count=item.query_count,
        )
        for item in repository.list_datasets()
    ]


@router.get('/{dataset_id}', response_model=DatasetDetailOut)
def get_dataset(dataset_id: str) -> DatasetDetailOut:
    repository = PublicDatasetRepository()
    dataset = repository.get_dataset(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail='Dataset nao encontrado')

    queries = [
        {
            'query_id': query['query_id'],
            'query': query['query'],
            'relevant_count': len(query.get('relevant_doc_ids', [])),
        }
        for query in dataset.get('queries', [])
    ]

    documents = [
        {'doc_id': item['doc_id']}
        for item in dataset.get('documents', [])
        if item.get('doc_id')
    ]

    return DatasetDetailOut(
        dataset_id=dataset['id'],
        name=dataset.get('name', dataset['id']),
        description=dataset.get('description', ''),
        queries=queries,
        documents=documents,
    )
