#!/usr/bin/env python
"""Unit tests for strain visualization functions."""

import pytest
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.image import AxesImage
from matplotlib.lines import Line2D
from lmfit import Model, Parameters
from lmfit.model import ModelResult

from ibeatles.core.strain.visualization import (
    plot_strain_map_overlay,
    plot_fitting_results_grid,
)
from ibeatles.core.config import BinCoordinates


@pytest.fixture
def mock_fitting_data():
    """Create mock data for testing fitting results grid."""

    # Create mock ModelResult
    def create_mock_result(wavelength: float) -> ModelResult:
        # Create dummy model and parameters
        model = Model(lambda x: x)
        params = Parameters()
        params.add("bragg_edge_wavelength", value=wavelength)

        # Create minimal result object
        result = ModelResult(model, params)
        result.best_fit = np.array([0.5, 0.6, 0.7])
        result.best_values = {"bragg_edge_wavelength": wavelength}
        result.data = np.array([0.4, 0.5, 0.6])

        # Add plot_fit method
        def plot_fit(ax, datafmt):
            ax.plot(result.best_fit, "r-")
            ax.plot(result.data, datafmt)

        result.plot_fit = plot_fit
        return result

    # Create mock bin data
    wavelengths = np.linspace(3.5, 4.5, 10)
    transmission = np.random.uniform(0.5, 1.0, 10)

    # Create 2x2 grid of results
    fit_results = {
        "0": create_mock_result(4.0),  # Good fit
        "1": None,  # Failed fit
        "2": create_mock_result(4.1),
        "3": create_mock_result(4.2),
    }

    bin_transmission = {
        "0": {
            "coordinates": BinCoordinates(
                x0=0, x1=2, y0=0, y1=2, row_index=0, column_index=0
            ),
            "wavelengths": wavelengths,
            "transmission": transmission,
        },
        "1": {
            "coordinates": BinCoordinates(
                x0=2, x1=4, y0=0, y1=2, row_index=0, column_index=1
            ),
            "wavelengths": wavelengths,
            "transmission": transmission,
        },
        "2": {
            "coordinates": BinCoordinates(
                x0=0, x1=2, y0=2, y1=4, row_index=1, column_index=0
            ),
            "wavelengths": wavelengths,
            "transmission": transmission,
        },
        "3": {
            "coordinates": BinCoordinates(
                x0=2, x1=4, y0=2, y1=4, row_index=1, column_index=1
            ),
            "wavelengths": wavelengths,
            "transmission": transmission,
        },
    }

    return fit_results, bin_transmission


def test_plot_fitting_results_grid(mock_fitting_data):
    """Test creation of fitting results grid plot."""
    fit_results, bin_transmission = mock_fitting_data
    reference_wavelength = 4.0

    # Create plot
    fig, axes = plot_fitting_results_grid(
        fit_results=fit_results,
        bin_transmission=bin_transmission,
        reference_wavelength=reference_wavelength,
    )

    # Check return types
    assert isinstance(fig, Figure)
    assert isinstance(axes, np.ndarray)
    assert axes.shape == (2, 2)  # 2x2 grid

    # Check first plot (good fit with legend)
    ax00 = axes[0, 0]
    assert ax00.get_title() == "Bin 0"
    assert any(isinstance(line, Line2D) for line in ax00.get_lines())

    # Check failed fit plot (raw data only)
    ax01 = axes[0, 1]
    assert ax01.get_title() == "Bin 1"
    collections = ax01.collections
    assert len(collections) == 1  # Scatter plot of raw data

    # Check labels
    for ax in axes.flat:
        assert ax.get_xlabel() == "Wavelength ($\AA$)"
        assert ax.get_ylabel() == "Transmission"


def test_grid_dimensions(mock_fitting_data):
    """Test grid dimensions match binning layout."""
    fit_results, bin_transmission = mock_fitting_data

    fig, axes = plot_fitting_results_grid(
        fit_results=fit_results,
        bin_transmission=bin_transmission,
        reference_wavelength=4.0,
        figsize=(10, 10),
    )

    # Check grid dimensions
    assert axes.shape == (2, 2)  # Should match max row/col indices


