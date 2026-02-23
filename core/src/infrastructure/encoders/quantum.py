from __future__ import annotations

import hashlib
import math

import numpy as np

from domain.ir import l2_normalize

try:
    import pennylane as qml  # type: ignore
except Exception:  # pragma: no cover
    qml = None


class PennyLaneQuantumEncoder:
    """Deterministic quantum-inspired encoder using a simulated feature map.

    Text -> hashed angles -> AngleEmbedding + entangling layers -> measurement probabilities.
    Output is real float32, fixed dimension = 2**n_qubits, L2-normalized.
    """

    def __init__(self, n_qubits: int = 4) -> None:
        self.n_qubits = n_qubits
        self.dim = 2 ** n_qubits
        self._dev = qml.device("default.qubit", wires=n_qubits) if qml else None
        self._qnode = self._build_qnode() if qml else None

    def _angles_from_text(self, text: str) -> np.ndarray:
        values = np.zeros(self.n_qubits, dtype=np.float64)
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            for i in range(self.n_qubits):
                values[i] += (digest[i] / 255.0) * math.pi
                values[i] += ((digest[i + self.n_qubits] / 255.0) - 0.5) * 0.25
        values = np.mod(values, 2 * math.pi)
        return values

    def _build_qnode(self):
        if not qml:
            return None

        @qml.qnode(self._dev)
        def circuit(angles):
            qml.AngleEmbedding(angles, wires=range(self.n_qubits), rotation="Y")
            for i in range(self.n_qubits - 1):
                qml.CNOT(wires=[i, i + 1])
            for i in range(self.n_qubits):
                qml.RZ(angles[i] / 2.0, wires=i)
            return qml.probs(wires=range(self.n_qubits))

        return circuit

    def _fallback_probs(self, angles: np.ndarray) -> list[float]:
        amps = []
        for state in range(self.dim):
            acc = 1.0
            for i in range(self.n_qubits):
                bit = (state >> i) & 1
                theta = angles[i]
                acc *= math.cos(theta / 2.0) if bit == 0 else math.sin(theta / 2.0)
            amps.append(acc)
        probs = np.square(np.array(amps, dtype=np.float64))
        total = float(probs.sum()) or 1.0
        return [float(x / total) for x in probs.tolist()]

    def encode(self, text: str) -> list[float]:
        angles = self._angles_from_text(text)
        if self._qnode is None:
            probs = self._fallback_probs(angles)
        else:
            probs = [float(x) for x in self._qnode(angles).tolist()]
        return l2_normalize([float(np.float32(x)) for x in probs])
