#!/usr/bin/env python
"""Unit tests for strain visualization functions."""

import pytest
import numpy as np
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.image import AxesImage

from ibeatles.core.strain.visualization import plot_strain_map_overlay
from ibeatles.core.config import BinCoordinates


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
