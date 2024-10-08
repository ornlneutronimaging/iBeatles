#!/usr/bin/env python
"""Kropff models for fitting."""

from typing import Dict, List, Tuple
from pydantic import BaseModel, Field
from ibeatles.core.config import (
    PixelBinning,
    FittingCriteria,
    RejectionCriteria,
    ThresholdFinder,
)


class KropffFittingParameters(BaseModel):
    lambda_min: float = Field(..., description="Minimum lambda value for fitting")
    lambda_max: float = Field(..., description="Maximum lambda value for fitting")
    threshold_finder: ThresholdFinder = Field(
        ..., description="Threshold finder configuration"
    )
    fitting_criteria: FittingCriteria = Field(..., description="Fitting criteria")
    rejection_criteria: RejectionCriteria = Field(..., description="Rejection criteria")
    pixel_binning: PixelBinning = Field(..., description="Pixel binning parameters")


class KropffBinData(BaseModel):
    xaxis: List[float] = Field(..., description="X-axis data for the bin")
    yaxis: List[float] = Field(..., description="Y-axis data for the bin")
    bin_coordinates: Dict[str, int] = Field(..., description="Coordinates of the bin")
    bragg_peak_threshold: Dict[str, float] = Field(
        ..., description="Bragg peak threshold values"
    )


class KropffFittingInput(BaseModel):
    parameters: KropffFittingParameters
    bin_data: Dict[str, KropffBinData] = Field(
        ..., description="Dictionary of bin data"
    )


class KropffFittingResult(BaseModel):
    a0: Tuple[float, float] = Field(..., description="Fitted a0 value and error")
    b0: Tuple[float, float] = Field(..., description="Fitted b0 value and error")
    ahkl: Tuple[float, float] = Field(..., description="Fitted ahkl value and error")
    bhkl: Tuple[float, float] = Field(..., description="Fitted bhkl value and error")
    lambda_hkl: Tuple[float, float] = Field(
        ..., description="Fitted lambda_hkl value and error"
    )
    tau: Tuple[float, float] = Field(..., description="Fitted tau value and error")
    sigma: Tuple[float, float] = Field(..., description="Fitted sigma value and error")
    fitted_data: Dict[str, List[float]] = Field(
        ..., description="Fitted data for each region"
    )
