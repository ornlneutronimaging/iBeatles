#!/usr/bin/env python
"""Visualization functions for strain mapping results."""

from typing import Dict, Tuple, Optional
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import matplotlib.pyplot as plt


def plot_strain_map_overlay(
    strain_results: Dict[str, Dict[str, float]],
    bin_transmission: Dict[str, Dict],
    integrated_image: np.ndarray,
    colormap: str = "viridis",
    interpolation: str = "nearest",
    alpha: float = 0.5,
    vmin: Optional[float] = None,
    vmax: Optional[float] = None,
) -> Tuple[Figure, Axes]:
    """Create strain map overlay on integrated image.

    Parameters
    ----------
    strain_results : Dict[str, Dict[str, float]]
        Dictionary of strain results per bin
    bin_transmission : Dict[str, Dict]
        Dictionary containing bin coordinates
    integrated_image : np.ndarray
        Background image to overlay on
    colormap : str
        Matplotlib colormap name
    interpolation : str
        Matplotlib interpolation method
    alpha : float
        Transparency of overlay
    vmin : Optional[float]
        Minimum value for strain colormap
    vmax : Optional[float]
        Maximum value for strain colormap

    Returns
    -------
    Tuple[Figure, Axes]
        Figure and axes with plot
    """
    # Create empty strain map matching integrated image shape
    strain_map = np.full_like(integrated_image, np.nan, dtype=np.float64)

    # Fill strain values into the map
    for bin_id, result in strain_results.items():
        coords = bin_transmission[bin_id]["coordinates"]
        strain_map[coords.y0 : coords.y1, coords.x0 : coords.x1] = result["strain"]

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot background image in grayscale
    ax.imshow(integrated_image, cmap="gray", interpolation=interpolation)

    # Plot strain map overlay
    # If vmin/vmax not provided, use data range
    if vmin is None:
        vmin = np.nanmin(strain_map)
    if vmax is None:
        vmax = np.nanmax(strain_map)

    im = ax.imshow(
        strain_map,
        cmap=colormap,
        alpha=alpha,
        interpolation=interpolation,
        vmin=vmin,
        vmax=vmax,
    )

    # Add colorbar
    fig.colorbar(im, ax=ax, label="Strain")

    # Add title and labels
    ax.set_title("Strain Map Overlay")
    ax.set_xlabel("Pixel")
    ax.set_ylabel("Pixel")

    return fig, ax
