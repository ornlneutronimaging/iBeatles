#!/usr/bin/env python
"""Uncertainty calculations for TPX1 MCP detector-corrected data.

This module computes uncertainty estimates for detector-efficiency-corrected
neutron imaging data. It takes the corrected TIFF stack and metadata files
as input, and outputs counts with uncertainty for a specified ROI.

The uncertainty is derived from the detector correction formula:
    T_i = F_i / ((1 - P_i) * s_i)

Where:
    - T_i: corrected counts (what the user has)
    - F_i: raw counts (derived internally)
    - P_i: cumulative pixel occupancy (derived internally)
    - s_i: shutter normalization ratio (derived from shutter counts file)

The variance formula (validated via Monte Carlo):
    Var(T_i) = T_i / ((1 - P_i) * s_i)

Usage
-----
>>> from ibeatles.core.detector import compute_counts_with_uncertainty
>>> result = compute_counts_with_uncertainty(
...     tiff_stack=corrected_images,  # shape: (n_frames, height, width)
...     tof_array=tof_values,         # shape: (n_frames,)
...     shutter_counts_file="path/to/ShutterCount.txt",
...     roi_mask=roi,                 # shape: (height, width), boolean
... )
>>> result.to_csv("output.csv", index=False)

References
----------
- Validation notebook: notebooks/uncertainty_validation.ipynb
- Reference implementation: NeutronImagingScripts/neutronimaging/detector_correction.py
"""

from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np
import pandas as pd
from loguru import logger


