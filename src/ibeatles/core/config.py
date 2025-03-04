#!/usr/bin/env python
"""Pydantic configuration model for CLI and GUI application settings (user)"""

import logging
import matplotlib.pyplot as plt
from enum import Enum
from typing import Dict, Optional, Union, Tuple, Literal, List
from pydantic import BaseModel, Field, model_validator, field_validator
from pathlib import Path


class SampleBackground(BaseModel):
    x0: int
    y0: int
    width: int
    height: int


class KernelType(str, Enum):
    box = "Box"
    gaussian = "Gaussian"


class KernelSize(BaseModel):
    y: int = 3
    x: int = 3
    lambda_: int = Field(default=3, alias="lambda")

    @model_validator(mode="after")
    def check_size(cls, values):
        return values


class MovingAverage(BaseModel):
    active: bool = True
    dimension: Literal["2D", "3D"] = "2D"
    size: KernelSize = Field(default_factory=KernelSize)
    type: KernelType = KernelType.box

    @model_validator(mode="after")
    def check_size(self) -> "MovingAverage":
        if self.dimension == "2D" and hasattr(self.size, "lambda_"):
            delattr(self.size, "lambda_")
        return self


class ProcessOrder(str, Enum):
    moving_average_normalization = "Moving average, Normalization"
    normalization_moving_average = "Normalization, Moving Average"


class NormalizationConfig(BaseModel):
    sample_background: Optional[List[SampleBackground]] = None
    moving_average: MovingAverage = Field(default_factory=MovingAverage)
    processing_order: ProcessOrder = ProcessOrder.moving_average_normalization


class PixelBinning(BaseModel):
    x0: int
    y0: int
    width: int
    height: int
    bins_size: int


class BinCoordinates(BaseModel):
    """Model for bin coordinates."""

    x0: int
    x1: int
    y0: int
    y1: int
    row_index: int  # Row number in binning grid
    column_index: int  # Column number in binning grid

    @model_validator(mode="after")
    def validate_coordinates(self) -> "BinCoordinates":
        """Validate bin coordinates."""
        if self.x0 >= self.x1:
            raise ValueError("x0 must be less than x1")
        if self.y0 >= self.y1:
            raise ValueError("y0 must be less than y1")
        if self.row_index < 0 or self.column_index < 0:
            raise ValueError("Row and column indices must be non-negative")
        return self


class ThresholdFinder(BaseModel):
    method: Literal["Sliding Average", "Error Function", "Change Point"] = (
        "Sliding Average"
    )
    threshold_width: int = 5


class FittingCriteria(BaseModel):
    """Fit results must be smaller than the threshold to be considered valid, if 'use' is True"""

    lambda_hkl: Dict[Literal["use", "value"], Union[bool, float]] = {
        "use": True,
        "value": 0.010,
    }
    tau: Dict[Literal["use", "value"], Union[bool, float]] = {
        "use": False,
        "value": 0.010,
    }
    sigma: Dict[Literal["use", "value"], Union[bool, float]] = {
        "use": False,
        "value": 0.010,
    }


class RejectionCriteria(BaseModel):
    bragg_peak_lambda_min: Dict[Literal["use", "value"], Union[bool, float]] = {
        "use": True,
        "value": 0.000,
    }
    bragg_peak_lambda_max: Dict[Literal["use", "value"], Union[bool, float]] = {
        "use": True,
        "value": 10.000,
    }


class FittingConfig(BaseModel):
    lambda_min: float
    lambda_max: float
    threshold_finder: ThresholdFinder = Field(default_factory=ThresholdFinder)
    fitting_criteria: FittingCriteria = Field(default_factory=FittingCriteria)
    rejection_criteria: RejectionCriteria = Field(default_factory=RejectionCriteria)


