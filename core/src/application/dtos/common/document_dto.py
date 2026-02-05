from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentDTO:
    doc_id: str
    text: str
