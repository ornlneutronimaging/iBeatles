#!/usr/bin/env python
"""Visualization functions for strain mapping results."""

from typing import Dict, Tuple, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from lmfit.model import ModelResult


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


def plot_fitting_results_grid(
    fit_results: Dict[str, Optional[ModelResult]],
    bin_transmission: Dict[str, Dict],
    reference_wavelength: float,
    figsize: Tuple[int, int] = (50, 50),
) -> Tuple[Figure, np.ndarray]:
    """Create grid plot of fitting results matching binning layout.

    Parameters
    ----------
    fit_results : Dict[str, Optional[ModelResult]]
        Dictionary of fitting results for each bin
    bin_transmission : Dict[str, Dict]
        Dictionary containing bin coordinates and data
    reference_wavelength : float
        Reference Bragg edge wavelength for comparison
    figsize : Tuple[int, int]
        Figure size in inches

    Returns
    -------
    Tuple[Figure, np.ndarray]
        Figure and array of axes
    """
    # Find grid dimensions from bin coordinates
    max_row = (
        max(
            int(bin_transmission[bin_id]["coordinates"].row_index)
            for bin_id in bin_transmission
        )
        + 1
    )
    max_col = (
        max(
            int(bin_transmission[bin_id]["coordinates"].column_index)
            for bin_id in bin_transmission
        )
        + 1
    )

    # Create figure and axes grid
    fig, axes = plt.subplots(max_row, max_col, figsize=figsize)

    # Plot each bin result in its corresponding position
    for bin_id, fit_result in fit_results.items():
        coords = bin_transmission[bin_id]["coordinates"]
        row = coords.row_index
        col = coords.column_index

        ax = axes[row, col]
        ax.set_title(f"Bin {bin_id}")

        if fit_result is not None:
            # Plot fitting result
            fit_result.plot_fit(ax=ax, datafmt=".")

            # Add reference wavelength line
            ax.axvline(
                x=reference_wavelength, color="black", linestyle="--", label="Reference"
            )

            # Add fitted wavelength line
            ax.axvline(
                x=fit_result.best_values["bragg_edge_wavelength"],
                color="green",
                linestyle="--",
                label="Fitted",
            )

        else:
            # Plot raw data
            wavelengths = bin_transmission[bin_id]["wavelengths"]
            wavelengths_angstrom = wavelengths * 1e10
            transmission = bin_transmission[bin_id]["transmission"]
            ax.scatter(wavelengths_angstrom, transmission, label="Raw Data", s=1)

        # set x and y labels
        ax.set_xlabel("Wavelength ($\AA$)")
        ax.set_ylabel("Transmission")

    plt.tight_layout()
    return fig, axes
