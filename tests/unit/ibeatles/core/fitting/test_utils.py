#!/usr/bin/env python3
"""Unit tests for fitting utility functions."""

import pytest
import numpy as np
import logging
from ibeatles.core.fitting.utils import (
    remove_invalid_data_points,
    generate_synthetic_transmission,
)


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


def test_generate_synthetic_transmission():
    # Define a simple model function for testing
    def test_model(wavelengths, a, b):
        return a * wavelengths + b

    # Set up test parameters
    wavelengths = np.linspace(1.0, 10.0, 1000)
    true_params = {"a": 0.5, "b": 1.0}
    noise_level = 0.01

    # Test case 1: Basic functionality
    def test_basic_functionality():
        wavelengths_out, noisy_transmission = generate_synthetic_transmission(
            test_model, wavelengths, true_params, noise_level
        )

        assert np.array_equal(wavelengths, wavelengths_out)
        assert len(noisy_transmission) == len(wavelengths)

        ideal_transmission = test_model(wavelengths, **true_params)
        assert np.allclose(noisy_transmission, ideal_transmission, atol=0.1)

    # Test case 2: Noise level
    def test_noise_level():
        _, noisy_transmission = generate_synthetic_transmission(
            test_model, wavelengths, true_params, noise_level
        )

        ideal_transmission = test_model(wavelengths, **true_params)
        actual_noise = noisy_transmission - ideal_transmission
        assert 0.8 * noise_level <= np.std(actual_noise) <= 1.2 * noise_level

    # Test case 3: Zero noise
    def test_zero_noise():
        _, noisy_transmission = generate_synthetic_transmission(
            test_model, wavelengths, true_params, 0
        )

        ideal_transmission = test_model(wavelengths, **true_params)
        np.testing.assert_allclose(noisy_transmission, ideal_transmission)

    # Test case 4: Different noise levels
    @pytest.mark.parametrize("noise", [0.001, 0.1, 0.5])
    def test_different_noise_levels(noise):
        _, noisy_transmission = generate_synthetic_transmission(
            test_model, wavelengths, true_params, noise
        )

        ideal_transmission = test_model(wavelengths, **true_params)
        actual_noise = noisy_transmission - ideal_transmission
        assert 0.8 * noise <= np.std(actual_noise) <= 1.2 * noise

    # Test case 5: Error handling
    def test_error_handling():
        with pytest.raises(TypeError):
            generate_synthetic_transmission("not a function", wavelengths, true_params)

        with pytest.raises(ValueError):
            generate_synthetic_transmission(test_model, wavelengths, true_params, -1)

    # Run all test cases
    test_basic_functionality()
    test_noise_level()
    test_zero_noise()
    test_different_noise_levels(0.001)
    test_different_noise_levels(0.1)
    test_different_noise_levels(0.5)
    test_error_handling()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
