from typing import Iterable, List

from application.use_cases import RealizarBuscaUseCase, SearchResult
from domain.entities import Document


class SearchService:
    def __init__(self, use_case: RealizarBuscaUseCase) -> None:
        self._use_case = use_case

    def buscar(self, query: str, documents: Iterable[Document]) -> List[SearchResult]:
        return self._use_case.execute(query, documents)
