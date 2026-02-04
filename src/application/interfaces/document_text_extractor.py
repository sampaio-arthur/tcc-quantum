from abc import ABC, abstractmethod


class DocumentTextExtractor(ABC):
    @abstractmethod
    def extract(self, filename: str, content: bytes) -> str:
        # Return plain text extracted from the file contents.
        raise NotImplementedError
