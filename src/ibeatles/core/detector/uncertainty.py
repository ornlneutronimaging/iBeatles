#!/usr/bin/env python
"""Uncertainty calculations for TPX1 MCP detector corrected transmission data.

This module implements uncertainty propagation for the TPX1 detector efficiency
correction algorithm. The correction formula is:

    T_i = F_i / ((1 - P_i) * s_i)

where:
    - T_i: corrected transmission for frame i
    - F_i: raw frame counts (Poisson-distributed)
    - P_i: cumulative pixel occupancy probability at frame i
    - s_i: shutter normalization ratio (shutter_counts[i] / shutter_counts[0])

The variance formula, derived via error propagation assuming Poisson statistics
for raw counts, is:

    Var(T_i) = T_i / ((1 - P_i) * s_i)

This formula was validated via Monte Carlo simulation in the uncertainty
validation notebook (see notebooks/uncertainty_validation.ipynb).

References
----------
- TPX1 MCP detector correction algorithm from NeutronImagingScripts
- Validation notebook: notebooks/uncertainty_validation.ipynb
"""

import logging
import warnings
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, Union

import numpy as np

logger = logging.getLogger(__name__)


class ZeroCountMethod(Enum):
    """Methods for handling zero counts in uncertainty calculation.

    Attributes
    ----------
    NONE : str
        No special handling; zero counts yield zero variance.
    ANSCOMBE : str
        Apply Anscombe transform: T + 0.375 to stabilize variance.
        Recommended for variance-stabilizing transformation.
    SMALL_CONSTANT : str
        Add small constant (0.5) to transmission before calculation.
        Simple approach but may introduce bias.
    MINIMUM_COUNT : str
        Treat zero as minimum detectable (1 count equivalent).
        Conservative approach that prevents zero variance.
    """

    NONE = "none"
    ANSCOMBE = "anscombe"
    SMALL_CONSTANT = "small_constant"
    MINIMUM_COUNT = "minimum_count"


@dataclass
class OccupancyWarning:
    """Warning information about occupancy levels.

    Attributes
    ----------
    level : str
        Warning level: "safe", "caution", "warning", or "critical".
    max_occupancy : float
        Maximum occupancy value found in the data.
    affected_fraction : float
        Fraction of pixels/frames affected by high occupancy.
    message : str
        Human-readable warning message.
    """

    level: str
    max_occupancy: float
    affected_fraction: float
    message: str


# Occupancy thresholds based on validation analysis
OCCUPANCY_THRESHOLD_SAFE = 0.50  # <50%: safe region
OCCUPANCY_THRESHOLD_CAUTION = 0.70  # 50-70%: caution region
OCCUPANCY_THRESHOLD_WARNING = 0.90  # 70-90%: warning region
# >90%: critical region (first-order approximation breaks down)


