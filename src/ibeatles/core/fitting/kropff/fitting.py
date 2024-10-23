#!/usr/bin/env python
"""Fitting routines for Kropff analysis"""

import logging
from typing import Dict, Optional, Tuple
import numpy as np
from lmfit import Model
from lmfit.model import ModelResult

from ibeatles.core.fitting.kropff.models import (
    kropff_transmission_model,
    kropff_high_lambda_transmission,
    kropff_low_lambda_transmission,
)
from ibeatles.core.fitting.utils import remove_invalid_data_points


def fit_bragg_edge_single_pass(
    wavelengths: np.ndarray,
    transmission: np.ndarray,
    initial_parameters: Optional[Dict[str, float]] = None,
    parameter_bounds: Optional[Dict[str, Dict[str, float]]] = None,
) -> Optional[ModelResult]:
    """
    Fit Bragg edge using single pass approach.

    Parameters
    ----------
    wavelengths : np.ndarray
        Wavelength values
    transmission : np.ndarray
        Transmission values
    initial_parameters : Optional[Dict[str, float]], optional
        Initial parameter values for fitting. If None, default values will be used.
        Default is None.
    parameter_bounds : Optional[Dict[str, Dict[str, float]]], optional
        Dictionary containing parameter bounds.
        Format: {param_name: {"min": min_value, "max": max_value}}
        If a parameter or bound is not specified, no constraint will be applied.
        Default is None.

    Returns
    -------
    Optional[ModelResult]
        The lmfit ModelResult object containing all fit results and diagnostics.
        Returns None if fitting fails.
    """
    try:
        # Clean data
        wavelengths, transmission = remove_invalid_data_points(
            wavelengths, transmission
        )

        # Create model
        model = Model(kropff_transmission_model)

        # Set up parameters with default values if not provided
        if initial_parameters is None:
            initial_parameters = {
                "a0": 0.1,
                "b0": 0.1,
                "a_hkl": 0.1,
                "b_hkl": 0.1,
                "bragg_edge_wavelength": 4.0,
                "sigma": 0.01,
                "tau": 0.01,
            }

        # Create parameters
        params = model.make_params(**initial_parameters)

        # Apply bounds if provided
        if parameter_bounds:
            for param_name, bounds in parameter_bounds.items():
                if param_name in params:
                    if "min" in bounds:
                        params[param_name].min = bounds["min"]
                    if "max" in bounds:
                        params[param_name].max = bounds["max"]

        # Perform fit
        result = model.fit(transmission, params, wavelength=wavelengths)

        if result.success:
            logging.debug(f"Fit successful: {result.fit_report()}")
        else:
            logging.warning(f"Fit completed but may not be optimal: {result.message}")

        return result

    except Exception as e:
        logging.warning(f"Fitting failed: {str(e)}")
        return None


