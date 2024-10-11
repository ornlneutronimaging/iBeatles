#!/usr/bin/env python3
"""Utility functions for fitting module."""

import logging
import numpy as np
from typing import Tuple


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
