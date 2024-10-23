#!/usr/bin/env python
"""Fitting routines for Kropff analysis"""

import logging
from typing import Dict, Optional
import numpy as np
from lmfit import Model
from lmfit.model import ModelResult

from ibeatles.core.fitting.kropff.models import (
    kropff_transmission_model,
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