def load_shutter_counts(file_path: Union[str, Path]) -> pd.DataFrame:
    """Load and parse shutter counts file.

    Parameters
    ----------
    file_path : str or Path
        Path to the shutter counts file (tab-separated, .txt extension).
        Expected format: shutter_index<TAB>shutter_counts

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - shutter_index: int
        - shutter_counts: int (total neutron counts for this shutter period)
        - shutter_n_ratio: float (shutter_counts / shutter_counts[0])

    Notes
    -----
    Only rows with shutter_counts > 0 are included.
    The shutter_n_ratio is derived as counts[i] / counts[0].
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Shutter counts file not found: {file_path}")

    df = pd.read_csv(
        file_path,
        sep="\t",
        names=["shutter_index", "shutter_counts"],
    )
    # Filter out zero-count entries
    df = df[df["shutter_counts"] > 0].copy()

    if len(df) == 0:
        raise ValueError(f"No valid shutter counts found in {file_path}")

    # Derive the normalization ratio
    df["shutter_n_ratio"] = df["shutter_counts"] / df["shutter_counts"].values[0]

    logger.info(
        f"Loaded shutter counts: {len(df)} shutter periods, "
        f"counts range [{df['shutter_counts'].min()}, {df['shutter_counts'].max()}]"
    )

    return df.reset_index(drop=True)


def _recover_raw_counts(
    corrected: np.ndarray,
    shutter_counts: int,
    shutter_n_ratio: Union[np.ndarray, float],
) -> Tuple[np.ndarray, np.ndarray]:
    """Recover raw counts F_i from corrected counts T_i.

    Uses the inversion formula derived from T_i = F_i / ((1 - P_i) * s_i):
        F_i = T_i * s_i * (N - S_{i-1}) / (N + T_i * s_i)

    Where S_{i-1} = cumsum of F_j for j < i.

    Parameters
    ----------
    corrected : np.ndarray
        Corrected counts T_i, shape (n_frames, height, width).
    shutter_counts : int
        Total shutter counts N for this shutter period.
    shutter_n_ratio : np.ndarray or float
        Shutter normalization ratio s_i. If array, shape (n_frames,).

    Returns
    -------
    Tuple[np.ndarray, np.ndarray]
        (raw_counts, occupancy) - F_i and P_i arrays with same shape as input.
    """
    n_frames = corrected.shape[0]
    N = float(shutter_counts)

    # Handle scalar vs array shutter ratio
    if np.isscalar(shutter_n_ratio):
        s = np.full(n_frames, shutter_n_ratio)
    else:
        s = np.asarray(shutter_n_ratio)

    # Initialize output arrays
    raw = np.zeros_like(corrected, dtype=np.float64)
    occupancy = np.zeros_like(corrected, dtype=np.float64)

    # Iteratively compute F_i and P_i
    cumsum_raw = np.zeros(corrected.shape[1:], dtype=np.float64)  # S_{i-1}

    for i in range(n_frames):
        T_i = corrected[i].astype(np.float64)
        s_i = s[i]

        # F_i = T_i * s_i * (N - S_{i-1}) / (N + T_i * s_i)
        numerator = T_i * s_i * (N - cumsum_raw)
        denominator = N + T_i * s_i

        # Avoid division by zero and negative counts
        # (numerator can be negative if cumsum_raw exceeds N due to numerical issues)
        with np.errstate(divide="ignore", invalid="ignore"):
            F_i = np.where((denominator > 0) & (numerator >= 0), numerator / denominator, 0.0)

        raw[i] = F_i

        # Update cumsum for next iteration
        cumsum_raw = cumsum_raw + F_i

        # P_i = cumsum(F) / N (including current frame)
        occupancy[i] = cumsum_raw / N

    return raw, occupancy


def _compute_variance(
    corrected: np.ndarray,
    occupancy: np.ndarray,
    shutter_n_ratio: Union[np.ndarray, float],
) -> np.ndarray:
    """Compute variance of corrected counts.

    Var(T_i) = T_i / ((1 - P_i) * s_i)

    Parameters
    ----------
    corrected : np.ndarray
        Corrected counts T_i.
    occupancy : np.ndarray
        Pixel occupancy probability P_i.
    shutter_n_ratio : np.ndarray or float
        Shutter normalization ratio s_i.

    Returns
    -------
    np.ndarray
        Variance array with same shape as input.
    """
    # Broadcast shutter ratio if needed
    if np.isscalar(shutter_n_ratio):
        s = shutter_n_ratio
    else:
        s = np.asarray(shutter_n_ratio)
        if s.ndim == 1:
            # Shape (n_frames,) -> (n_frames, 1, 1) for broadcasting
            s = s[:, np.newaxis, np.newaxis]

    # Compute variance
    denominator = (1.0 - occupancy) * s

    with np.errstate(divide="ignore", invalid="ignore"):
        variance = np.where(denominator > 0, corrected / denominator, 0.0)

    # Ensure non-negative
    variance = np.maximum(variance, 0.0)

    return variance


def compute_counts_with_uncertainty(
    tiff_stack: np.ndarray,
    tof_array: np.ndarray,
    shutter_counts_file: Union[str, Path],
    roi_mask: Optional[np.ndarray] = None,
    shutter_index: int = 0,
) -> pd.DataFrame:
    """Compute counts with uncertainty for a region of interest.

    This is the main entry point for uncertainty calculation. It takes
    the detector-efficiency-corrected TIFF stack and metadata files,
    computes the uncertainty, and returns a DataFrame ready for export.

    Parameters
    ----------
    tiff_stack : np.ndarray
        Detector-efficiency-corrected image stack, shape (n_frames, height, width).
        These are the T_i values from the correction formula.
    tof_array : np.ndarray
        Time-of-flight values for each frame, shape (n_frames,).
        Can be obtained from load_time_spectra()["tof_array"].
    shutter_counts_file : str or Path
        Path to the shutter counts file.
    roi_mask : np.ndarray, optional
        Boolean mask defining the ROI, shape (height, width).
        If None, uses all pixels.
    shutter_index : int, optional
        Which shutter period to use (default 0, the first).
        For single-shutter acquisitions, use 0.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns:
        - tof: Time-of-flight values
        - counts: Summed counts in ROI
        - uncertainty: Uncertainty (standard deviation) of summed counts

    Examples
    --------
    >>> # Load data using existing iBeatles functions
    >>> data = load_data_from_folder("/path/to/corrected/tiffs")
    >>> spectra = load_time_spectra(spectra_file, distance, offset)
    >>>
    >>> # Define ROI (e.g., 100x100 box in center)
    >>> roi = np.zeros((512, 512), dtype=bool)
    >>> roi[200:300, 200:300] = True
    >>>
    >>> # Compute uncertainty
    >>> result = compute_counts_with_uncertainty(
    ...     tiff_stack=data["data"],
    ...     tof_array=spectra["tof_array"],
    ...     shutter_counts_file="/path/to/ShutterCount.txt",
    ...     roi_mask=roi,
    ... )
    >>>
    >>> # Export to CSV
    >>> result.to_csv("counts_with_uncertainty.csv", index=False)
    """
    # Validate inputs
    tiff_stack = np.asarray(tiff_stack, dtype=np.float64)
    tof_array = np.asarray(tof_array)

    if tiff_stack.ndim != 3:
        raise ValueError(f"tiff_stack must be 3D (n_frames, height, width), got shape {tiff_stack.shape}")

    n_frames, height, width = tiff_stack.shape

    if len(tof_array) != n_frames:
        raise ValueError(f"tof_array length ({len(tof_array)}) must match number of frames ({n_frames})")

    # Load shutter metadata
    shutter_df = load_shutter_counts(shutter_counts_file)

    if shutter_index < 0 or shutter_index >= len(shutter_df):
        raise ValueError(f"shutter_index {shutter_index} out of range (must be 0 to {len(shutter_df) - 1})")

    shutter_counts = int(shutter_df.loc[shutter_index, "shutter_counts"])
    shutter_n_ratio = float(shutter_df.loc[shutter_index, "shutter_n_ratio"])

    logger.info(f"Using shutter period {shutter_index}: counts={shutter_counts}, ratio={shutter_n_ratio:.4f}")

    # Create ROI mask if not provided
    if roi_mask is None:
        roi_mask = np.ones((height, width), dtype=bool)
        logger.info("No ROI mask provided, using all pixels")
    else:
        roi_mask = np.asarray(roi_mask, dtype=bool)
        if roi_mask.shape != (height, width):
            raise ValueError(f"roi_mask shape {roi_mask.shape} must match image shape ({height}, {width})")
        n_pixels = np.sum(roi_mask)
        logger.info(f"ROI contains {n_pixels} pixels")

    # Recover raw counts and compute occupancy
    logger.info("Computing occupancy from corrected counts...")
    _, occupancy = _recover_raw_counts(tiff_stack, shutter_counts, shutter_n_ratio)

    # Compute variance
    logger.info("Computing variance...")
    variance = _compute_variance(tiff_stack, occupancy, shutter_n_ratio)

    # Aggregate over ROI
    logger.info("Aggregating over ROI...")
    counts_per_frame = np.zeros(n_frames)
    variance_per_frame = np.zeros(n_frames)

    for i in range(n_frames):
        # Sum counts in ROI
        counts_per_frame[i] = np.sum(tiff_stack[i][roi_mask])
        # Sum variances (pixels assumed independent)
        variance_per_frame[i] = np.sum(variance[i][roi_mask])

    # Standard deviation = sqrt(variance)
    uncertainty_per_frame = np.sqrt(variance_per_frame)

    # Build output DataFrame
    result = pd.DataFrame(
        {
            "tof": tof_array,
            "counts": counts_per_frame,
            "uncertainty": uncertainty_per_frame,
        }
    )

    logger.info(f"Computed uncertainty for {n_frames} frames")

    return result
