#!/usr/bin/env python
"""Normalization functions for the TOF imaging data."""

import numpy as np
import scipy.ndimage
from typing import Any, Dict, Optional, Tuple
from ibeatles.core.config import MovingAverage, KernelType


def moving_average(data: np.ndarray, config: MovingAverage) -> np.ndarray:
    """
    Apply moving average filter to the input data.

    Parameters
    ----------
    data : np.ndarray
        Input data. Must be a 2D image or 3D volume (TOF stack of 2D images).
    config : MovingAverage
        Configuration for the moving average filter from IBeatlesUserConfig.

    Returns
    -------
    np.ndarray
        Filtered data with the same shape as the input.

    Raises
    ------
    ValueError
        If input data or configuration is invalid.
    """
    if not config.active:
        return data

    if data.ndim not in (2, 3):
        raise ValueError("Data must be 2D image or 3D volume (TOF stack of 2D images).")

    kernel = _get_kernel_from_config(config)

    if data.ndim == 2 and len(kernel) == 3:
        raise ValueError("Cannot apply 3D kernel to 2D data.")

    if data.ndim == 3 and len(kernel) == 2:
        return _apply_2d_kernel_to_3d_data(data, config)

    if config.type == KernelType.box:
        return _apply_box_filter(data, kernel)
    elif config.type == KernelType.gaussian:
        return scipy.ndimage.gaussian_filter(data, kernel)
    else:
        raise ValueError(f"Unsupported kernel type: {config.type}")


def _get_kernel_from_config(config: MovingAverage) -> Tuple[int, ...]:
    if isinstance(config.size, dict):
        kernel = (config.size["y"], config.size["x"])
        if config.dimension == "3D":
            kernel += (config.size["lambda"],)
    else:
        kernel = config.size
    return kernel


def _apply_2d_kernel_to_3d_data(data: np.ndarray, config: MovingAverage) -> np.ndarray:
    output = np.zeros_like(data)
    for i in range(data.shape[2]):
        output[:, :, i] = moving_average(data[:, :, i], config)
    return output


def _apply_box_filter(data: np.ndarray, kernel: Tuple[int, ...]) -> np.ndarray:
    kernel_array = np.ones(kernel)
    kernel_array /= kernel_array.sum()
    return scipy.ndimage.convolve(data, kernel_array)


def normalize_data(
    sample_data: np.ndarray,
    ob_data: Optional[np.ndarray],
    time_spectra: Dict[str, Any],
    config: Dict[str, Any],
    output_folder: str,
) -> Tuple[np.ndarray, str]:
    """
    Normalize the input data based on the provided configuration.

    Parameters:
    -----------
    sample_data : np.ndarray
        The raw sample data to be normalized.
    ob_data : Optional[np.ndarray]
        The open beam data, if available.
    time_spectra : Dict[str, Any]
        Time spectra information.
    config : Dict[str, Any]
        Configuration dictionary containing normalization settings.
    output_folder : str
        Base output folder for normalized data.

    Returns:
    --------
    Tuple[np.ndarray, str]
        A tuple containing the normalized data and the full path to the output folder.
    """
    # Implementation here
    pass
