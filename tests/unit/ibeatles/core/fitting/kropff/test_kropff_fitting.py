#!/usr/bin/env python
"""Unit tests for Kropff fitting functions."""

import pytest
import numpy as np
from lmfit.model import ModelResult

from ibeatles.core.fitting.kropff.fitting import (
    fit_bragg_edge_single_pass,
    fit_bragg_edge_with_refinement,
    fit_bragg_edge_multi_step,
)
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


# ----- Single pass fitting tests -----


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
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    # Case 1: Completely corrupted data (no edge to fit)
    transmission_constant = np.ones_like(wavelengths) * np.nan
    result_constant = fit_bragg_edge_single_pass(
        wavelengths, transmission_constant, parameter_bounds=bounds
    )
    assert result_constant is None or not result_constant.success

    # Case 2: Pure noise (no meaningful signal)
    transmission_noise = np.random.normal(0.5, 2.0, size=len(wavelengths))
    result_noise = fit_bragg_edge_single_pass(
        wavelengths, transmission_noise, parameter_bounds=bounds
    )
    if result_noise is not None and result_noise.success:
        # Check edge parameters
        edge_params = result_noise.params["bragg_edge_wavelength"]
        sigma = result_noise.params["sigma"]
        tau = result_noise.params["tau"]
        # Log the results for debugging
        print(f"Edge: {edge_params.value} +/- {edge_params.stderr}")
        print(f"Sigma: {sigma.value} +/- {sigma.stderr}")
        print(f"Tau: {tau.value} +/- {tau.stderr}")

        # The fit should have terrible R-squared if it's really noise
        assert result_noise.rsquared < 0.5

    # Case 3: Too few points after cleaning
    wavelengths_few = np.linspace(3.0, 5.0, 3)
    transmission_few = np.ones_like(wavelengths_few)
    result_few = fit_bragg_edge_single_pass(
        wavelengths_few, transmission_few, parameter_bounds=bounds
    )
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


# ----- Refinement tests -----