class InterpolationMethod(str, Enum):
    """Supported interpolation methods for strain mapping visualization."""

    NONE = "none"
    NEAREST = "nearest"
    BILINEAR = "bilinear"
    BICUBIC = "bicubic"
    SPLINE16 = "spline16"
    SPLINE36 = "spline36"
    HANNING = "hanning"
    HAMMING = "hamming"
    HERMITE = "hermite"
    KAISER = "kaiser"
    QUADRIC = "quadric"
    CATROM = "catrom"
    GAUSSIAN = "gaussian"
    BESSEL = "bessel"
    MITCHELL = "mitchell"
    SINC = "sinc"
    LANCZOS = "lanczos"


class FigureFormat(str, Enum):
    """Supported figure formats for saving plots."""

    PNG = "png"
    PDF = "pdf"
    SVG = "svg"
    EPS = "eps"


class CsvFormat(BaseModel):
    """Configuration for CSV output format."""

    delimiter: str = ","
    include_metadata_header: bool = True
    metadata_comment_char: str = "#"
    na_rep: str = "null"


class OutputFileConfig(BaseModel):
    """Configuration for output file formats and options."""

    strain_map_format: FigureFormat = FigureFormat.PNG
    fitting_grid_format: FigureFormat = FigureFormat.PDF
    figure_dpi: int = Field(default=300, ge=72, le=1200)
    csv_format: CsvFormat = Field(default_factory=CsvFormat)

    class Config:
        use_enum_values = True


class StrainVisualization(BaseModel):
    """Configuration for strain mapping visualization."""

    interpolation_method: InterpolationMethod = InterpolationMethod.NEAREST
    colormap: str = "viridis"
    alpha: float = Field(
        default=0.5, ge=0.0, le=1.0, description="Transparency for overlay plots"
    )
    display_fit_quality: bool = True

    @field_validator("colormap")
    @classmethod
    def validate_colormap(cls, v):
        """Validate that the colormap exists in matplotlib."""
        if v not in plt.colormaps():
            raise ValueError(
                f"Colormap '{v}' is not available in matplotlib. "
                f"Available colormaps: {', '.join(plt.colormaps())}"
            )
        return v


class StrainMapping(BaseModel):
    """Configuration for strain mapping analysis."""

    d0: Optional[float] = None  # optional override for d0
    quality_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="R-squared threshold for accepting fit results",
    )
    visualization: StrainVisualization = Field(
        default_factory=StrainVisualization, description="Visualization settings"
    )
    output_file_config: OutputFileConfig = Field(
        default_factory=OutputFileConfig, description="Output file format settings"
    )
    save_intermediate_results: bool = False

    @model_validator(mode="after")
    def check_d0_warning(self) -> "StrainMapping":
        """Validate d0 and add warning if using non-standard value."""
        if self.d0 is not None:
            logging.warning(
                "Using user-provided d0. This overrides the value calculated "
                "from material properties."
            )
        return self

    @model_validator(mode="after")
    def ensure_d0_is_positive(self) -> "StrainMapping":
        """Ensure that d0 is positive."""
        if self.d0 is not None and self.d0 <= 0:
            raise ValueError("d0 must be a positive value")
        return self


class CustomMaterial(BaseModel):
    name: str
    lattice: float
    crystal_structure: str
    hkl_lambda_pairs: Dict[Tuple[int, int, int], float]


class Material(BaseModel):
    element: Optional[str] = None
    custom_material: Optional[CustomMaterial] = None

    @model_validator(mode="after")
    def check_material_specification(self) -> "Material":
        if self.element is None and self.custom_material is None:
            raise ValueError("Either 'element' or 'custom_material' must be specified")
        if self.element is not None and self.custom_material is not None:
            raise ValueError(
                "Only one of 'element' or 'custom_material' should be specified"
            )
        return self


class AnalysisConfig(BaseModel):
    material: Material
    pixel_binning: PixelBinning
    fitting: FittingConfig
    strain_mapping: StrainMapping = Field(default_factory=StrainMapping)
    distance_source_detector_in_m: float = Field(
        default=19.855, description="Distance from source to detector in meters"
    )
    detector_offset_in_us: float = Field(
        default=5000, description="Detector offset in microseconds"
    )


