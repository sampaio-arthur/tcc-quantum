from application.dtos import SearchFileRequestDTO, SearchRequestDTO, SearchResponseDTO
from application.use_cases import BuscarPorArquivoUseCase, RealizarBuscaUseCase


class SearchService:
    def __init__(self, buscar_use_case: RealizarBuscaUseCase, buscar_por_arquivo_use_case: BuscarPorArquivoUseCase) -> None:
        self._buscar_use_case = buscar_use_case
        self._buscar_por_arquivo_use_case = buscar_por_arquivo_use_case

    def buscar_por_texto(self, request: SearchRequestDTO) -> SearchResponseDTO:
        return self._buscar_use_case.execute(request.query, request.documents)

    def buscar_por_arquivo(self, request: SearchFileRequestDTO) -> SearchResponseDTO:
        docs = self._buscar_por_arquivo_use_case.execute(request.filename, request.content)
        if not docs:
            return SearchResponseDTO(query=request.query, results=[])
        return self._buscar_use_case.execute(request.query, docs)
