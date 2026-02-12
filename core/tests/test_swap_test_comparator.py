import numpy as np
import pytest

from infrastructure.quantum.swap_test_comparator import (
    SwapTestQuantumComparator,
    _next_power_of_two,
    _pad_and_normalize,
)


def test_next_power_of_two():
    assert _next_power_of_two(1) == 1
    assert _next_power_of_two(2) == 2
    assert _next_power_of_two(3) == 4
    assert _next_power_of_two(7) == 8
    assert _next_power_of_two(8) == 8
    assert _next_power_of_two(9) == 16


def test_next_power_of_two_rejects_invalid_values():
    with pytest.raises(TypeError, match="integer"):
        _next_power_of_two(1.5)
    with pytest.raises(ValueError, match="positive"):
        _next_power_of_two(0)
    with pytest.raises(ValueError, match="positive"):
        _next_power_of_two(-3)


def test_pad_and_normalize_pads_and_normalizes():
    vector = np.array([3.0, 4.0])
    result = _pad_and_normalize(vector, 4)

    assert result.size == 4
    assert np.isclose(np.linalg.norm(result), 1.0)
    assert np.allclose(result[2:], [0.0, 0.0])


def test_pad_and_normalize_raises_when_target_smaller():
    vector = np.array([1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="Target length smaller"):
        _pad_and_normalize(vector, 2)


def test_pad_and_normalize_raises_on_zero_norm():
    vector = np.array([0.0, 0.0])
    with pytest.raises(ValueError, match="Vector norm is zero"):
        _pad_and_normalize(vector, 2)


def test_pad_and_normalize_rejects_invalid_inputs():
    with pytest.raises(ValueError, match="required"):
        _pad_and_normalize(None, 2)
    with pytest.raises(TypeError, match="integer"):
        _pad_and_normalize(np.array([1.0]), 2.5)
    with pytest.raises(ValueError, match="positive"):
        _pad_and_normalize(np.array([1.0]), 0)
    with pytest.raises(ValueError, match="non-empty"):
        _pad_and_normalize(np.array([]), 2)


def test_swap_test_rejects_empty_vectors():
    comparator = SwapTestQuantumComparator()
    with pytest.raises(ValueError, match="non-empty"):
        comparator.compare([], [1.0])
    with pytest.raises(ValueError, match="non-empty"):
        comparator.compare([1.0], [])


def test_swap_test_rejects_none_vector():
    comparator = SwapTestQuantumComparator()
    with pytest.raises(TypeError):
        comparator.compare(None, [1.0, 0.0])


def test_swap_test_similarity_identical_vectors():
    comparator = SwapTestQuantumComparator()
    similarity = comparator.compare([1.0, 2.0, 3.0], [1.0, 2.0, 3.0])
    assert similarity == pytest.approx(1.0, abs=1e-6)


def test_swap_test_similarity_orthogonal_vectors():
    comparator = SwapTestQuantumComparator()
    similarity = comparator.compare([1.0, 0.0], [0.0, 1.0])
    assert similarity == pytest.approx(0.0, abs=1e-6)


def test_swap_test_rejects_zero_vector():
    comparator = SwapTestQuantumComparator()
    with pytest.raises(ValueError, match="Vector norm is zero"):
        comparator.compare([0.0, 0.0], [1.0, 0.0])


def test_swap_test_large_vectors_runs_and_returns_valid_score():
    comparator = SwapTestQuantumComparator()
    vector_a = list(range(1, 35))
    vector_b = list(range(1, 50))

    similarity = comparator.compare(vector_a, vector_b)

    assert 0.0 <= similarity <= 1.0
