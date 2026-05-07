#!/usr/bin/env python
"""Detector-specific modules for neutron imaging data processing.

This package contains modules for TPX1 MCP detector uncertainty calculations.
"""

from ibeatles.core.detector.uncertainty import (
    compute_counts_with_uncertainty,
    load_shutter_counts,
)

__all__ = [
    "compute_counts_with_uncertainty",
    "load_shutter_counts",
]
