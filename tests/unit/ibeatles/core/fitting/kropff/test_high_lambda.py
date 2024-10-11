#!/usr/bin/env python
import pytest
import numpy as np
from ibeatles.core.config import (
    PixelBinning,
    FittingCriteria,
    RejectionCriteria,
    ThresholdFinder,
)
from ibeatles.core.fitting.kropff.high_lambda import (
    fit_high_lambda,
    apply_high_lambda_fit,
)
from ibeatles.core.fitting.kropff.models import KropffBinData, KropffFittingParameters


def test_fit_high_lambda():
    # Create sample data
    xdata = np.linspace(1, 10, 100)
    ydata = np.exp(-(2 + 0.5 * xdata))  # a0=2, b0=0.5
    bin_data = KropffBinData(
        xaxis=xdata.tolist(),
        yaxis=ydata.tolist(),
        bin_coordinates={"x0": 0, "y0": 0, "x1": 10, "y1": 10},
        bragg_peak_threshold={"left": 1, "right": 10},
    )
    fitting_parameters = KropffFittingParameters(
        lambda_min=1,
        lambda_max=1,
        threshold_finder=ThresholdFinder(),
        fitting_criteria=FittingCriteria(),
        rejection_criteria=RejectionCriteria(),
        pixel_binning=PixelBinning(x0=0, y0=0, width=10, height=10, bins_size=1),
    )

    # Perform fit
    fit_results, x_fit, y_fit = fit_high_lambda(bin_data, fitting_parameters)

    # Check results
    assert "a0" in fit_results
    assert "b0" in fit_results
    assert abs(fit_results["a0"]["value"] - 2) < 0.1
    assert abs(fit_results["b0"]["value"] - 0.5) < 0.1
    assert len(x_fit) == len(xdata)
    assert len(y_fit) == len(ydata)


def test_fit_high_lambda_with_bad_data():
    # Create sample data with NaNs
    xdata = np.linspace(1, 10, 100)
    ydata = np.full_like(xdata, np.nan)  # All NaNs
    bin_data = KropffBinData(
        xaxis=xdata.tolist(),
        yaxis=ydata.tolist(),
        bin_coordinates={"x0": 0, "y0": 0, "x1": 10, "y1": 10},
        bragg_peak_threshold={"left": 1, "right": 10},
    )
    fitting_parameters = KropffFittingParameters(
        lambda_min=1,
        lambda_max=10,
        threshold_finder=ThresholdFinder(),
        fitting_criteria=FittingCriteria(),
        rejection_criteria=RejectionCriteria(),
        pixel_binning=PixelBinning(x0=0, y0=0, width=10, height=10, bins_size=1),
    )

    # Attempt fit and check for expected exception
    with pytest.raises(ValueError):
        fit_high_lambda(bin_data, fitting_parameters)


def test_apply_high_lambda_fit():
    # Create sample data for multiple bins
    bin_data_dict = {}
    for i in range(3):
        xdata = np.linspace(1, 10, 100)
        ydata = np.exp(-(2 + (0.5 + i * 0.1) * xdata))  # Varying b0
        bin_data_dict[f"bin_{i}"] = KropffBinData(
            xaxis=xdata.tolist(),
            yaxis=ydata.tolist(),
            bin_coordinates={"x0": 0, "y0": 0, "x1": 10, "y1": 10},
            bragg_peak_threshold={"left": 1, "right": 10},
        )

    fitting_parameters = KropffFittingParameters(
        lambda_min=1,
        lambda_max=10,
        threshold_finder=ThresholdFinder(),
        fitting_criteria=FittingCriteria(),
        rejection_criteria=RejectionCriteria(),
        pixel_binning=PixelBinning(x0=0, y0=0, width=10, height=10, bins_size=1),
    )

    # Apply fit to all bins
    results = apply_high_lambda_fit(bin_data_dict, fitting_parameters)

    # Check results
    assert len(results) == 3
    for i in range(3):
        assert f"bin_{i}" in results
        assert "a0" in results[f"bin_{i}"]
        assert "b0" in results[f"bin_{i}"]
        assert abs(results[f"bin_{i}"]["a0"]["value"] - 2) < 0.1
        assert abs(results[f"bin_{i}"]["b0"]["value"] - (0.5 + i * 0.1)) < 0.1
