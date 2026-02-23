from __future__ import annotations

import math


def l2_normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0.0:
        return [0.0 for _ in vector]
    return [float(x / norm) for x in vector]


def cosine_score_from_distance(distance: float) -> float:
    return 1.0 - float(distance)
