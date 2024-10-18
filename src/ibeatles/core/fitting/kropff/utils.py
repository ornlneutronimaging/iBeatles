#!/usr/bin/env python
"""Helper functions for Kropff fitting"""

import numpy as np
from typing import Dict, Tuple
from ibeatles.core.fitting.kropff.models import kropff_transmission_model


def generate_synthetic_data(
    wavelengths: np.ndarray, true_params: Dict[str, float], noise_level: float = 0.01
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic data based on the Kropff model with added noise.

    Parameters:
    -----------
    wavelengths : np.ndarray
        Array of wavelength values
    true_params : Dict[str, float]
        Dictionary of true parameter values for the Kropff model
    noise_level : float, optional
        Standard deviation of Gaussian noise to add (default is 0.01)

    Returns:
    --------
    Tuple[np.ndarray, np.ndarray]
        Wavelengths and corresponding noisy transmission values
    """
    ideal_transmission = kropff_transmission_model(wavelengths, **true_params)
    # NOTE: add Gaussian noise (mu=0, sigma=noise_level) to the ideal transmission
    noise = np.random.normal(0, noise_level, len(wavelengths))
    noisy_transmission = ideal_transmission + noise
    return wavelengths, noisy_transmission