def fit_bragg_edge_with_refinement(
    wavelengths: np.ndarray,
    transmission: np.ndarray,
    initial_parameters: Optional[Dict[str, float]] = None,
    parameter_bounds: Optional[Dict[str, Dict[str, float]]] = None,
) -> Optional[ModelResult]:
    """
    Fit Bragg edge using multi-step refinement approach.
    This method performs fitting in three steps:
    1. Initial fit with all parameters
    2. Refine a0 and b0 while fixing other parameters
    3. Refine a_hkl and b_hkl while fixing other parameters
    4. Final refinement of edge parameters while fixing decay parameters

    Parameters
    ----------
    wavelengths : np.ndarray
        Wavelength values
    transmission : np.ndarray
        Transmission values
    initial_parameters : Optional[Dict[str, float]], optional
        Initial parameter values for fitting. If None, default values will be used.
        Default is None.
    parameter_bounds : Optional[Dict[str, Dict[str, float]]], optional
        Dictionary containing parameter bounds.
        Format: {param_name: {"min": min_value, "max": max_value}}
        Bounds for sigma and tau must be provided to ensure numerical stability.
        Default is None.

    Returns
    -------
    Optional[ModelResult]
        The lmfit ModelResult object containing all fit results and diagnostics.
        Returns None if fitting fails.
    """
    # Check if required bounds are provided, missing bounds means numerical instability, therefore
    # we raise an error to force user to provide bounds
    if (
        parameter_bounds is None
        or "sigma" not in parameter_bounds
        or "tau" not in parameter_bounds
    ):
        raise ValueError(
            "Bounds for 'sigma' and 'tau' must be provided to ensure numerical stability"
        )

    def setup_parameters(model, prev_result, vary_params, bounds=None):
        """Helper function to set up parameters for each step."""
        params = model.make_params()

        # If this is initial setup (no prev_result)
        if prev_result is None:
            for name, value in initial_parameters.items():
                params[name].set(value=value)
        else:
            for name, param in prev_result.params.items():
                params[name].set(value=param.value, vary=name in vary_params)

        # Apply bounds
        if bounds:
            for param_name, param_bounds in bounds.items():
                if param_name in params:
                    for bound_type, value in param_bounds.items():
                        setattr(params[param_name], bound_type, value)

        return params

    try:
        # Clean data
        wavelengths, transmission = remove_invalid_data_points(
            wavelengths, transmission
        )

        # Create model
        model = Model(kropff_transmission_model)

        # Set up initial parameters
        if initial_parameters is None:
            initial_parameters = {
                "a0": 0.1,
                "b0": 0.1,
                "a_hkl": 0.1,
                "b_hkl": 0.1,
                "bragg_edge_wavelength": 4.0,
                "sigma": 0.01,
                "tau": 0.01,
            }

        # Initial blind fit with bounds
        initial_params = setup_parameters(
            model,
            None,  # No previous result for initial fit
            vary_params=initial_parameters.keys(),
            bounds=parameter_bounds,
        )

        initial_result = model.fit(
            transmission,
            initial_params,
            wavelength=wavelengths,
        )

        if not initial_result.success:
            logging.warning("Initial fit failed")
            return None

        # Define refinement steps
        refinement_steps = [
            {"vary": ["a0", "b0"]},
            {"vary": ["a_hkl", "b_hkl"]},
            {"vary": ["bragg_edge_wavelength", "sigma", "tau"]},
        ]

        current_result = initial_result
        for step in refinement_steps:
            params = setup_parameters(
                model, current_result, step["vary"], parameter_bounds
            )
            current_result = model.fit(transmission, params, wavelength=wavelengths)

        if current_result.success:
            logging.debug(
                f"Multi-step refinement successful: {current_result.fit_report()}"
            )
        else:
            logging.warning(
                f"Multi-step refinement completed but may not be optimal: {current_result.message}"
            )

        return current_result

    except Exception as e:
        logging.warning(f"Multi-step refinement failed: {str(e)}")
        return None


