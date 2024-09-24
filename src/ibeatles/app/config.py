"""Pydantic configuration model for CLI and GUI application settings (user)"""

from typing import Dict, Optional, Union, Tuple, Literal
from pydantic import BaseModel, Field, model_validator
from pathlib import Path


class SampleBackground(BaseModel):
    x0: float
    y0: float
    width: float
    height: float


class MovingAverage(BaseModel):
    active: bool = True
    dimension: Literal["2D", "3D"] = "2D"
    size: Union[Dict[str, int], Tuple[int, int], Tuple[int, int, int]] = Field(
        default_factory=lambda: {"y": 3, "x": 3}
    )
    type: Literal["Box", "Gaussian"] = "Box"

    @model_validator(mode="after")
    def check_size(self) -> "MovingAverage":
        if self.dimension == "2D":
            if isinstance(self.size, dict):
                assert set(self.size.keys()) == {
                    "y",
                    "x",
                }, "2D size must have 'y' and 'x' keys"
            elif isinstance(self.size, tuple):
                assert len(self.size) == 2, "2D size tuple must have 2 elements"
        elif self.dimension == "3D":
            if isinstance(self.size, dict):
                assert set(self.size.keys()) == {
                    "y",
                    "x",
                    "lambda",
                }, "3D size must have 'y', 'x', and 'lambda' keys"
            elif isinstance(self.size, tuple):
                assert len(self.size) == 3, "3D size tuple must have 3 elements"
        return self


class NormalizationConfig(BaseModel):
    sample_background: Optional[SampleBackground] = None
    moving_average: MovingAverage = Field(default_factory=MovingAverage)
    processing_order: Literal[
        "Moving average, Normalization", "Normalization, Moving Average"
    ] = "Moving average, Normalization"


class PixelBinning(BaseModel):
    x0: int
    y0: int
    width: int
    height: int
    bins_size: int


class ThresholdFinder(BaseModel):
    method: Literal["Sliding Average", "Error Function", "Change Point"] = (
        "Sliding Average"
    )
    threshold_width: int = 5


class FittingCriteria(BaseModel):
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


class StrainMapping(BaseModel):
    d0: Optional[float] = None
    output: Optional[Path] = None


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


class IBeatlesUserConfig(BaseModel):
    input: Dict[str, Path] = Field(...)
    normalization: NormalizationConfig = Field(default_factory=NormalizationConfig)
    analysis: AnalysisConfig
    output: Dict[str, Path] = Field(...)

    @model_validator(mode="after")
    def check_input_paths(self) -> "IBeatlesUserConfig":
        if "raw_data_dir" not in self.input:
            raise ValueError("'raw_data_dir' is mandatory in input paths")
        return self


# Example usage:
if __name__ == "__main__":
    config_dict = {
        "input": {
            "raw_data_dir": "/path/to/raw_data",
            "open_beam_data_dir": "/path/to/open_beam",
            "spectra_file_path": "/path/to/spectra.csv",
        },
        "output": {
            "normalized_data_dir": "/path/to/normalized_data",
            "analysis_results_dir": "/path/to/analysis_results",
        },
        "normalization": {
            "sample_background": {"x0": 0, "y0": 0, "width": 10, "height": 10},
            "moving_average": {
                "dimension": "3D",
                "size": {"y": 3, "x": 3, "lambda": 3},
            },
        },
        "analysis": {
            "material": {"element": "Fe"},  # For predefined element
            # Alternatively, for custom material:
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
            "strain_mapping": {"d0": 3.52, "output": "/path/to/strain_output"},
        },
    }

    config = IBeatlesUserConfig(**config_dict)
    print(config.model_dump_json(indent=2))
