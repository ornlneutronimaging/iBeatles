#!/usr/bin/env python
"""Bragg peak detection, high lambda"""

import numpy as np
from lmfit import Model
from typing import Tuple, Dict, Any
from ibeatles.core.fitting.kropff.fitting_functions import (
    kropff_high_lambda_transmission,
    kropff_high_lambda_attenuation,
)
from ibeatles.core.fitting.kropff.models import KropffBinData, KropffFittingParameters


def fit_high_lambda(
    bin_data: KropffBinData, fitting_parameters: KropffFittingParameters
) -> Tuple[Dict[str, Any], np.ndarray, np.ndarray]:
    """
    Perform high lambda fitting for Kropff analysis.

    Parameters:
    -----------
    bin_data : KropffBinData
        The bin data to fit, containing x and y axis data.
    fitting_parameters : KropffFittingParameters
        The fitting parameters, including initial guesses and constraints.

    Returns:
    --------
    Tuple[Dict[str, Any], np.ndarray, np.ndarray]
        A tuple containing:
        - A dictionary with the fitted parameters (a0, b0) and their errors.
        - The x-axis values used for fitting.
        - The fitted y-axis values.

    Raises:
    -------
    ValueError
        If the fitting fails or produces invalid results.
    """
    # Extract data from input models
    xdata = np.array(bin_data.xaxis)
    ydata = -np.log(np.array(bin_data.yaxis))  # Convert to attenuation

    # Create lmfit Model
    # NOTE: Transmission -> Attenuation will reduce the complexity of fitting
    #       from exponential to linear, hence we use the attenuation function
    #       for fitting, but the transmission function for plotting.
    model = Model(kropff_high_lambda_attenuation, independent_vars=["lda"])

    # Set up parameters with initial guesses
    # NOTE: we explicitly specify a0 and b0 to be the fitting parameters, in case
    #       the implicit behavior of lmfit changes in the future.
    params = model.make_params(
        a0=fitting_parameters.lambda_min, b0=fitting_parameters.lambda_max
    )

    # Perform the fit
    try:
        result = model.fit(ydata, params, lda=xdata)
    except Exception as e:
        raise ValueError(f"Fitting failed: {str(e)}")

    # Check if the fit was successful
    if not result.success:
        raise ValueError("Fitting did not converge")

    # Extract fitted parameters and errors
    a0_value = result.params["a0"].value
    a0_error = result.params["a0"].stderr
    b0_value = result.params["b0"].value
    b0_error = result.params["b0"].stderr

    # Calculate fitted y values
    y_fit = kropff_high_lambda_transmission(xdata, a0_value, b0_value)

    # Prepare results
    fit_results = {
        "a0": {"value": a0_value, "error": a0_error},
        "b0": {"value": b0_value, "error": b0_error},
    }

    return fit_results, xdata, y_fit


def apply_high_lambda_fit(
    bin_data_dict: Dict[str, KropffBinData], fitting_parameters: KropffFittingParameters
) -> Dict[str, Dict[str, Any]]:
    """
    Apply high lambda fitting to multiple bins.

    Parameters:
    -----------
    bin_data_dict : Dict[str, KropffBinData]
        A dictionary of bin data, keyed by bin identifier.
    fitting_parameters : KropffFittingParameters
        The fitting parameters to use for all bins.

    Returns:
    --------
    Dict[str, Dict[str, Any]]
        A dictionary of fitting results for each bin, keyed by bin identifier.
    """
    results = {}
    for bin_id, bin_data in bin_data_dict.items():
        try:
            fit_result, _, _ = fit_high_lambda(bin_data, fitting_parameters)
            results[bin_id] = fit_result
        except ValueError as e:
            # we catch failed fitting and store the error message, but continue
            results[bin_id] = {"error": str(e)}

    return results
