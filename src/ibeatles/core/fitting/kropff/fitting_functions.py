#!/usr/bin/env python
"""Bragg peak detection and fitting module."""

import numpy as np
from scipy import special
from typing import Optional


def kropff_high_lambda(lda: np.ndarray, a0: float, b0: float) -> Optional[np.ndarray]:
    """
    Equation for the high lambda region of the Kropff fitting.

    Parameters:
    -----------
    lda : np.ndarray
        Array of lambda values (wavelengths).
    a0 : float
        Fitting parameter a0.
    b0 : float
        Fitting parameter b0.

    Returns:
    --------
    np.ndarray or None
        Calculated transmission values for the high lambda region,
        or None if any input parameter is NaN or infinite.

    Reference:
    ----------
    Equation 7.2 in "Development and application of Bragg edge neutron transmission
    imaging on the IMAT beamline" by Ranggi Sahmura Ramadhan (June 2019).
    """
    if (
        np.any(np.isnan(lda))
        or np.isnan(a0)
        or np.isnan(b0)
        or np.any(np.isinf(lda))
        or np.isinf(a0)
        or np.isinf(b0)
    ):
        return None

    return np.exp(-(a0 + b0 * lda))


def kropff_low_lambda(
    lda: np.ndarray, a0: float, b0: float, ahkl: float, bhkl: float
) -> Optional[np.ndarray]:
    """
    Equation for the low lambda region of the Kropff fitting.

    Parameters:
    -----------
    lda : np.ndarray
        Array of lambda values (wavelengths).
    a0 : float
        Fixed parameter a0 from high lambda fit.
    b0 : float
        Fixed parameter b0 from high lambda fit.
    ahkl : float
        Fitting parameter ahkl.
    bhkl : float
        Fitting parameter bhkl.

    Returns:
    --------
    np.ndarray or None
        Calculated transmission values for the low lambda region,
        or None if any input parameter is NaN or infinite.

    Reference:
    ----------
    Equation 7.3 in "Development and application of Bragg edge neutron transmission
    imaging on the IMAT beamline" by Ranggi Sahmura Ramadhan (June 2019).
    """
    if (
        np.any(np.isnan(lda))
        or np.isnan(a0)
        or np.isnan(b0)
        or np.isnan(ahkl)
        or np.isnan(bhkl)
        or np.any(np.isinf(lda))
        or np.isinf(a0)
        or np.isinf(b0)
        or np.isinf(ahkl)
        or np.isinf(bhkl)
    ):
        return None

    return np.exp(-(a0 + b0 * lda)) * np.exp(-(ahkl + bhkl * lda))


def kropff_bragg_peak_tof(
    lda: np.ndarray,
    a0: float,
    b0: float,
    ahkl: float,
    bhkl: float,
    ldahkl: float,
    sigma: float,
    tau: float,
) -> Optional[np.ndarray]:
    """
    Equation for the Bragg peak region of the Kropff fitting.

    Parameters:
    -----------
    lda : np.ndarray
        Array of lambda values (wavelengths).
    a0 : float
        Fixed parameter a0 from high lambda fit.
    b0 : float
        Fixed parameter b0 from high lambda fit.
    ahkl : float
        Fixed parameter ahkl from low lambda fit.
    bhkl : float
        Fixed parameter bhkl from low lambda fit.
    ldahkl : float
        Fitting parameter lambda_hkl (position of the Bragg edge).
    sigma : float
        Fitting parameter sigma (related to the width of the Bragg edge).
    tau : float
        Fitting parameter tau (related to the sharpness of the Bragg edge).

    Returns:
    --------
    np.ndarray or None
        Calculated transmission values for the Bragg peak region,
        or None if any input parameter is NaN or infinite.

    Reference:
    ----------
    Equations 4.3 and 4.4 in "Development and application of Bragg edge neutron transmission
    imaging on the IMAT beamline" by Ranggi Sahmura Ramadhan (June 2019).
    """
    if (
        np.any(np.isnan(lda))
        or np.isnan(a0)
        or np.isnan(b0)
        or np.isnan(ahkl)
        or np.isnan(bhkl)
        or np.isnan(ldahkl)
        or np.isnan(sigma)
        or np.isnan(tau)
        or np.any(np.isinf(lda))
        or np.isinf(a0)
        or np.isinf(b0)
        or np.isinf(ahkl)
        or np.isinf(bhkl)
        or np.isinf(ldahkl)
        or np.isinf(sigma)
        or np.isinf(tau)
    ):
        return None

    def B(ldahkl: float, sigma: float, tau: float, lda: np.ndarray) -> np.ndarray:
        const1 = (sigma * sigma) / (2 * tau * tau)
        const2 = sigma / tau

        part1 = special.erfc(-(lda - ldahkl) / (np.sqrt(2) * sigma))
        part2 = np.exp((-(lda - ldahkl) / tau) + const1)
        part3 = special.erfc((-(lda - ldahkl) / (np.sqrt(2) * sigma)) + const2)

        return 0.5 * (part1 - part2 * part3)

    exp_expression_1 = np.exp(-(a0 + b0 * lda))
    exp_expression_2 = np.exp(-(ahkl + bhkl * lda))

    b_term = B(ldahkl, sigma, tau, lda)

    return (
        b_term * exp_expression_1 + (1 - b_term) * exp_expression_1 * exp_expression_2
    )
