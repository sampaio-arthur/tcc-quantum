from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ErrorDTO:
    code: str
    message: str
    details: Optional[str] = None
