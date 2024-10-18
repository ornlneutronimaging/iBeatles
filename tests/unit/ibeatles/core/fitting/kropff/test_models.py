#!/usr/bin/env python
import numpy as np
import pytest
from ibeatles.core.fitting.kropff.models import (
    kropff_high_lambda_transmission,
    kropff_low_lambda_transmission,
    bragg_edge_function,
    kropff_transmission_model,
)


def test_kropff_high_lambda_transmission():
    wavelength = np.array([1.0, 2.0, 3.0])
    a0, b0 = 0.1, 0.2
    expected = np.exp(-(0.1 + 0.2 * wavelength))
    np.testing.assert_allclose(
        kropff_high_lambda_transmission(wavelength, a0, b0), expected
    )


def test_kropff_low_lambda_transmission():
    wavelength = np.array([1.0, 2.0, 3.0])
    a0, b0, a_hkl, b_hkl = 0.1, 0.2, 0.3, 0.4
    expected = np.exp(-(0.1 + 0.2 * wavelength) - (0.3 + 0.4 * wavelength))
    np.testing.assert_allclose(
        kropff_low_lambda_transmission(wavelength, a0, b0, a_hkl, b_hkl), expected
    )


def test_bragg_edge_function():
    wavelength = np.array([3.9, 4.0, 4.1])
    bragg_edge_wavelength = 4.0
    sigma, tau = 0.01, 0.02
    result = bragg_edge_function(wavelength, bragg_edge_wavelength, sigma, tau)
    val_at_edge = 0.22832758914924972  # the edge is smaller than 0.5 because we skewed the ERFC function
    assert len(result) == 3
    assert 0 <= result[0] < val_at_edge  # Before edge
    assert result[1] == pytest.approx(val_at_edge, abs=1e-6)  # At edge
    assert val_at_edge < result[2] <= 1  # After edge


def test_kropff_transmission_model():
    wavelength = np.array([3.9, 4.0, 4.1])
    a0, b0, a_hkl, b_hkl = 0.1, 0.2, 0.3, 0.4
    bragg_edge_wavelength = 4.0
    sigma, tau = 0.01, 0.02
    result = kropff_transmission_model(
        wavelength, a0, b0, a_hkl, b_hkl, bragg_edge_wavelength, sigma, tau
    )
    assert len(result) == 3
    assert (
        0 < result[0] < result[1] < result[2] < 1
    )  # Transmission should increase across the edge


@pytest.mark.parametrize(
    "func",
    [
        kropff_high_lambda_transmission,
        kropff_low_lambda_transmission,
        bragg_edge_function,
        kropff_transmission_model,
    ],
)
def test_function_input_types(func):
    with pytest.raises(TypeError):
        func("not an array", *([1.0] * (func.__code__.co_argcount - 1)))


def test_kropff_transmission_model_integration():
    wavelength = np.linspace(3.0, 5.0, 200)
    a0, b0, a_hkl, b_hkl = 0.15, 0.11, 0.12, 0.11
    bragg_edge_wavelength = 4.054
    sigma, tau = 0.01, 0.02
    result = kropff_transmission_model(
        wavelength, a0, b0, a_hkl, b_hkl, bragg_edge_wavelength, sigma, tau
    )

    # Check that the result is within expected transmission range
    assert np.all((0 < result) & (result < 1))

    # Find the index of the Bragg edge
    edge_index = np.argmin(np.abs(wavelength - bragg_edge_wavelength))

    # Check that transmission decreases before the edge
    assert np.all(np.diff(result[: edge_index - 5]) < 0)

    # Check for the sharp increase at the edge
    assert result[edge_index + 1] > result[edge_index - 1]

    # Check that the rate of decrease is slower after the edge
    pre_edge_slope = np.mean(np.diff(result[:20]))
    post_edge_slope = np.mean(np.diff(result[-20:]))
    assert abs(post_edge_slope) < abs(pre_edge_slope)


if __name__ == "__main__":
    pytest.main([__file__])