def test_custom_figsize(mock_fitting_data):
    """Test custom figure size."""
    fit_results, bin_transmission = mock_fitting_data
    custom_figsize = np.array((15, 15))

    fig, axes = plot_fitting_results_grid(
        fit_results=fit_results,
        bin_transmission=bin_transmission,
        reference_wavelength=4.0,
        figsize=custom_figsize,
    )

    # Check figure size
    np.testing.assert_allclose(fig.get_size_inches(), custom_figsize)


@pytest.fixture
def mock_data():
    """Create mock data for testing."""
    # Create small test image
    integrated_image = np.ones((10, 10))

    # Create mock strain results
    strain_results = {
        "0": {"strain": 0.001, "error": 0.0001, "quality": 0.95},
        "1": {"strain": -0.001, "error": 0.0001, "quality": 0.90},
    }

    # Create mock bin transmission
    bin_transmission = {
        "0": {
            "coordinates": BinCoordinates(
                x0=2, x1=4, y0=2, y1=4, row_index=0, column_index=0
            )
        },
        "1": {
            "coordinates": BinCoordinates(
                x0=6, x1=8, y0=6, y1=8, row_index=1, column_index=1
            )
        },
    }

    return integrated_image, strain_results, bin_transmission


def test_plot_strain_map_overlay(mock_data):
    """Test strain map overlay plot creation."""
    integrated_image, strain_results, bin_transmission = mock_data

    # Create plot
    fig, ax = plot_strain_map_overlay(
        strain_results=strain_results,
        bin_transmission=bin_transmission,
        integrated_image=integrated_image,
    )

    # Check return types
    assert isinstance(fig, Figure)
    assert isinstance(ax, Axes)

    # Check if both images are plotted
    images = ax.get_images()
    assert len(images) == 2
    assert all(isinstance(img, AxesImage) for img in images)

    # Check background image properties
    bg_image = images[0]
    assert bg_image.get_cmap().name == "gray"

    # Check strain overlay properties
    strain_image = images[1]
    assert strain_image.get_cmap().name == "viridis"
    assert strain_image.get_alpha() == 0.5

    # Check img and colorbar axes
    assert len(fig.axes) == 2  # Image and colorbar
    assert fig.axes[0] == ax
    assert fig.axes[1].get_ylabel() == "Strain"

    # Check labels
    assert ax.get_xlabel() == "Pixel"
    assert ax.get_ylabel() == "Pixel"
    assert ax.get_title() == "Strain Map Overlay"


def test_plot_strain_map_overlay_custom_params(mock_data):
    """Test strain map overlay plot with custom parameters."""
    integrated_image, strain_results, bin_transmission = mock_data

    # Custom parameters
    custom_params = {
        "colormap": "hot",
        "interpolation": "bilinear",
        "alpha": 0.7,
        "vmin": -0.002,
        "vmax": 0.002,
    }

    # Create plot with custom parameters
    fig, ax = plot_strain_map_overlay(
        strain_results=strain_results,
        bin_transmission=bin_transmission,
        integrated_image=integrated_image,
        **custom_params,
    )

    # Check strain overlay properties
    strain_image = ax.get_images()[1]
    assert strain_image.get_cmap().name == "hot"
    assert strain_image.get_alpha() == 0.7
    assert strain_image.get_clim() == (-0.002, 0.002)


def test_empty_strain_results(mock_data):
    """Test plotting with empty strain results."""
    integrated_image, _, bin_transmission = mock_data

    # Create plot with empty strain results
    fig, ax = plot_strain_map_overlay(
        strain_results={},
        bin_transmission=bin_transmission,
        integrated_image=integrated_image,
    )

    # Check if only background image is plotted
    strain_image = np.array(ax.get_images()[1].get_array())
    assert np.all(np.isnan(strain_image))


if __name__ == "__main__":
    pytest.main(["-v", __file__])
