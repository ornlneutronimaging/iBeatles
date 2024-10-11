#!/usr/bin/env python
"""Bragg peak detection, low lambda"""

import numpy as np
from lmfit import Model, Parameter
from typing import Tuple, Dict, Any
from ibeatles.core.fitting.kropff.fitting_functions import (
    kropff_low_lambda_transmission,
    kropff_low_lambda_attenuation,
)
from ibeatles.core.fitting.kropff.models import KropffBinData, KropffFittingParameters
from ibeatles.core.fitting.utils import remove_invalid_data_points


def fit_low_lambda(
    bin_data: KropffBinData,
    fitting_parameters: KropffFittingParameters,
    high_lambda_results: Dict[str, Dict[str, float]],
) -> Tuple[Dict[str, Any], np.ndarray, np.ndarray]:
    """
    Perform low lambda fitting for Kropff analysis.

    Parameters:
    -----------
    bin_data : KropffBinData
        The bin data to fit, containing x and y axis data.
    fitting_parameters : KropffFittingParameters
        The fitting parameters, including initial guesses and constraints.
    high_lambda_results : Dict[str, Dict[str, float]]
        Results from the high lambda fit, containing 'a0' and 'b0' values.

    Returns:
    --------
    Tuple[Dict[str, Any], np.ndarray, np.ndarray]
        A tuple containing:
        - A dictionary with the fitted parameters (ahkl, bhkl) and their errors.
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

    # Remove NaN or inf values
    xdata, ydata = remove_invalid_data_points(xdata, ydata)

    # Extract high lambda results
    a0 = high_lambda_results["a0"]["value"]
    b0 = high_lambda_results["b0"]["value"]

    # Create lmfit Model
    model = Model(kropff_low_lambda_attenuation, independent_vars=["lda"])

    # Set up parameters with initial guesses
    params = model.make_params(
        a0=Parameter("a0", value=a0, vary=False),
        b0=Parameter("b0", value=b0, vary=False),
        ahkl=fitting_parameters.lambda_min,
        bhkl=fitting_parameters.lambda_max,
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
    ahkl_value = result.params["ahkl"].value
    ahkl_error = result.params["ahkl"].stderr
    bhkl_value = result.params["bhkl"].value
    bhkl_error = result.params["bhkl"].stderr

    # Calculate fitted y values
    y_fit = kropff_low_lambda_transmission(xdata, a0, b0, ahkl_value, bhkl_value)

    # Prepare results
    fit_results = {
        "ahkl": {"value": ahkl_value, "error": ahkl_error},
        "bhkl": {"value": bhkl_value, "error": bhkl_error},
    }

    return fit_results, xdata, y_fit


def apply_low_lambda_fit(
    bin_data_dict: Dict[str, KropffBinData],
    fitting_parameters: KropffFittingParameters,
    high_lambda_results: Dict[str, Dict[str, Dict[str, float]]],
) -> Dict[str, Dict[str, Any]]:
    """
    Apply low lambda fitting to multiple bins.

    Parameters:
    -----------
    bin_data_dict : Dict[str, KropffBinData]
        A dictionary of bin data, keyed by bin identifier.
    fitting_parameters : KropffFittingParameters
        The fitting parameters to use for all bins.
    high_lambda_results : Dict[str, Dict[str, Dict[str, float]]]
        Results from the high lambda fit for all bins.

    Returns:
    --------
    Dict[str, Dict[str, Any]]
        A dictionary of fitting results for each bin, keyed by bin identifier.
    """
    results = {}
    for bin_id, bin_data in bin_data_dict.items():
        try:
            high_lambda_bin_results = high_lambda_results[bin_id]
            fit_result, _, _ = fit_low_lambda(
                bin_data, fitting_parameters, high_lambda_bin_results
            )
            results[bin_id] = fit_result
        except ValueError as e:
            results[bin_id] = {"error": str(e)}

    return results
