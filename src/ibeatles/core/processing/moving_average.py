#!/usr/bin/env python
"""Normalization functions for the TOF imaging data."""

import numpy as np
import scipy.ndimage
from typing import Tuple, overload, Union
from ibeatles.core.config import MovingAverage, KernelType


@overload
def moving_average(
    data: np.ndarray,
    kernel_type: str,
    kernel: Union[Tuple[int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """
    Apply moving average filter to the input data.

    Parameters
    ----------
    data : np.ndarray
        Input data. Must be a 2D image or 3D volume (TOF stack of 2D images).
    kernel_type : str
        Type of kernel to use for the filter. Must be either 'Box' or 'Gaussian'.
    kernel : Union[Tuple[int, int], Tuple[int, int, int]]
        Size of the kernel. For 2D data, use (y, x). For 3D data, use (y, x, lambda).

    Returns
    -------
    np.ndarray
        Filtered data with the same shape as the input.

    Raises
    ------
    ValueError
        If input data, kernel_type, or kernel is invalid.
    """
    pass


@overload
def moving_average(data: np.ndarray, config: MovingAverage) -> np.ndarray:
    """
    Apply moving average filter to the input data using a MovingAverage configuration.

    Parameters
    ----------
    data : np.ndarray
        Input data. Must be a 2D image or 3D volume (TOF stack of 2D images).
    config : MovingAverage
        Configuration for the moving average filter.

    Returns
    -------
    np.ndarray
        Filtered data with the same shape as the input.

    Raises
    ------
    ValueError
        If input data or configuration is invalid.
    """
    pass


def moving_average(
    data: np.ndarray,
    arg2: Union[str, MovingAverage],
    arg3: Union[Tuple[int, ...], None] = None,
) -> np.ndarray:
    """
    Apply moving average filter to the input data.

    This function supports two calling conventions:
    1. moving_average(data, kernel_type, kernel)
    2. moving_average(data, config)

    Parameters
    ----------
    data : np.ndarray
        Input data. Must be a 2D image or 3D volume (TOF stack of 2D images).
    arg2 : Union[str, MovingAverage]
        Either a string specifying the kernel type ('Box' or 'Gaussian') or a MovingAverage configuration object.
    arg3 : Union[Tuple[int, ...], None], optional
        If arg2 is a string, this should be a tuple specifying the kernel size.

    Returns
    -------
    np.ndarray
        Filtered data with the same shape as the input.

    Raises
    ------
    ValueError
        If input data, kernel type, kernel size, or configuration is invalid.
    """
    if isinstance(arg2, str):
        kernel_type = arg2
        kernel = arg3
        if kernel is None:
            raise ValueError(
                "Kernel size must be provided when specifying kernel type as a string."
            )
        config = MovingAverage(
            active=True,
            dimension="2D" if len(kernel) == 2 else "3D",
            size=kernel,
            type=KernelType(kernel_type),
        )
    elif isinstance(arg2, MovingAverage):
        config = arg2
    else:
        raise ValueError("Invalid argument type for kernel_type or config.")

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
