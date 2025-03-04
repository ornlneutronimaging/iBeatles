"""Unit tests for binning module."""

import pytest
import numpy as np
from numpy.testing import assert_array_almost_equal

from ibeatles.core.config import BinCoordinates
from ibeatles.core.fitting.binning import (
    get_bin_coordinates,
    get_bin_transmission,
    validate_transmission_data,
)


# Test data setup
@pytest.fixture
def sample_image_shape():
    return (100, 150)  # height, width


@pytest.fixture
def sample_images():
    # Create 10 images of 100x150 with known values
    images = []
    for i in range(10):
        img = np.ones((100, 150)) * (i + 1) * 0.1  # Transmission values 0.1, 0.2, ...
        images.append(img)
    return images


@pytest.fixture
def sample_wavelengths():
    return np.linspace(1, 4, 10)  # 10 wavelength points


class TestGetBinCoordinates:
    def test_valid_binning(self, sample_image_shape):
        """Test normal case with valid inputs."""
        bins = get_bin_coordinates(
            image_shape=sample_image_shape,
            x0=0,
            y0=0,
            width=40,
            height=30,
            bins_size=10,
        )

        assert len(bins) == 12  # 4x3 grid

        # Check first bin
        assert bins[0].x0 == 0
        assert bins[0].x1 == 10
        assert bins[0].y0 == 0
        assert bins[0].y1 == 10
        assert bins[0].row_index == 0
        assert bins[0].column_index == 0

        # Check grid indices
        for i, bin_coord in enumerate(bins):
            expected_col = i // 3
            expected_row = i % 3
            assert bin_coord.column_index == expected_col
            assert bin_coord.row_index == expected_row

    def test_invalid_start_coordinates(self, sample_image_shape):
        """Test error when starting coordinates are negative."""
        with pytest.raises(
            ValueError, match="Starting coordinates must be non-negative"
        ):
            get_bin_coordinates(
                image_shape=sample_image_shape,
                x0=-1,
                y0=0,
                width=40,
                height=30,
                bins_size=10,
            )

    def test_roi_exceeds_image(self, sample_image_shape):
        """Test error when ROI extends beyond image boundaries."""
        with pytest.raises(ValueError, match="ROI extends beyond image boundaries"):
            get_bin_coordinates(
                image_shape=sample_image_shape,
                x0=0,
                y0=0,
                width=200,  # Wider than image
                height=30,
                bins_size=10,
            )

    def test_invalid_bin_size(self, sample_image_shape):
        """Test error cases for invalid bin sizes."""
        # Zero bin size
        with pytest.raises(ValueError, match="Bin size must be positive"):
            get_bin_coordinates(
                image_shape=sample_image_shape,
                x0=0,
                y0=0,
                width=40,
                height=30,
                bins_size=0,
            )

        # Bin size larger than ROI
        with pytest.raises(ValueError, match="Bin size larger than ROI dimensions"):
            get_bin_coordinates(
                image_shape=sample_image_shape,
                x0=0,
                y0=0,
                width=40,
                height=30,
                bins_size=50,
            )


class TestGetBinTransmission:
    def test_basic_transmission(self, sample_images, sample_wavelengths):
        """Test basic transmission calculation for a bin."""
        bin_coords = BinCoordinates(
            x0=0, x1=10, y0=0, y1=10, row_index=0, column_index=0
        )

        wavelengths, transmission = get_bin_transmission(
            images=sample_images, wavelengths=sample_wavelengths, bin_coords=bin_coords
        )

        # Check shapes
        assert len(wavelengths) == len(sample_wavelengths)
        assert len(transmission) == len(sample_wavelengths)

        # Check values (each image has constant value of (i+1)*0.1)
        expected_transmission = np.arange(1, 11) * 0.1
        assert_array_almost_equal(transmission, expected_transmission)

    def test_wavelength_range_selection(self, sample_images, sample_wavelengths):
        """Test wavelength range selection."""
        bin_coords = BinCoordinates(
            x0=0, x1=10, y0=0, y1=10, row_index=0, column_index=0
        )

        lambda_range = (2.0, 3.0)
        wavelengths, transmission = get_bin_transmission(
            images=sample_images,
            wavelengths=sample_wavelengths,
            bin_coords=bin_coords,
            lambda_range=lambda_range,
        )

        # Check that wavelengths are within range
        assert np.all(wavelengths >= lambda_range[0])
        assert np.all(wavelengths <= lambda_range[1])

    def test_nan_handling(self, sample_images, sample_wavelengths):
        """Test handling of NaN values in images."""
        # Create image with some NaN values
        images = sample_images.copy()
        images[0][0:5, 0:5] = np.nan

        bin_coords = BinCoordinates(
            x0=0, x1=10, y0=0, y1=10, row_index=0, column_index=0
        )

        wavelengths, transmission = get_bin_transmission(
            images=images, wavelengths=sample_wavelengths, bin_coords=bin_coords
        )

        # Check that we get finite values (nanmean should handle NaNs)
        assert np.all(np.isfinite(transmission))


