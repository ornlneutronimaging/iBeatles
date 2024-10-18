#!/usr/bin/env python3
"""Utility functions for fitting module."""

import logging
import numpy as np
from typing import Tuple, Callable


def remove_invalid_data_points(
    xdata: np.ndarray, ydata: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Remove NaN and infinite values from input data arrays.

    Parameters:
    -----------
    xdata : np.ndarray
        The x-axis data.
    ydata : np.ndarray
        The y-axis data.

    Returns:
    --------
    Tuple[np.ndarray, np.ndarray]
        A tuple containing the cleaned x and y data arrays.

    Warns:
    ------
    UserWarning
        If any data points were removed due to being NaN or infinite.
    """
    valid_indices = np.isfinite(xdata) & np.isfinite(ydata)
    if np.sum(valid_indices) < len(xdata):
        removed_count = len(xdata) - np.sum(valid_indices)
        logging.warning(
            f"Removed {removed_count} corrupted data point(s) from the input."
        )
        xdata = xdata[valid_indices]
        ydata = ydata[valid_indices]

    return xdata, ydata


def generate_synthetic_transmission(
    model: Callable,
    wavelengths: np.ndarray,
    true_params: dict,
    noise_level: float = 0.01,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate synthetic transmission data based on a given model with added noise.

    Parameters:
    -----------
    model : Callable
        The model function to use for generating synthetic data.
    wavelengths : np.ndarray
        Array of wavelength values.
    true_params : dict
        Dictionary of true parameter values for the model.
    noise_level : float, optional
        Standard deviation of Gaussian noise to add (default is 0.01).

    Returns:
    --------
    Tuple[np.ndarray, np.ndarray]
        Wavelengths and corresponding noisy transmission values
    """
    ideal_transmission = model(wavelengths, **true_params)
    # NOTE: add Gaussian noise (mu=0, sigma=noise_level) to the ideal transmission
    noise = np.random.normal(0, noise_level, len(wavelengths))
    noisy_transmission = ideal_transmission + noise
    return wavelengths, noisy_transmission