def calculate_transmission_variance(
    transmission: np.ndarray,
    occupancy: np.ndarray,
    shutter_n_ratio: Union[np.ndarray, float],
    zero_count_method: ZeroCountMethod = ZeroCountMethod.NONE,
) -> np.ndarray:
    """Calculate variance of corrected transmission values.

    Implements the variance formula derived from error propagation:

        Var(T_i) = T_i / ((1 - P_i) * s_i)

    This formula assumes:
    - Raw counts follow Poisson distribution
    - Occupancy P_i is treated as known (not a random variable)
    - Shutter ratio s_i is treated as known (not a random variable)

    Parameters
    ----------
    transmission : np.ndarray
        Corrected transmission values T_i. Shape can be (n_frames,),
        (n_frames, height, width), or (height, width) for single frame.
    occupancy : np.ndarray
        Cumulative pixel occupancy probability P_i. Must be broadcastable
        to transmission shape.
    shutter_n_ratio : np.ndarray or float
        Shutter normalization ratio s_i = shutter_counts / shutter_counts[0].
        Must be broadcastable to transmission shape. For per-frame values,
        use shape (n_frames,) or (n_frames, 1, 1).
    zero_count_method : ZeroCountMethod, optional
        Method for handling zero/near-zero transmission values.
        Default is ZeroCountMethod.NONE.

    Returns
    -------
    np.ndarray
        Variance of transmission values, same shape as input transmission.

    Raises
    ------
    ValueError
        If occupancy values are >= 1.0 (would cause division by zero).
        If shutter_n_ratio contains non-positive values.

    Notes
    -----
    The variance formula is exact under the assumption that occupancy
    is deterministic. In practice, occupancy has its own uncertainty,
    but this contribution is typically small compared to counting
    statistics for occupancy < 0.7.

    Examples
    --------
    >>> transmission = np.array([100.0, 150.0, 200.0])
    >>> occupancy = np.array([0.1, 0.2, 0.3])
    >>> shutter_n_ratio = 1.0
    >>> var = calculate_transmission_variance(transmission, occupancy, shutter_n_ratio)
    >>> np.allclose(var, transmission / ((1 - occupancy) * shutter_n_ratio))
    True
    """
    transmission = np.asarray(transmission, dtype=np.float64)
    occupancy = np.asarray(occupancy, dtype=np.float64)
    shutter_n_ratio = np.asarray(shutter_n_ratio, dtype=np.float64)

    # Validate inputs
    if np.any(occupancy >= 1.0):
        raise ValueError(
            f"Occupancy values must be < 1.0 to avoid division by zero. Max occupancy: {np.max(occupancy):.4f}"
        )

    if np.any(shutter_n_ratio <= 0):
        raise ValueError(f"Shutter ratio must be positive. Min ratio: {np.min(shutter_n_ratio):.4f}")

    # Apply zero count handling
    T_effective = handle_zero_counts(transmission, occupancy, shutter_n_ratio, zero_count_method)

    # Calculate variance: Var(T) = T / ((1 - P) * s)
    denominator = (1.0 - occupancy) * shutter_n_ratio
    variance = T_effective / denominator

    # Ensure non-negative variance (handle numerical edge cases)
    variance = np.maximum(variance, 0.0)

    return variance


def calculate_transmission_std(
    transmission: np.ndarray,
    occupancy: np.ndarray,
    shutter_n_ratio: Union[np.ndarray, float],
    zero_count_method: ZeroCountMethod = ZeroCountMethod.NONE,
) -> np.ndarray:
    """Calculate standard deviation of corrected transmission values.

    This is a convenience function that returns sqrt(variance).

    Parameters
    ----------
    transmission : np.ndarray
        Corrected transmission values T_i.
    occupancy : np.ndarray
        Cumulative pixel occupancy probability P_i.
    shutter_n_ratio : np.ndarray or float
        Shutter normalization ratio s_i.
    zero_count_method : ZeroCountMethod, optional
        Method for handling zero/near-zero transmission values.

    Returns
    -------
    np.ndarray
        Standard deviation of transmission values.

    See Also
    --------
    calculate_transmission_variance : Returns variance instead of std.
    """
    variance = calculate_transmission_variance(transmission, occupancy, shutter_n_ratio, zero_count_method)
    return np.sqrt(variance)