class TestValidateTransmissionData:
    def test_valid_data(self):
        """Test validation of good data."""
        wavelengths = np.linspace(1, 4, 20)
        transmission = np.ones_like(wavelengths) * 0.5

        assert validate_transmission_data(wavelengths, transmission)

    def test_invalid_transmission_values(self):
        """Test validation with invalid transmission values."""
        wavelengths = np.linspace(1, 4, 20)

        # Test values > 1
        transmission = np.ones_like(wavelengths) * 1.5
        assert not validate_transmission_data(wavelengths, transmission)

        # Test negative values
        transmission = np.ones_like(wavelengths) * (-0.5)
        assert not validate_transmission_data(wavelengths, transmission)

    def test_insufficient_points(self):
        """Test validation with too few points."""
        wavelengths = np.linspace(1, 4, 5)  # Only 5 points
        transmission = np.ones_like(wavelengths) * 0.5

        assert not validate_transmission_data(
            wavelengths, transmission, min_valid_points=10
        )

    def test_non_monotonic_wavelengths(self):
        """Test validation with non-monotonic wavelengths."""
        wavelengths = np.array([1, 2, 1.5, 3, 4])  # Not monotonically increasing
        transmission = np.ones_like(wavelengths) * 0.5

        assert not validate_transmission_data(wavelengths, transmission)

    def test_nan_handling(self):
        """Test validation with NaN values."""
        wavelengths = np.linspace(1, 4, 20)
        transmission = np.ones_like(wavelengths) * 0.5
        transmission[0] = np.nan  # Add one NaN

        # Should still pass if we have enough valid points
        assert validate_transmission_data(
            wavelengths, transmission, min_valid_points=15
        )

        # Should fail if too many NaNs
        transmission[:15] = np.nan
        assert not validate_transmission_data(
            wavelengths, transmission, min_valid_points=15
        )

    def test_mismatched_lengths(self):
        """Test validation with mismatched array lengths."""
        wavelengths = np.linspace(1, 4, 20)
        transmission = np.ones(15) * 0.5  # Different length

        assert not validate_transmission_data(wavelengths, transmission)


def test_valid_bin_coordinates():
    """Test valid bin coordinate creation."""
    bin_coord = BinCoordinates(x0=0, x1=10, y0=0, y1=10, row_index=0, column_index=0)
    assert isinstance(bin_coord, BinCoordinates)
    assert bin_coord.x0 == 0
    assert bin_coord.x1 == 10
    assert bin_coord.y0 == 0
    assert bin_coord.y1 == 10
    assert bin_coord.row_index == 0
    assert bin_coord.column_index == 0


def test_invalid_bin_coordinate_order():
    """Test error when end coordinates are less than start coordinates."""
    # x1 less than x0
    with pytest.raises(ValueError, match="x0 must be less than x1"):
        BinCoordinates(
            x0=10,
            x1=0,  # Invalid: x1 < x0
            y0=0,
            y1=10,
            row_index=0,
            column_index=0,
        )

    # y1 less than y0
    with pytest.raises(ValueError, match="y0 must be less than y1"):
        BinCoordinates(
            x0=0,
            x1=10,
            y0=10,
            y1=0,  # Invalid: y1 < y0
            row_index=0,
            column_index=0,
        )


def test_invalid_bin_indices():
    """Test error when row or column indices are negative."""
    with pytest.raises(ValueError, match="Row and column indices must be non-negative"):
        BinCoordinates(
            x0=0,
            x1=10,
            y0=0,
            y1=10,
            row_index=-1,  # Invalid: negative index
            column_index=0,
        )

    with pytest.raises(ValueError, match="Row and column indices must be non-negative"):
        BinCoordinates(
            x0=0,
            x1=10,
            y0=0,
            y1=10,
            row_index=0,
            column_index=-1,  # Invalid: negative index
        )


def test_bin_coordinates_equality():
    """Test that identical bin coordinates are equal."""
    bin1 = BinCoordinates(x0=0, x1=10, y0=0, y1=10, row_index=0, column_index=0)
    bin2 = BinCoordinates(x0=0, x1=10, y0=0, y1=10, row_index=0, column_index=0)
    assert bin1 == bin2


def test_bin_coordinates_conversion():
    """Test dictionary conversion of bin coordinates."""
    coords_dict = {
        "x0": 0,
        "x1": 10,
        "y0": 0,
        "y1": 10,
        "row_index": 0,
        "column_index": 0,
    }
    bin_coord = BinCoordinates(**coords_dict)
    assert bin_coord.model_dump() == coords_dict
