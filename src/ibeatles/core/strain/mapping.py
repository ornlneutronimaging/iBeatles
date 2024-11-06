#!/usr/bin/env python
"""Core functions for strain mapping from Bragg edge fitting results."""

from typing import Dict, Optional
from lmfit.model import ModelResult


def calculate_strain_mapping(
    fit_results: Dict[str, Optional[ModelResult]],
    d0: float,
    quality_threshold: float = 0.8,
) -> Dict[str, Dict[str, float]]:
    """Calculate strain from Bragg edge fitting results.

    Parameters
    ----------
    fit_results : Dict[str, Optional[ModelResult]]
        Dictionary of fitting results for each bin
    d0 : float
        Reference d-spacing value (unstrained)
    quality_threshold : float
        R-squared threshold for accepting fit results

    Returns
    -------
    Dict[str, Dict[str, float]]
        Dictionary containing strain results for each bin:
        {bin_id: {'strain': value, 'error': value, 'quality': value}}
    """
    strain_results = {}

    for bin_id, fit_result in fit_results.items():
        # skip failed fits
        if fit_result is None:
            continue

        # skip low quality fits
        if fit_result.rsquared < quality_threshold:
            continue

        # Calculate strain: (d - d0)/d0 where d = λ/2
        wavelength = fit_result.best_values["bragg_edge_wavelength"]
        wavelength_error = fit_result.params["bragg_edge_wavelength"].stderr

        d_spacing = wavelength / 2.0
        strain = (d_spacing - d0) / d0

        # Calculate error if possible
        strain_error = wavelength_error / (2.0 * d0) if wavelength_error else None

        strain_results[bin_id] = {
            "strain": strain,
            "error": strain_error,
            "quality": fit_result.rsquared,
        }

    return strain_results
