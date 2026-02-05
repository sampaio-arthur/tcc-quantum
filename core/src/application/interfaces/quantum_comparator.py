from abc import ABC, abstractmethod
from typing import Sequence


class QuantumComparator(ABC):
    @abstractmethod
    def compare(self, vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
        # Return similarity score in [0, 1].
        raise NotImplementedError
