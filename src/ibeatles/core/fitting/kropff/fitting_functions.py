#!/usr/bin/env python
"""Bragg peak detection and fitting module."""

import numpy as np
from scipy import special


def kropff_high_lambda_transmission(
    lda: np.ndarray, a0: float, b0: float
) -> np.ndarray:
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
    np.ndarray
        Calculated transmission values for the high lambda region.

    Reference:
    ----------
    Equation 7.2 in
    `"Development and application of Bragg edge neutron transmission imaging on the IMAT beamline" <https://pureportal.coventry.ac.uk/en/studentTheses/development-and-application-of-bragg-edge-neutron-transmission-im>`
    by Ranggi Sahmura Ramadhan, June 2019.
    """
    return np.exp(-(a0 + b0 * lda))


def kropff_high_lambda_attenuation(lda: np.ndarray, a0: float, b0: float) -> np.ndarray:
    """
    Linear function for fitting the high lambda region in attenuation space.

    Parameters:
    -----------
    lda : np.ndarray
        Array of lambda values (wavelengths).
    a0 : float
        Intercept parameter.
    b0 : float
        Slope parameter.

    Returns:
    --------
    np.ndarray
        Calculated attenuation values for the high lambda region.
    """
    return a0 + b0 * lda


def kropff_low_lambda_transmission(
    lda: np.ndarray, a0: float, b0: float, ahkl: float, bhkl: float
) -> np.ndarray:
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
        Calculated transmission values for the low lambda region.

    Reference:
    ----------
    Equation 7.3 in
    `"Development and application of Bragg edge neutron transmission imaging on the IMAT beamline" <https://pureportal.coventry.ac.uk/en/studentTheses/development-and-application-of-bragg-edge-neutron-transmission-im>`
    by Ranggi Sahmura Ramadhan, June 2019.
    """
    return np.exp(-(a0 + b0 * lda)) * np.exp(-(ahkl + bhkl * lda))


def kropff_low_lambda_attenuation(
    lda: np.ndarray, a0: float, b0: float, ahkl: float, bhkl: float
) -> np.ndarray:
    """
    Linear function for fitting the low lambda region in attenuation space.

    Parameters:
    -----------
    lda : np.ndarray
        Array of lambda values (wavelengths).
    a0 : float
        Intercept parameter from high lambda fit.
    b0 : float
        Slope parameter from high lambda fit.
    ahkl : float
        Additional intercept parameter for low lambda region.
    bhkl : float
        Additional slope parameter for low lambda region.

    Returns:
    --------
    np.ndarray
        Calculated attenuation values for the low lambda region.
    """
    return a0 + b0 * lda + ahkl + bhkl * lda


def kropff_bragg_peak_tof(
    lda: np.ndarray,
    a0: float,
    b0: float,
    ahkl: float,
    bhkl: float,
    ldahkl: float,
    sigma: float,
    tau: float,
) -> np.ndarray:
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
        Calculated transmission values for the Bragg peak region.

    Reference:
    ----------
    Equations 4.3 and 4.4 in
    `"Development and application of Bragg edge neutron transmission imaging on the IMAT beamline" <https://pureportal.coventry.ac.uk/en/studentTheses/development-and-application-of-bragg-edge-neutron-transmission-im>`
    by Ranggi Sahmura Ramadhan, June 2019.
    """

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
