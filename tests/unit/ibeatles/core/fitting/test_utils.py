#!/usr/bin/env python3
"""Unit tests for fitting utility functions."""

import pytest
import numpy as np
import logging
from ibeatles.core.fitting.utils import remove_invalid_data_points


def test_remove_invalid_data_points_no_invalid():
    """Test with no invalid data points."""
    x = np.array([1, 2, 3, 4, 5])
    y = np.array([1, 4, 9, 16, 25])
    x_clean, y_clean = remove_invalid_data_points(x, y)
    np.testing.assert_array_equal(x_clean, x)
    np.testing.assert_array_equal(y_clean, y)


def test_remove_invalid_data_points_with_nan():
    """Test with NaN values."""
    x = np.array([1, 2, np.nan, 4, 5])
    y = np.array([1, 4, 9, np.nan, 25])
    x_clean, y_clean = remove_invalid_data_points(x, y)
    np.testing.assert_array_equal(x_clean, np.array([1, 2, 5]))
    np.testing.assert_array_equal(y_clean, np.array([1, 4, 25]))


def test_remove_invalid_data_points_with_inf():
    """Test with infinite values."""
    x = np.array([1, 2, np.inf, 4, 5])
    y = np.array([1, 4, 9, -np.inf, 25])
    x_clean, y_clean = remove_invalid_data_points(x, y)
    np.testing.assert_array_equal(x_clean, np.array([1, 2, 5]))
    np.testing.assert_array_equal(y_clean, np.array([1, 4, 25]))


def test_remove_invalid_data_points_all_invalid():
    """Test with all invalid data points."""
    x = np.array([np.nan, np.inf, np.nan])
    y = np.array([np.inf, np.nan, np.inf])
    x_clean, y_clean = remove_invalid_data_points(x, y)
    assert len(x_clean) == 0
    assert len(y_clean) == 0


def test_remove_invalid_data_points_mixed():
    """Test with a mix of valid and invalid data points."""
    x = np.array([1, np.nan, 3, np.inf, 5])
    y = np.array([np.inf, 4, np.nan, 16, 25])
    x_clean, y_clean = remove_invalid_data_points(x, y)
    np.testing.assert_array_equal(x_clean, np.array([5]))
    np.testing.assert_array_equal(y_clean, np.array([25]))


def test_remove_invalid_data_points_warning(caplog):
    """Test that a warning is logged when data points are removed."""
    x = np.array([1, np.nan, 3, np.inf, 5])
    y = np.array([1, 4, np.nan, 16, 25])

    with caplog.at_level(logging.WARNING):
        remove_invalid_data_points(x, y)

    assert "Removed 3 corrupted data point(s) from the input." in caplog.text


def test_remove_invalid_data_points_different_shapes():
    """Test with input arrays of different shapes."""
    x = np.array([1, 2, 3])
    y = np.array([1, 2, 3, 4])
    with pytest.raises(ValueError):
        remove_invalid_data_points(x, y)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
