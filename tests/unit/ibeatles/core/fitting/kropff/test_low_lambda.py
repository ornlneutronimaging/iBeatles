#!/usr/bin/env python3
"""Unit tests for low_lambda module."""

import pytest
import numpy as np
from ibeatles.core.fitting.kropff.low_lambda import fit_low_lambda, apply_low_lambda_fit
from ibeatles.core.fitting.kropff.models import KropffBinData, KropffFittingParameters
from ibeatles.core.config import (
    ThresholdFinder,
    FittingCriteria,
    RejectionCriteria,
    PixelBinning,
)


def create_sample_data():
    """Create sample data for testing."""
    x = np.linspace(1, 10, 100)
    y = np.exp(-(2 + 0.5 * x + 1 + 0.3 * x))  # a0=2, b0=0.5, ahkl=1, bhkl=0.3
    return x, y


def test_fit_low_lambda():
    """Test the fit_low_lambda function."""
    x, y = create_sample_data()
    bin_data = KropffBinData(
        xaxis=x.tolist(),
        yaxis=y.tolist(),
        bin_coordinates={"x0": 0, "y0": 0, "x1": 10, "y1": 10},
        bragg_peak_threshold={"left": 1, "right": 10},
    )
    fitting_parameters = KropffFittingParameters(
        lambda_min=0.0,
        lambda_max=0.0,
        threshold_finder=ThresholdFinder(),
        fitting_criteria=FittingCriteria(),
        rejection_criteria=RejectionCriteria(),
        pixel_binning=PixelBinning(x0=0, y0=0, width=10, height=10, bins_size=1),
    )
    high_lambda_results = {
        "a0": {"value": 2.0, "error": 0.1},
        "b0": {"value": 0.5, "error": 0.05},
    }

    fit_results, x_fit, y_fit = fit_low_lambda(
        bin_data, fitting_parameters, high_lambda_results
    )

    assert "ahkl" in fit_results
    assert "bhkl" in fit_results
    assert abs(fit_results["ahkl"]["value"] - 1) < 0.1
    assert abs(fit_results["bhkl"]["value"] - 0.3) < 0.1
    assert len(x_fit) == len(x)
    assert len(y_fit) == len(y)


def test_fit_low_lambda_with_invalid_data():
    """Test fit_low_lambda with invalid data points."""
    x, y = create_sample_data()
    x[10:20] = np.nan  # Introduce some NaN values
    y[30:40] = np.inf  # Introduce some inf values

    bin_data = KropffBinData(
        xaxis=x.tolist(),
        yaxis=y.tolist(),
        bin_coordinates={"x0": 0, "y0": 0, "x1": 10, "y1": 10},
        bragg_peak_threshold={"left": 1, "right": 10},
    )
    fitting_parameters = KropffFittingParameters(
        lambda_min=0.5,
        lambda_max=1.5,
        threshold_finder=ThresholdFinder(),
        fitting_criteria=FittingCriteria(),
        rejection_criteria=RejectionCriteria(),
        pixel_binning=PixelBinning(x0=0, y0=0, width=10, height=10, bins_size=1),
    )
    high_lambda_results = {
        "a0": {"value": 2.0, "error": 0.1},
        "b0": {"value": 0.5, "error": 0.05},
    }

    fit_results, x_fit, y_fit = fit_low_lambda(
        bin_data, fitting_parameters, high_lambda_results
    )

    assert len(x_fit) < len(x)  # Some data points should have been removed
    assert len(y_fit) < len(y)


def test_apply_low_lambda_fit():
    """Test the apply_low_lambda_fit function."""
    x, y = create_sample_data()
    bin_data_dict = {
        "bin1": KropffBinData(
            xaxis=x.tolist(),
            yaxis=y.tolist(),
            bin_coordinates={"x0": 0, "y0": 0, "x1": 10, "y1": 10},
            bragg_peak_threshold={"left": 1, "right": 10},
        ),
        "bin2": KropffBinData(
            xaxis=x.tolist(),
            yaxis=(y * 1.1).tolist(),  # Slightly different data
            bin_coordinates={"x0": 10, "y0": 0, "x1": 20, "y1": 10},
            bragg_peak_threshold={"left": 1, "right": 10},
        ),
    }
    fitting_parameters = KropffFittingParameters(
        lambda_min=0.5,
        lambda_max=1.5,
        threshold_finder=ThresholdFinder(),
        fitting_criteria=FittingCriteria(),
        rejection_criteria=RejectionCriteria(),
        pixel_binning=PixelBinning(x0=0, y0=0, width=20, height=10, bins_size=1),
    )
    high_lambda_results = {
        "bin1": {
            "a0": {"value": 2.0, "error": 0.1},
            "b0": {"value": 0.5, "error": 0.05},
        },
        "bin2": {
            "a0": {"value": 2.2, "error": 0.1},
            "b0": {"value": 0.55, "error": 0.05},
        },
    }

    results = apply_low_lambda_fit(
        bin_data_dict, fitting_parameters, high_lambda_results
    )

    assert "bin1" in results
    assert "bin2" in results
    assert "ahkl" in results["bin1"]
    assert "bhkl" in results["bin1"]
    assert "ahkl" in results["bin2"]
    assert "bhkl" in results["bin2"]


def test_apply_low_lambda_fit_with_error():
    """Test apply_low_lambda_fit with a bin that causes an error."""
    x, y = create_sample_data()
    bin_data_dict = {
        "bin1": KropffBinData(
            xaxis=x.tolist(),
            yaxis=y.tolist(),
            bin_coordinates={"x0": 0, "y0": 0, "x1": 10, "y1": 10},
            bragg_peak_threshold={"left": 1, "right": 10},
        ),
        "bin2": KropffBinData(
            xaxis=x.tolist(),
            yaxis=[np.nan] * len(y),  # This should cause an error
            bin_coordinates={"x0": 10, "y0": 0, "x1": 20, "y1": 10},
            bragg_peak_threshold={"left": 1, "right": 10},
        ),
    }
    fitting_parameters = KropffFittingParameters(
        lambda_min=0.5,
        lambda_max=1.5,
        threshold_finder=ThresholdFinder(),
        fitting_criteria=FittingCriteria(),
        rejection_criteria=RejectionCriteria(),
        pixel_binning=PixelBinning(x0=0, y0=0, width=20, height=10, bins_size=1),
    )
    high_lambda_results = {
        "bin1": {
            "a0": {"value": 2.0, "error": 0.1},
            "b0": {"value": 0.5, "error": 0.05},
        },
        "bin2": {
            "a0": {"value": 2.2, "error": 0.1},
            "b0": {"value": 0.55, "error": 0.05},
        },
    }

    results = apply_low_lambda_fit(
        bin_data_dict, fitting_parameters, high_lambda_results
    )

    assert "bin1" in results
    assert "bin2" in results
    assert "ahkl" in results["bin1"]
    assert "bhkl" in results["bin1"]
    assert "error" in results["bin2"]


if __name__ == "__main__":
    pytest.main([__file__])