def fit_bragg_edge_multi_step(
    wavelengths: np.ndarray,
    transmission: np.ndarray,
    high_lambda_range: Tuple[float, float],
    low_lambda_range: Tuple[float, float],
    initial_parameters: Optional[Dict[str, float]] = None,
    parameter_bounds: Optional[Dict[str, Dict[str, float]]] = None,
) -> Optional[ModelResult]:
    """
    Fit Bragg edge using traditional Kropff multi-step approach.

    Parameters
    ----------
    wavelengths : np.ndarray
        Wavelength values
    transmission : np.ndarray
        Transmission values
    high_lambda_range : Tuple[float, float]
        (min, max) wavelength range for high lambda fitting
    low_lambda_range : Tuple[float, float]
        (min, max) wavelength range for low lambda fitting
    initial_parameters : Optional[Dict[str, float]], optional
        Initial parameter values for fitting. If None, default values will be used.
        Default is None.
    parameter_bounds : Optional[Dict[str, Dict[str, float]]], optional
        Dictionary containing parameter bounds.
        Format: {param_name: {"min": min_value, "max": max_value}}
        Bounds for sigma and tau must be provided to ensure numerical stability.
        Default is None.

    Returns
    -------
    Optional[ModelResult]
        The lmfit ModelResult object containing all fit results and diagnostics.
        Returns None if fitting fails.
    """
    # Validate bounds first
    if (
        parameter_bounds is None
        or "sigma" not in parameter_bounds
        or "tau" not in parameter_bounds
    ):
        raise ValueError(
            "Bounds for 'sigma' and 'tau' must be provided to ensure numerical stability"
        )

    try:
        # Clean data
        wavelengths, transmission = remove_invalid_data_points(
            wavelengths, transmission
        )

        # Set up initial parameters if not provided
        if initial_parameters is None:
            initial_parameters = {
                "a0": 0.1,
                "b0": 0.1,
                "a_hkl": 0.1,
                "b_hkl": 0.1,
                "bragg_edge_wavelength": 4.0,
                "sigma": 0.01,
                "tau": 0.01,
            }

        # Step 1: Fit high lambda region
        high_lambda_mask = (wavelengths >= high_lambda_range[0]) & (
            wavelengths <= high_lambda_range[1]
        )
        high_lambda_model = Model(kropff_high_lambda_transmission)

        high_lambda_params = high_lambda_model.make_params(
            a0=initial_parameters["a0"], b0=initial_parameters["b0"]
        )

        if parameter_bounds and "a0" in parameter_bounds:
            high_lambda_params["a0"].min = parameter_bounds["a0"].get("min")
            high_lambda_params["a0"].max = parameter_bounds["a0"].get("max")
        if parameter_bounds and "b0" in parameter_bounds:
            high_lambda_params["b0"].min = parameter_bounds["b0"].get("min")
            high_lambda_params["b0"].max = parameter_bounds["b0"].get("max")

        high_lambda_result = high_lambda_model.fit(
            transmission[high_lambda_mask],
            high_lambda_params,
            wavelength=wavelengths[high_lambda_mask],
        )

        if not high_lambda_result.success:
            logging.warning("High lambda fit failed")
            return None

        # Step 2: Fit low lambda region using fixed high lambda parameters
        low_lambda_mask = (wavelengths >= low_lambda_range[0]) & (
            wavelengths <= low_lambda_range[1]
        )
        low_lambda_model = Model(kropff_low_lambda_transmission)

        low_lambda_params = low_lambda_model.make_params(
            a0=high_lambda_result.params["a0"].value,
            b0=high_lambda_result.params["b0"].value,
            a_hkl=initial_parameters["a_hkl"],
            b_hkl=initial_parameters["b_hkl"],
        )

        # Fix high lambda parameters
        low_lambda_params["a0"].vary = False
        low_lambda_params["b0"].vary = False

        if parameter_bounds and "a_hkl" in parameter_bounds:
            low_lambda_params["a_hkl"].min = parameter_bounds["a_hkl"].get("min")
            low_lambda_params["a_hkl"].max = parameter_bounds["a_hkl"].get("max")
        if parameter_bounds and "b_hkl" in parameter_bounds:
            low_lambda_params["b_hkl"].min = parameter_bounds["b_hkl"].get("min")
            low_lambda_params["b_hkl"].max = parameter_bounds["b_hkl"].get("max")

        low_lambda_result = low_lambda_model.fit(
            transmission[low_lambda_mask],
            low_lambda_params,
            wavelength=wavelengths[low_lambda_mask],
        )

        if not low_lambda_result.success:
            logging.warning("Low lambda fit failed")
            return None

        # Step 3: Final full profile fit with fixed decay parameters
        full_model = Model(kropff_transmission_model)

        final_params = full_model.make_params(
            a0=high_lambda_result.params["a0"].value,
            b0=high_lambda_result.params["b0"].value,
            a_hkl=low_lambda_result.params["a_hkl"].value,
            b_hkl=low_lambda_result.params["b_hkl"].value,
            bragg_edge_wavelength=initial_parameters["bragg_edge_wavelength"],
            sigma=initial_parameters["sigma"],
            tau=initial_parameters["tau"],
        )

        # Fix decay parameters
        final_params["a0"].vary = False
        final_params["b0"].vary = False
        final_params["a_hkl"].vary = False
        final_params["b_hkl"].vary = False

        # Apply bounds for edge parameters
        for param_name in ["bragg_edge_wavelength", "sigma", "tau"]:
            if parameter_bounds and param_name in parameter_bounds:
                if "min" in parameter_bounds[param_name]:
                    final_params[param_name].min = parameter_bounds[param_name]["min"]
                if "max" in parameter_bounds[param_name]:
                    final_params[param_name].max = parameter_bounds[param_name]["max"]

        final_result = full_model.fit(
            transmission, final_params, wavelength=wavelengths
        )

        if final_result.success:
            logging.debug(f"Multi-step fit successful: {final_result.fit_report()}")
        else:
            logging.warning(
                f"Multi-step fit completed but may not be optimal: {final_result.message}"
            )

        return final_result

    except Exception as e:
        logging.warning(f"Multi-step fit failed: {str(e)}")
        return None
