from typing import Sequence

import numpy as np
import pennylane as qml

from application.interfaces import QuantumComparator


def _next_power_of_two(value: int) -> int:
    if value <= 0:
        raise ValueError("Value must be positive")
    power = 1
    while power < value:
        power *= 2
    return power


def _pad_and_normalize(vector: np.ndarray, target_len: int) -> np.ndarray:
    if target_len <= 0:
        raise ValueError("Target length must be positive")
    if vector.size == 0:
        raise ValueError("Vector must be non-empty")
    if vector.size > target_len:
        raise ValueError("Target length smaller than vector length")
    if vector.size < target_len:
        vector = np.pad(vector, (0, target_len - vector.size))
    norm = np.linalg.norm(vector)
    if norm == 0:
        raise ValueError("Vector norm is zero")
    return vector / norm


def _cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    score = float(np.dot(vec_a, vec_b) / (norm_a * norm_b))
    return float(np.clip(score, 0.0, 1.0))


class SwapTestQuantumComparator(QuantumComparator):
    # Keep simulation tractable. 64 dims => 6 qubits per register (+1 ancilla).
    MAX_QUANTUM_VECTOR_LEN = 64

    def compare(self, vector_a: Sequence[float], vector_b: Sequence[float]) -> float:
        vec_a = np.array(vector_a, dtype=float)
        vec_b = np.array(vector_b, dtype=float)

        if vec_a.size == 0 or vec_b.size == 0:
            raise ValueError("Vectors must be non-empty")

        if max(vec_a.size, vec_b.size) > self.MAX_QUANTUM_VECTOR_LEN:
            return _cosine_similarity(vec_a, vec_b)

        target_len = _next_power_of_two(max(vec_a.size, vec_b.size))
        vec_a = _pad_and_normalize(vec_a, target_len)
        vec_b = _pad_and_normalize(vec_b, target_len)

        n_qubits = int(np.log2(target_len))
        dev = qml.device("default.qubit", wires=1 + 2 * n_qubits)

        @qml.qnode(dev)
        def circuit() -> np.ndarray:
            qml.Hadamard(wires=0)
            qml.AmplitudeEmbedding(vec_a, wires=range(1, 1 + n_qubits), normalize=False)
            qml.AmplitudeEmbedding(
                vec_b, wires=range(1 + n_qubits, 1 + 2 * n_qubits), normalize=False
            )
            for i in range(n_qubits):
                qml.CSWAP(wires=[0, 1 + i, 1 + n_qubits + i])
            qml.Hadamard(wires=0)
            return qml.probs(wires=0)

        prob_zero = circuit()[0]
        similarity = 2 * prob_zero - 1
        return float(np.clip(similarity, 0.0, 1.0))
