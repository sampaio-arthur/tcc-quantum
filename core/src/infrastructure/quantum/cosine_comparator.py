from typing import Sequence

import numpy as np

from application.interfaces import QuantumComparator


class CosineSimilarityComparator(QuantumComparator):
    def compare(self, vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
        vec_a = np.array(vector_a, dtype=float)
        vec_b = np.array(vector_b, dtype=float)

        if vec_a.size == 0 or vec_b.size == 0:
            return 0.0

        denom = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)
        if denom == 0:
            return 0.0

        score = float(np.dot(vec_a, vec_b) / denom)
        return float(np.clip(score, 0.0, 1.0))
