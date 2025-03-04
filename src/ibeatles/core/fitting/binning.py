"""Functions for generating bins and extracting bin data for fitting."""

from typing import List, Tuple, Optional, Sequence
import numpy as np
from ibeatles.core.config import BinCoordinates


def get_bin_coordinates(
    image_shape: Tuple[int, int],
    x0: int,
    y0: int,
    width: int,
    height: int,
    bins_size: int,
) -> List[BinCoordinates]:
    """
    Generate list of bin coordinates based on configuration.

    Parameters
    ----------
    image_shape : Tuple[int, int]
        Shape of the image (height, width)
    x0 : int
        Starting x coordinate of ROI
    y0 : int
        Starting y coordinate of ROI
    width : int
        Width of ROI
    height : int
        Height of ROI
    bins_size : int
        Size of each bin (square bins)

    Returns
    -------
    List[BinCoordinates]
        List of bin coordinates with row and column indices

    Raises
    ------
    ValueError
        If ROI extends beyond image boundaries or bins_size is invalid
    """
    # Validate inputs
    img_height, img_width = image_shape

    if x0 < 0 or y0 < 0:
        raise ValueError("Starting coordinates must be non-negative")

    if x0 + width > img_width or y0 + height > img_height:
        raise ValueError("ROI extends beyond image boundaries")

    if bins_size <= 0:
        raise ValueError("Bin size must be positive")

    if width < bins_size or height < bins_size:
        raise ValueError("Bin size larger than ROI dimensions")

    # Calculate number of bins in each direction
    n_cols = width // bins_size  # Integer division
    n_rows = height // bins_size

    bins = []
    for col in range(n_cols):
        for row in range(n_rows):
            bin_x0 = x0 + col * bins_size
            bin_x1 = bin_x0 + bins_size
            bin_y0 = y0 + row * bins_size
            bin_y1 = bin_y0 + bins_size

            # Create bin coordinates with grid position
            bin_coords = BinCoordinates(
                x0=bin_x0,
                x1=bin_x1,
                y0=bin_y0,
                y1=bin_y1,
                row_index=row,
                column_index=col,
            )

            bins.append(bin_coords)

    return bins


def get_bin_transmission(
    images: Sequence[np.ndarray],
    wavelengths: np.ndarray,
    bin_coords: BinCoordinates,
    lambda_range: Optional[Tuple[float, float]] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract wavelength-transmission profile for a single bin.

    Parameters
    ----------
    images : Sequence[np.ndarray]
        List or array of 2D transmission images
    wavelengths : np.ndarray
        Corresponding wavelengths for each image
    bin_coords : BinCoordinates
        Coordinates of the bin
    lambda_range : Optional[Tuple[float, float]]
        Optional (min, max) wavelength range to extract. If None, use all wavelengths.

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        Wavelengths and corresponding transmission values for the bin

    Notes
    -----
    - Uses numpy.nanmean to handle any NaN values in the data
    - Assumes images are already normalized to transmission values
    """
    # Extract bin region from each image and calculate mean
    # NOTE: some additional filtering might be helpful here is the data
    #       is extremely noisy
    transmission_values = np.array(
        [
            np.nanmean(
                img[bin_coords.y0 : bin_coords.y1, bin_coords.x0 : bin_coords.x1]
            )
            for img in images
        ]
    )

    # Apply wavelength range selection if specified
    if lambda_range is not None:
        lambda_min, lambda_max = lambda_range
        mask = (wavelengths >= lambda_min) & (wavelengths <= lambda_max)
        wavelengths = wavelengths[mask]
        transmission_values = transmission_values[mask]

    return wavelengths, transmission_values


def validate_transmission_data(
    wavelengths: np.ndarray, transmission: np.ndarray, min_valid_points: int = 10
) -> bool:
    """
    Validate transmission data before fitting.

    Parameters
    ----------
    wavelengths : np.ndarray
        Wavelength values
    transmission : np.ndarray
        Transmission values
    min_valid_points : int, optional
        Minimum number of valid points required, by default 10

    Returns
    -------
    bool
        True if data is valid for fitting

    Notes
    -----
    Checks:
    - Matching wavelength and transmission lengths
    - Sufficient number of valid (non-NaN) points
    - All transmission values are between 0 and 1
    - Wavelengths are monotonically increasing
    """
    # Check lengths match
    if len(wavelengths) != len(transmission):
        return False

    # Check number of valid points
    valid_mask = ~(np.isnan(transmission) | np.isnan(wavelengths))
    if np.sum(valid_mask) < min_valid_points:
        return False

    # Check transmission values are physical
    valid_transmission = transmission[valid_mask]
    if not np.all((valid_transmission >= 0) & (valid_transmission <= 1)):
        return False

    # Check wavelengths are ordered
    valid_wavelengths = wavelengths[valid_mask]
    if not np.all(np.diff(valid_wavelengths) > 0):
        return False

    return True
