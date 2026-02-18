import numpy as np
import pytest

from infrastructure.quantum.swap_test_comparator import (
    SwapTestQuantumComparator,
    _next_power_of_two,
    _pad_and_normalize,
)


def test_next_power_of_two_basic():
    assert _next_power_of_two(1) == 1
    assert _next_power_of_two(2) == 2
    assert _next_power_of_two(3) == 4


def test_next_power_of_two_rejects_non_positive():
    with pytest.raises(ValueError):
        _next_power_of_two(0)

    with pytest.raises(ValueError):
        _next_power_of_two(-2)


def test_pad_and_normalize_padding_and_norm():
    vector = np.array([3.0, 4.0])
    padded = _pad_and_normalize(vector, 4)

    assert padded.size == 4
    assert np.isclose(np.linalg.norm(padded), 1.0)
    assert np.allclose(padded[2:], [0.0, 0.0])


def test_pad_and_normalize_rejects_invalid_inputs():
    with pytest.raises(ValueError):
        _pad_and_normalize(np.array([]), 2)

    projected = _pad_and_normalize(np.array([1.0, 2.0]), 1)
    assert projected.size == 1
    assert np.isclose(np.linalg.norm(projected), 1.0)

    with pytest.raises(ValueError):
        _pad_and_normalize(np.array([0.0, 0.0]), 2)

    with pytest.raises(ValueError):
        _pad_and_normalize(np.array([1.0]), 0)


def test_swap_test_similarity_bounds():
    comparator = SwapTestQuantumComparator()

    same = comparator.compare([1.0, 0.0], [1.0, 0.0])
    orthogonal = comparator.compare([1.0, 0.0], [0.0, 1.0])

    assert same >= 0.99
    assert orthogonal <= 0.01
