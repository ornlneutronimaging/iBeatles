#!/usr/bin/env python
"""Detector-specific modules for neutron imaging data processing.

This package contains modules for TPX1 MCP detector corrections and
uncertainty calculations.
"""

from ibeatles.core.detector.uncertainty import (
    OccupancyWarning,
    ZeroCountMethod,
    aggregate_roi_uncertainty,
    calculate_relative_uncertainty,
    calculate_transmission_std,
    calculate_transmission_variance,
    check_occupancy_validity,
    handle_zero_counts,
)

__all__ = [
    "OccupancyWarning",
    "ZeroCountMethod",
    "aggregate_roi_uncertainty",
    "calculate_relative_uncertainty",
    "calculate_transmission_std",
    "calculate_transmission_variance",
    "check_occupancy_validity",
    "handle_zero_counts",
]