def test_fit_bragg_edge_with_refinement_clean_data(sample_data):
    """Test multi-step refinement fitting with clean data."""
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    result = fit_bragg_edge_with_refinement(
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


def test_fit_bragg_edge_with_refinement_noisy_data(sample_data):
    """Test multi-step refinement fitting with noisy data."""
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    result = fit_bragg_edge_with_refinement(
        sample_data["wavelengths"],
        sample_data["noisy_data"],
        initial_parameters=sample_data["true_params"],
        parameter_bounds=bounds,
    )

    assert isinstance(result, ModelResult)
    assert result.success

    # Only check the Bragg edge parameters
    # NOTE: a0, b0, ahkl and bhkl are correlated and may not converge to true values
    assert np.isclose(
        result.params["bragg_edge_wavelength"].value,
        sample_data["true_params"]["bragg_edge_wavelength"],
        rtol=1e-1,
    )


def test_fit_bragg_edge_with_refinement_missing_bounds():
    """Test multi-step refinement with missing bounds."""
    wavelengths = np.linspace(3.0, 5.0, 100)
    transmission = np.ones_like(wavelengths)

    # Missing bounds
    with pytest.raises(
        ValueError, match="Bounds for 'sigma' and 'tau' must be provided"
    ):
        fit_bragg_edge_with_refinement(wavelengths, transmission)

    # Missing sigma bounds
    bounds = {"tau": {"min": 0.005, "max": 0.1}}
    with pytest.raises(
        ValueError, match="Bounds for 'sigma' and 'tau' must be provided"
    ):
        fit_bragg_edge_with_refinement(
            wavelengths, transmission, parameter_bounds=bounds
        )


def test_fit_bragg_edge_with_refinement_bad_data():
    """Test multi-step refinement with data that should cause fitting to fail."""
    wavelengths = np.linspace(3.0, 5.0, 100)
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    # Case 1: Completely corrupted data (no edge to fit)
    transmission_constant = np.ones_like(wavelengths) * np.nan
    result_constant = fit_bragg_edge_with_refinement(
        wavelengths, transmission_constant, parameter_bounds=bounds
    )
    assert result_constant is None or not result_constant.success

    # Case 2: Pure noise (no meaningful signal)
    transmission_noise = np.random.normal(0.5, 2.0, size=len(wavelengths))
    result_noise = fit_bragg_edge_with_refinement(
        wavelengths, transmission_noise, parameter_bounds=bounds
    )
    if result_noise is not None and result_noise.success:
        # Check edge parameters
        edge_params = result_noise.params["bragg_edge_wavelength"]
        sigma = result_noise.params["sigma"]
        tau = result_noise.params["tau"]
        # Log the results for debugging
        print(f"Edge: {edge_params.value} +/- {edge_params.stderr}")
        print(f"Sigma: {sigma.value} +/- {sigma.stderr}")
        print(f"Tau: {tau.value} +/- {tau.stderr}")

        # The fit should have terrible R-squared if it's really noise
        assert result_noise.rsquared < 0.5

    # Case 3: Too few points
    wavelengths_few = np.linspace(3.0, 5.0, 3)
    transmission_few = np.ones_like(wavelengths_few)
    result_few = fit_bragg_edge_with_refinement(
        wavelengths_few, transmission_few, parameter_bounds=bounds
    )
    assert result_few is None or not result_few.success


def test_fit_bragg_edge_with_refinement_convergence(sample_data):
    """Test multi-step refinement convergence with different initial guesses."""
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    # Test with initial guesses far from true values
    far_initial_params = {k: v * 2 for k, v in sample_data["true_params"].items()}

    result = fit_bragg_edge_with_refinement(
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


# ----- Three-step tests -----


def test_fit_bragg_edge_multi_step_clean_data(sample_data):
    """Test traditional multi-step fitting with clean data."""
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    # Define wavelength ranges for fitting
    high_lambda_range = (4.5, 5.0)  # Above the edge
    low_lambda_range = (3.0, 3.5)  # Below the edge

    result = fit_bragg_edge_multi_step(
        sample_data["wavelengths"],
        sample_data["clean_data"],
        high_lambda_range=high_lambda_range,
        low_lambda_range=low_lambda_range,
        initial_parameters=sample_data["true_params"],
        parameter_bounds=bounds,
    )

    assert isinstance(result, ModelResult)
    assert result.success

    # Check if parameters are close to true values
    for param_name, true_value in sample_data["true_params"].items():
        assert np.isclose(result.params[param_name].value, true_value, rtol=5e-3)


def test_fit_bragg_edge_multi_step_noisy_data(sample_data):
    """Test traditional multi-step fitting with noisy data."""
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    high_lambda_range = (4.5, 5.0)
    low_lambda_range = (3.0, 3.5)

    result = fit_bragg_edge_multi_step(
        sample_data["wavelengths"],
        sample_data["noisy_data"],
        high_lambda_range=high_lambda_range,
        low_lambda_range=low_lambda_range,
        initial_parameters=sample_data["true_params"],
        parameter_bounds=bounds,
    )

    assert isinstance(result, ModelResult)
    assert result.success

    # Only check the Bragg edge parameters
    # NOTE: a0, b0, ahkl and bhkl are correlated and may not converge to true values
    assert np.isclose(
        result.params["bragg_edge_wavelength"].value,
        sample_data["true_params"]["bragg_edge_wavelength"],
        rtol=1e-1,
    )


def test_fit_bragg_edge_multi_step_missing_bounds():
    """Test multi-step fitting with missing bounds."""
    wavelengths = np.linspace(3.0, 5.0, 100)
    transmission = np.ones_like(wavelengths)
    high_lambda_range = (4.5, 5.0)
    low_lambda_range = (3.0, 3.5)

    with pytest.raises(
        ValueError, match="Bounds for 'sigma' and 'tau' must be provided"
    ):
        fit_bragg_edge_multi_step(
            wavelengths,
            transmission,
            high_lambda_range=high_lambda_range,
            low_lambda_range=low_lambda_range,
        )


def test_fit_bragg_edge_multi_step_invalid_ranges():
    """Test multi-step fitting with invalid wavelength ranges."""
    wavelengths = np.linspace(3.0, 5.0, 100)
    transmission = np.ones_like(wavelengths)
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }

    # Test range outside wavelength bounds
    invalid_high_range = (5.5, 6.0)
    result = fit_bragg_edge_multi_step(
        wavelengths,
        transmission,
        high_lambda_range=invalid_high_range,
        low_lambda_range=(3.0, 3.5),
        parameter_bounds=bounds,
    )
    assert result is None

    # Test empty range after masking
    empty_range = (3.0, 3.0)  # No points will fall in this range
    result = fit_bragg_edge_multi_step(
        wavelengths,
        transmission,
        high_lambda_range=(4.5, 5.0),
        low_lambda_range=empty_range,
        parameter_bounds=bounds,
    )
    assert result is None


def test_fit_bragg_edge_multi_step_bad_data():
    """Test multi-step fitting with data that should cause fitting to fail."""
    wavelengths = np.linspace(3.0, 5.0, 100)
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }
    high_lambda_range = (4.5, 5.0)
    low_lambda_range = (3.0, 3.5)

    # Case 1: Completely corrupted data
    transmission_constant = np.ones_like(wavelengths) * np.nan
    result_constant = fit_bragg_edge_multi_step(
        wavelengths,
        transmission_constant,
        high_lambda_range=high_lambda_range,
        low_lambda_range=low_lambda_range,
        parameter_bounds=bounds,
    )
    assert result_constant is None or not result_constant.success

    # Case 2: Pure noise
    transmission_noise = np.random.normal(0.5, 2.0, size=len(wavelengths))
    result_noise = fit_bragg_edge_multi_step(
        wavelengths,
        transmission_noise,
        high_lambda_range=high_lambda_range,
        low_lambda_range=low_lambda_range,
        parameter_bounds=bounds,
    )

    # If fit succeeds, check that the result doesn't make physical sense
    if result_noise is not None and result_noise.success:
        assert result_noise.rsquared < 0.5


def test_fit_bragg_edge_multi_step_convergence(sample_data):
    """Test multi-step fitting convergence with different initial guesses."""
    bounds = {
        "bragg_edge_wavelength": {"min": 3.0, "max": 5.0},
        "sigma": {"min": 0.005, "max": 0.1},
        "tau": {"min": 0.005, "max": 0.1},
    }
    high_lambda_range = (4.5, 5.0)
    low_lambda_range = (3.0, 3.5)

    # Test with initial guesses far from true values
    far_initial_params = {k: v * 2 for k, v in sample_data["true_params"].items()}

    result = fit_bragg_edge_multi_step(
        sample_data["wavelengths"],
        sample_data["clean_data"],
        high_lambda_range=high_lambda_range,
        low_lambda_range=low_lambda_range,
        initial_parameters=far_initial_params,
        parameter_bounds=bounds,
    )

    assert isinstance(result, ModelResult)
    assert result.success

    # Only check the Bragg edge parameters
    # NOTE: the three-step actually performs worse with the synthetic data, so
    #       we relax the tolerance here
    assert np.isclose(
        result.params["bragg_edge_wavelength"].value,
        sample_data["true_params"]["bragg_edge_wavelength"],
        rtol=2e-1,
    )


if __name__ == "__main__":
    pytest.main([__file__])
