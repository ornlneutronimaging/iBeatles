#!/usr/bin/env python
"""Unit tests for Kropff fitting functions."""

import pytest
import numpy as np
from lmfit.model import ModelResult

from ibeatles.core.fitting.kropff.fitting import fit_bragg_edge_single_pass
from ibeatles.core.fitting.utils import generate_synthetic_transmission
from ibeatles.core.fitting.kropff.models import kropff_transmission_model


@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    # Define true parameters
    true_params = {
        "a0": 0.15,
        "b0": 0.11,
        "a_hkl": 0.12,
        "b_hkl": 0.11,
        "bragg_edge_wavelength": 4.054,
        "sigma": 0.01,
        "tau": 0.02,
    }

    # Generate wavelength points
    wavelengths = np.linspace(3.0, 5.0, 100)

    # Generate data with different noise levels
    clean_data = kropff_transmission_model(wavelengths, **true_params)
    noisy_data = generate_synthetic_transmission(
        kropff_transmission_model, wavelengths, true_params, noise_level=0.01
    )[1]

    return {
        "wavelengths": wavelengths,
        "clean_data": clean_data,
        "noisy_data": noisy_data,
        "true_params": true_params,
    }


def test_fit_bragg_edge_single_pass_clean_data(sample_data):
    """Test fitting with clean data."""
    bounds = {
        "bragg_edge_wavelength": {
            "min": 3.0,
            "max": 5.0,
        },  # we should know the edge rough bounds
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    result = fit_bragg_edge_single_pass(
        sample_data["wavelengths"],
        sample_data["clean_data"],
        initial_parameters=sample_data["true_params"],
        parameter_bounds=bounds,
    )

    assert isinstance(result, ModelResult)
    assert result.success

    # Check if parameters are close to true values
    for param_name, true_value in sample_data["true_params"].items():
        assert np.isclose(result.params[param_name].value, true_value, rtol=5e-3)


def test_fit_bragg_edge_single_pass_noisy_data(sample_data):
    """Test fitting with noisy data."""
    bounds = {
        "bragg_edge_wavelength": {
            "min": 3.0,
            "max": 5.0,
        },  # we should know the edge rough bounds
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    result = fit_bragg_edge_single_pass(
        sample_data["wavelengths"],
        sample_data["noisy_data"],
        initial_parameters=sample_data["true_params"],
        parameter_bounds=bounds,
    )

    assert isinstance(result, ModelResult)
    assert result.success

    # Only check the Bragg edge parameters
    # NOTE: a0, b0, ahkl and bhkl are correlated and may not converge to true values, so we skip them
    #       plus, we only care about the Bragg edge position for this fitting function
    assert np.isclose(
        result.params["bragg_edge_wavelength"].value,
        sample_data["true_params"]["bragg_edge_wavelength"],
        rtol=1e-1,
    )


def test_fit_bragg_edge_single_pass_with_bounds(sample_data):
    """Test fitting with parameter bounds."""
    bounds = {
        "bragg_edge_wavelength": {
            "min": 3.0,
            "max": 5.0,
        },  # we should know the edge rough bounds
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    result = fit_bragg_edge_single_pass(
        sample_data["wavelengths"],
        sample_data["clean_data"],
        initial_parameters=sample_data["true_params"],
        parameter_bounds=bounds,
    )

    assert isinstance(result, ModelResult)
    assert result.success
    assert result.params["sigma"].value >= bounds["sigma"]["min"]
    assert result.params["sigma"].value <= bounds["sigma"]["max"]
    assert result.params["tau"].value >= bounds["tau"]["min"]
    assert result.params["tau"].value <= bounds["tau"]["max"]


def test_fit_bragg_edge_single_pass_bad_data():
    """Test fitting with data that should cause fitting to fail."""
    wavelengths = np.linspace(3.0, 5.0, 100)

    # Case 1: Completely corrupted data (no edge to fit)
    transmission_constant = np.ones_like(wavelengths) * np.nan
    result_constant = fit_bragg_edge_single_pass(wavelengths, transmission_constant)
    assert result_constant is None or not result_constant.success

    # Case 2: Pure noise (no meaningful signal)
    transmission_noise = np.random.normal(0.5, 0.5, size=len(wavelengths))
    result_noise = fit_bragg_edge_single_pass(wavelengths, transmission_noise)
    assert result_noise is None or not result_noise.success

    # Case 3: Too few points after cleaning
    wavelengths_few = np.linspace(3.0, 5.0, 3)
    transmission_few = np.ones_like(wavelengths_few)
    result_few = fit_bragg_edge_single_pass(wavelengths_few, transmission_few)
    assert result_few is None or not result_few.success


def test_fit_bragg_edge_single_pass_default_params(sample_data):
    """Test fitting with default parameters."""
    bounds = {
        "bragg_edge_wavelength": {
            "min": 3.0,
            "max": 5.0,
        },  # we should know the edge rough bounds
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    result = fit_bragg_edge_single_pass(
        sample_data["wavelengths"],
        sample_data["clean_data"],
        parameter_bounds=bounds,
    )

    assert isinstance(result, ModelResult)
    assert result.success


def test_fit_bragg_edge_single_pass_convergence(sample_data):
    """Test fitting convergence with different initial guesses."""
    # Test with initial guesses far from true values
    bounds = {
        "bragg_edge_wavelength": {
            "min": 3.0,
            "max": 5.0,
        },  # we should know the edge rough bounds
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }
    far_initial_params = {k: v * 2 for k, v in sample_data["true_params"].items()}

    result = fit_bragg_edge_single_pass(
        sample_data["wavelengths"],
        sample_data["clean_data"],
        initial_parameters=far_initial_params,
        parameter_bounds=bounds,
    )

    assert isinstance(result, ModelResult)
    assert result.success

    # Only check the Bragg edge parameters
    assert np.isclose(
        result.params["bragg_edge_wavelength"].value,
        sample_data["true_params"]["bragg_edge_wavelength"],
        rtol=1e-1,
    )


if __name__ == "__main__":
    pytest.main([__file__])