class RawData(BaseModel):
    raw_data_dir: Path
    extension: str = ".tif"

    @model_validator(mode="after")
    def check_raw_data_dir(self) -> "RawData":
        if not self.raw_data_dir.exists():
            raise ValueError(f"Directory '{self.raw_data_dir}' does not exist")
        return self

    @model_validator(mode="after")
    def check_raw_data_extension(self) -> "RawData":
        # extension must be ".tif", ".tiff", ".fits"
        if self.extension not in [".tif", ".tiff", ".fits"]:
            raise ValueError("Raw data extension must be '.tif', '.tiff', or '.fits'")
        return self


class OpenBeamData(BaseModel):
    open_beam_data_dir: Path
    extension: str = ".tif"

    @model_validator(mode="after")
    def check_open_beam_data_dir(self) -> "OpenBeamData":
        if not self.open_beam_data_dir.exists():
            raise ValueError(f"Directory '{self.open_beam_data_dir}' does not exist")
        return self

    @model_validator(mode="after")
    def check_open_beam_data_extension(self) -> "OpenBeamData":
        # extension must be ".tif", ".tiff", ".fits"
        if self.extension not in [".tif", ".tiff", ".fits"]:
            raise ValueError(
                "Open beam data extension must be '.tif', '.tiff', or '.fits'"
            )
        return self


class IBeatlesUserConfig(BaseModel):
    raw_data: RawData
    open_beam: Optional[OpenBeamData] = None
    spectra_file_path: Optional[Path] = None
    normalization: NormalizationConfig = Field(default_factory=NormalizationConfig)
    analysis: AnalysisConfig
    output: Dict[str, Path] = Field(...)


# Example usage:
if __name__ == "__main__":
    config_dict = {
        "raw_data": {
            "raw_data_dir": "/tmp",
            "extension": ".tif",
        },
        "open_beam": {
            "open_beam_data_dir": "/tmp",
            "extension": ".tif",
        },
        "spectra_file_path": "/tmp/spectra.txt",
        "output": {
            "normalized_data_dir": "/path/to/normalized_data",
            "analysis_results_dir": "/path/to/analysis_results",
            "strain_results_dir": "/path/to/strain_results",
        },
        "normalization": {
            "sample_background": [{"x0": 0, "y0": 0, "width": 10, "height": 10}],
            "moving_average": {
                "dimension": "3D",
                "size": {"y": 3, "x": 3, "lambda": 3},
            },
        },
        "analysis": {
            # Standard material example
            "material": {"element": "Fe"},
            # Custom material example (commented out)
            # "material": {
            #     "custom_material": {
            #         "name": "Custom Alloy",
            #         "lattice": 3.52,
            #         "crystal_structure": "BCC",
            #         "hkl_lambda_pairs": {(1, 1, 0): 2.8664, (2, 0, 0): 2.0267}
            #     }
            # },
            "pixel_binning": {
                "x0": 0,
                "y0": 0,
                "width": 100,
                "height": 100,
                "bins_size": 5,
            },
            "fitting": {"lambda_min": 0.5, "lambda_max": 5.0},
            "strain_mapping": {
                "d0": 3.52,  # optional, if not provided will use material properties
                "quality_threshold": 0.8,
                "visualization": {
                    "interpolation_method": "nearest",
                    "colormap": "viridis",
                    "alpha": 0.5,
                    "display_fit_quality": True,
                },
                "output_file_config": {
                    "strain_map_format": "png",
                    "fitting_grid_format": "pdf",
                    "figure_dpi": 300,
                    "csv_format": {
                        "delimiter": ",",
                        "include_metadata_header": True,
                        "metadata_comment_char": "#",
                    },
                },
                "save_intermediate_results": False,
            },
            "distance_source_detector_in_m": 19.855,
            "detector_offset_in_us": 9600,
        },
    }

    config = IBeatlesUserConfig(**config_dict)
    print(config.model_dump_json(indent=2))
