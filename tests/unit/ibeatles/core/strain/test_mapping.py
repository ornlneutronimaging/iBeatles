#!/usr/bin/env python
"""Unit tests for strain mapping functions."""

import pytest
import numpy as np
from lmfit import Parameters, Model
from lmfit.model import ModelResult

from ibeatles.core.strain.mapping import calculate_strain_mapping


@pytest.fixture
def mock_fit_results():
    """Create mock fitting results."""

    def create_mock_result(
        wavelength: float, wavelength_error: float, rsquared: float
    ) -> ModelResult:
        # Create minimal Parameters with required attributes
        params = Parameters()
        params.add("bragg_edge_wavelength", value=wavelength)

        # Set the standard error manually after adding the parameter
        if wavelength_error is not None:
            params["bragg_edge_wavelength"].stderr = wavelength_error

        # Create dummy model (needed for ModelResult)
        model = Model(lambda x: x)

        # Create ModelResult with minimal required attributes
        result = ModelResult(
            model, params, data=np.array([1.0]), weights=np.array([1.0])
        )

        # Set additional attributes
        result.rsquared = rsquared
        result.best_values = {"bragg_edge_wavelength": wavelength}
        result.best_fit = np.array([1.0])  # Dummy data for best_fit

        return result

    # Create dictionary of test results
    results = {
        "good_fit": create_mock_result(4.0, 0.01, 0.95),
        "poor_fit": create_mock_result(4.1, 0.01, 0.7),
        "no_error": create_mock_result(4.2, None, 0.9),
        "failed_fit": None,
    }

    return results


def test_strain_calculation(mock_fit_results):
    """Test strain calculation with various fit results."""
    d0 = 2.0  # reference d-spacing
    strain_results = calculate_strain_mapping(
        fit_results=mock_fit_results, d0=d0, quality_threshold=0.8
    )

    # Check number of results (should exclude poor_fit and failed_fit)
    assert len(strain_results) == 2
    assert "poor_fit" not in strain_results
    assert "failed_fit" not in strain_results

    # Check good fit results
    good_result = strain_results["good_fit"]
    d_spacing = 4.0 / 2.0  # wavelength/2
    expected_strain = (d_spacing - d0) / d0
    expected_error = 0.01 / (2.0 * d0)

    assert good_result["strain"] == pytest.approx(expected_strain)
    assert good_result["error"] == pytest.approx(expected_error)
    assert good_result["quality"] == pytest.approx(0.95)

    # Check result with no error
    no_error_result = strain_results["no_error"]
    assert no_error_result["error"] is None


def test_strain_calculation_quality_threshold(mock_fit_results):
    """Test quality threshold filtering."""
    strain_results = calculate_strain_mapping(
        fit_results=mock_fit_results,
        d0=2.0,
        quality_threshold=0.6,  # Lower threshold to include poor_fit
    )

    assert len(strain_results) == 3
    assert "poor_fit" in strain_results


def test_empty_results():
    """Test handling of empty or all-failed fits."""
    empty_results = {}
    strain_results = calculate_strain_mapping(fit_results=empty_results, d0=2.0)
    assert len(strain_results) == 0

    failed_results = {"bin1": None, "bin2": None}
    strain_results = calculate_strain_mapping(fit_results=failed_results, d0=2.0)
    assert len(strain_results) == 0


if __name__ == "__main__":
    pytest.main(["-v", __file__])
