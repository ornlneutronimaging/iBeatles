#!/usr/bin/env python
"""Mathematical models used in Kropff fitting"""

import numpy as np
from scipy import special


def kropff_high_lambda_transmission(
    wavelength: np.ndarray, a0: float, b0: float
) -> np.ndarray:
    """
    Calculate the high-wavelength side transmission function.

    Parameters
    ----------
    wavelength : np.ndarray
        The wavelength values to calculate the function.
    a0 : float
        The a0 parameter.
    b0 : float
        The b0 parameter.

    Returns
    -------
    np.ndarray
        The high-wavelength side transmission function.
    """
    return np.exp(-(a0 + b0 * wavelength))


def kropff_low_lambda_transmission(
    wavelength: np.ndarray, a0: float, b0: float, a_hkl: float, b_hkl: float
) -> np.ndarray:
    """
    Calculate the low-wavelength side transmission function.

    Parameters
    ----------
    wavelength : np.ndarray
        The wavelength values to calculate the function.
    a0 : float
        The a0 parameter.
    b0 : float
        The b0 parameter.
    a_hkl : float
        The a_hkl parameter.
    b_hkl : float
        The b_hkl parameter.

    Returns
    -------
    np.ndarray
        The low-wavelength side transmission function.
    """
    return np.exp(-(a0 + b0 * wavelength) - (a_hkl + b_hkl * wavelength))


def bragg_edge_function(
    wavelength: np.ndarray, bragg_edge_wavelength: float, sigma: float, tau: float
) -> np.ndarray:
    """
    Calculate the Bragg edge function.

    Parameters
    ----------
    wavelength : np.ndarray
        The wavelength values to calculate the function.
    bragg_edge_wavelength : float
        The wavelength of the Bragg edge.
    sigma : float
        The sigma parameter (related to symmetric broadening).
    tau : float
        The tau parameter (related to asymmetric broadening).

    Returns
    -------
    np.ndarray
        The Bragg edge function.
    """
    t = wavelength - bragg_edge_wavelength
    y = sigma / tau

    term1 = special.erfc(-t / (np.sqrt(2) * sigma))
    term2 = np.exp(-(t / tau) + (y**2 / 2))
    term3 = special.erfc(-t / (np.sqrt(2) * sigma) + y)

    return 0.5 * (term1 - term2 * term3)


def kropff_transmission_model(
    wavelength: np.ndarray,
    a0: float,
    b0: float,
    a_hkl: float,
    b_hkl: float,
    bragg_edge_wavelength: float,
    sigma: float,
    tau: float,
) -> np.ndarray:
    """
    Calculate the full Kropff transmission model.

    Parameters
    ----------
    wavelength : np.ndarray
        The wavelength values to calculate the function.
    a0 : float
        The a0 parameter.
    b0 : float
        The b0 parameter.
    a_hkl : float
        The a_hkl parameter.
    b_hkl : float
        The b_hkl parameter.
    bragg_edge_wavelength : float
        The wavelength of the Bragg edge.
    sigma : float
        The sigma parameter (related to symmetric broadening).
    tau : float
        The tau parameter (related to asymmetric broadening).

    Returns
    -------
    np.ndarray
        The full Kropff transmission model.
    """
    high_lambda = kropff_high_lambda_transmission(wavelength, a0, b0)
    low_lambda = kropff_low_lambda_transmission(wavelength, a0, b0, a_hkl, b_hkl)
    edge_function = bragg_edge_function(wavelength, bragg_edge_wavelength, sigma, tau)

    return low_lambda + (high_lambda - low_lambda) * edge_function