def handle_zero_counts(
    transmission: np.ndarray,
    occupancy: np.ndarray,
    shutter_n_ratio: Union[np.ndarray, float],
    method: ZeroCountMethod,
) -> np.ndarray:
    """Apply zero-count handling to transmission values for variance calculation.

    Parameters
    ----------
    transmission : np.ndarray
        Corrected transmission values.
    occupancy : np.ndarray
        Cumulative pixel occupancy probability.
    shutter_n_ratio : np.ndarray or float
        Shutter normalization ratio.
    method : ZeroCountMethod
        Method to use for handling zero counts.

    Returns
    -------
    np.ndarray
        Modified transmission values suitable for variance calculation.

    Notes
    -----
    Different methods have different trade-offs:

    - NONE: Preserves zeros but gives zero variance (may underestimate uncertainty)
    - ANSCOMBE: Variance-stabilizing, good statistical properties
    - SMALL_CONSTANT: Simple but may introduce bias
    - MINIMUM_COUNT: Conservative, ensures non-zero variance
    """
    transmission = np.asarray(transmission, dtype=np.float64)
    T_effective = transmission.copy()

    if method == ZeroCountMethod.NONE:
        return T_effective

    elif method == ZeroCountMethod.ANSCOMBE:
        # Anscombe transform: add 3/8 to stabilize variance
        # This is applied to the effective transmission for variance calculation
        T_effective = transmission + 0.375
        return T_effective

    elif method == ZeroCountMethod.SMALL_CONSTANT:
        # Add 0.5 to zero values only
        zero_mask = transmission <= 0
        T_effective[zero_mask] = 0.5
        return T_effective

    elif method == ZeroCountMethod.MINIMUM_COUNT:
        # Treat zeros as 1-count equivalent
        # T_min = 1 / ((1 - P) * s) is the minimum detectable transmission
        shutter_n_ratio = np.asarray(shutter_n_ratio, dtype=np.float64)
        T_min = 1.0 / ((1.0 - occupancy) * shutter_n_ratio)
        zero_mask = transmission <= 0
        T_effective[zero_mask] = T_min[zero_mask] if hasattr(T_min, "__getitem__") else T_min
        return T_effective

    else:
        raise ValueError(f"Unknown zero count method: {method}")


def check_occupancy_validity(
    occupancy: np.ndarray,
    threshold_safe: float = OCCUPANCY_THRESHOLD_SAFE,
    threshold_caution: float = OCCUPANCY_THRESHOLD_CAUTION,
    threshold_warning: float = OCCUPANCY_THRESHOLD_WARNING,
) -> OccupancyWarning:
    """Check occupancy levels and return appropriate warning.

    The uncertainty formula is based on a first-order Taylor expansion
    that becomes increasingly inaccurate at high occupancy. This function
    evaluates the occupancy distribution and returns a warning level.

    Parameters
    ----------
    occupancy : np.ndarray
        Cumulative pixel occupancy probability values.
    threshold_safe : float, optional
        Occupancy threshold below which results are reliable. Default 0.50.
    threshold_caution : float, optional
        Occupancy threshold for caution level. Default 0.70.
    threshold_warning : float, optional
        Occupancy threshold for warning level. Default 0.90.

    Returns
    -------
    OccupancyWarning
        Dataclass containing warning level, statistics, and message.

    Notes
    -----
    Warning levels:
    - "safe" (P < 0.50): First-order approximation is accurate (<1% error)
    - "caution" (0.50 <= P < 0.70): Approximation begins to diverge (1-5% error)
    - "warning" (0.70 <= P < 0.90): Significant error possible (5-20% error)
    - "critical" (P >= 0.90): First-order approximation breaks down (>20% error)

    These thresholds were determined from Monte Carlo validation
    (see notebooks/uncertainty_validation.ipynb).
    """
    occupancy = np.asarray(occupancy)
    max_occ = float(np.max(occupancy))

    # Calculate affected fractions
    n_total = occupancy.size
    n_above_safe = np.sum(occupancy >= threshold_safe)
    affected_fraction = n_above_safe / n_total if n_total > 0 else 0.0

    if max_occ < threshold_safe:
        level = "safe"
        message = f"Occupancy levels are safe (max: {max_occ:.1%}). Uncertainty estimates are reliable."
    elif max_occ < threshold_caution:
        level = "caution"
        message = (
            f"Some occupancy values exceed safe threshold (max: {max_occ:.1%}, "
            f"{affected_fraction:.1%} of pixels affected). "
            f"Uncertainty estimates may have 1-5% error."
        )
    elif max_occ < threshold_warning:
        level = "warning"
        message = (
            f"High occupancy detected (max: {max_occ:.1%}, "
            f"{affected_fraction:.1%} of pixels affected). "
            f"Uncertainty estimates may have 5-20% error. "
            f"Consider using Monte Carlo validation for critical results."
        )
    else:
        level = "critical"
        message = (
            f"Critical occupancy levels detected (max: {max_occ:.1%}, "
            f"{affected_fraction:.1%} of pixels affected). "
            f"First-order approximation is unreliable (>20% error expected). "
            f"Results should be validated with Monte Carlo simulation."
        )

    warning = OccupancyWarning(
        level=level,
        max_occupancy=max_occ,
        affected_fraction=affected_fraction,
        message=message,
    )

    # Log the warning
    if level == "safe":
        logger.debug(message)
    elif level == "caution":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    else:
        logger.error(message)
        warnings.warn(message, UserWarning)

    return warning


