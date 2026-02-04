from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    doc_id: str
    text: str
