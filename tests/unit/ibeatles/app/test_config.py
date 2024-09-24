#!/usr/bin/env python
"""Uint test for user config model."""

import pytest
from pathlib import Path
from ibeatles.app.config import IBeatlesUserConfig, CustomMaterial


@pytest.fixture
def valid_config_dict():
    return {
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
            "material": {"element": "Fe"},
            "pixel_binning": {
                "x0": 0,
                "y0": 0,
                "width": 100,
                "height": 100,
                "bins_size": 5,
            },
            "fitting": {"lambda_min": 0.5, "lambda_max": 5.0},
            "strain_mapping": {"d0": 3.52},
        },
    }


def test_valid_config(valid_config_dict):
    config = IBeatlesUserConfig(**valid_config_dict)
    assert isinstance(config, IBeatlesUserConfig)


def test_default_values():
    minimal_config = {
        "input": {"raw_data_dir": "/path/to/raw_data"},
        "output": {
            "normalized_data_dir": "/path/to/normalized",
            "analysis_results_dir": "/path/to/analysis",
        },
        "analysis": {
            "material": {"element": "Fe"},
            "pixel_binning": {
                "x0": 0,
                "y0": 0,
                "width": 100,
                "height": 100,
                "bins_size": 5,
            },
            "fitting": {"lambda_min": 0.5, "lambda_max": 5.0},
        },
    }
    config = IBeatlesUserConfig(**minimal_config)
    assert config.normalization.processing_order == "Moving average, Normalization"
    assert config.normalization.moving_average.dimension == "2D"


def test_custom_material():
    config_dict = {
        "input": {"raw_data_dir": "/path/to/raw_data"},
        "output": {
            "normalized_data_dir": "/path/to/normalized",
            "analysis_results_dir": "/path/to/analysis",
        },
        "analysis": {
            "material": {
                "custom_material": {
                    "name": "Custom Alloy",
                    "lattice": 3.52,
                    "crystal_structure": "BCC",
                    "hkl_lambda_pairs": {(1, 1, 0): 2.8664, (2, 0, 0): 2.0267},
                }
            },
            "pixel_binning": {
                "x0": 0,
                "y0": 0,
                "width": 100,
                "height": 100,
                "bins_size": 5,
            },
            "fitting": {"lambda_min": 0.5, "lambda_max": 5.0},
        },
    }
    config = IBeatlesUserConfig(**config_dict)
    assert isinstance(config.analysis.material.custom_material, CustomMaterial)
    assert config.analysis.material.custom_material.name == "Custom Alloy"


def test_invalid_config():
    invalid_config = {
        "input": {},  # Missing required raw_data_dir
        "output": {
            "normalized_data_dir": "/path/to/normalized",
            "analysis_results_dir": "/path/to/analysis",
        },
        "analysis": {
            "material": {"element": "Fe"},
            "pixel_binning": {
                "x0": 0,
                "y0": 0,
                "width": 100,
                "height": 100,
                "bins_size": 5,
            },
            "fitting": {"lambda_min": 0.5, "lambda_max": 5.0},
        },
    }
    with pytest.raises(ValueError):
        IBeatlesUserConfig(**invalid_config)


def test_invalid_material_specification():
    invalid_material_config = {
        "input": {"raw_data_dir": "/path/to/raw_data"},
        "output": {
            "normalized_data_dir": "/path/to/normalized",
            "analysis_results_dir": "/path/to/analysis",
        },
        "analysis": {
            "material": {
                "element": "Fe",
                "custom_material": {},
            },  # Both element and custom_material specified
            "pixel_binning": {
                "x0": 0,
                "y0": 0,
                "width": 100,
                "height": 100,
                "bins_size": 5,
            },
            "fitting": {"lambda_min": 0.5, "lambda_max": 5.0},
        },
    }
    with pytest.raises(ValueError):
        IBeatlesUserConfig(**invalid_material_config)


def test_path_conversion():
    config_dict = {
        "input": {"raw_data_dir": "/path/to/raw_data"},
        "output": {
            "normalized_data_dir": "/path/to/normalized",
            "analysis_results_dir": "/path/to/analysis",
        },
        "analysis": {
            "material": {"element": "Fe"},
            "pixel_binning": {
                "x0": 0,
                "y0": 0,
                "width": 100,
                "height": 100,
                "bins_size": 5,
            },
            "fitting": {"lambda_min": 0.5, "lambda_max": 5.0},
        },
    }
    config = IBeatlesUserConfig(**config_dict)
    assert isinstance(config.input["raw_data_dir"], Path)
    assert isinstance(config.output["normalized_data_dir"], Path)
    assert isinstance(config.output["analysis_results_dir"], Path)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