def aggregate_roi_uncertainty(
    variance: np.ndarray,
    roi_mask: Optional[np.ndarray] = None,
    correlation_factor: float = 1.0,
) -> Tuple[float, float]:
    """Aggregate pixel uncertainties over a region of interest.

    For ROI-averaged transmission, assuming independent pixels:

        Var(T_ROI) = (1/N^2) * sum(Var(T_i)) = mean(Var(T_i)) / N

    If pixels are correlated (e.g., due to beam structure), a correlation
    factor can be applied to adjust the effective number of independent
    measurements.

    Parameters
    ----------
    variance : np.ndarray
        Per-pixel variance values. Shape should be (height, width) for
        a single frame or (n_frames, height, width) for multiple frames.
    roi_mask : np.ndarray, optional
        Boolean mask defining the ROI. True values indicate pixels to include.
        If None, all pixels are included.
    correlation_factor : float, optional
        Factor to account for pixel correlations. Value of 1.0 assumes
        independent pixels. Higher values indicate positive correlation
        (fewer effective independent measurements). Default 1.0.

    Returns
    -------
    Tuple[float, float]
        (roi_variance, roi_std) - Variance and standard deviation of
        the ROI-averaged transmission.

    Notes
    -----
    The correlation factor affects the effective sample size:
        N_eff = N / correlation_factor

    For truly independent pixels, correlation_factor = 1.0.
    For highly correlated pixels (e.g., within beam speckle size),
    correlation_factor can be estimated from the autocorrelation
    function of the image.

    Examples
    --------
    >>> variance = np.ones((100, 100)) * 10.0  # uniform variance
    >>> roi_mask = np.zeros((100, 100), dtype=bool)
    >>> roi_mask[40:60, 40:60] = True  # 20x20 ROI = 400 pixels
    >>> roi_var, roi_std = aggregate_roi_uncertainty(variance, roi_mask)
    >>> # Expected: roi_var = 10.0 / 400 = 0.025
    >>> np.isclose(roi_var, 0.025)
    True
    """
    variance = np.asarray(variance, dtype=np.float64)

    if roi_mask is not None:
        roi_mask = np.asarray(roi_mask, dtype=bool)
        # Handle broadcasting for 3D variance arrays
        if variance.ndim == 3 and roi_mask.ndim == 2:
            # Apply mask to each frame
            roi_variance = variance[:, roi_mask]
        else:
            roi_variance = variance[roi_mask]
        n_pixels = np.sum(roi_mask)
    else:
        roi_variance = variance.ravel()
        n_pixels = variance.size

    if n_pixels == 0:
        return 0.0, 0.0

    # Effective number of independent measurements
    n_effective = n_pixels / correlation_factor

    # For mean of N measurements with variances var_i:
    # Var(mean) = sum(var_i) / N^2 = mean(var_i) / N
    mean_variance = np.mean(roi_variance)
    roi_var = mean_variance / n_effective

    return float(roi_var), float(np.sqrt(roi_var))


def calculate_relative_uncertainty(
    transmission: np.ndarray,
    std: np.ndarray,
    min_transmission: float = 1e-10,
) -> np.ndarray:
    """Calculate relative uncertainty (coefficient of variation).

    Parameters
    ----------
    transmission : np.ndarray
        Corrected transmission values.
    std : np.ndarray
        Standard deviation of transmission values.
    min_transmission : float, optional
        Minimum transmission value to avoid division by zero. Default 1e-10.

    Returns
    -------
    np.ndarray
        Relative uncertainty (std / transmission), clipped to avoid infinities.
    """
    transmission = np.asarray(transmission, dtype=np.float64)
    std = np.asarray(std, dtype=np.float64)

    # Avoid division by zero
    safe_transmission = np.maximum(np.abs(transmission), min_transmission)
    relative = std / safe_transmission

    return relative
