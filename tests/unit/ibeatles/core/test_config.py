#!/usr/bin/env python
"""Unit test for ibeatles.core.config module."""

import pytest
from pathlib import Path
import tempfile
import os
from ibeatles.core.config import IBeatlesUserConfig, CustomMaterial


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@pytest.fixture
def valid_config_dict(temp_dir):
    raw_data_dir = os.path.join(temp_dir, "raw_data")
    open_beam_dir = os.path.join(temp_dir, "open_beam")
    os.makedirs(raw_data_dir)
    os.makedirs(open_beam_dir)

    return {
        "raw_data": {
            "raw_data_dir": raw_data_dir,
            "raw_data_extension": ".tif",
        },
        "open_beam": {
            "open_beam_data_dir": open_beam_dir,
            "open_beam_data_extension": ".tif",
        },
        "spectra_file_path": os.path.join(temp_dir, "spectra.txt"),
        "output": {
            "normalized_data_dir": os.path.join(temp_dir, "normalized_data"),
            "analysis_results_dir": os.path.join(temp_dir, "analysis_results"),
        },
        "normalization": {
            "sample_background": [{"x0": 0, "y0": 0, "width": 10, "height": 10}],
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
            "distance_source_detector_in_m": 19.855,
            "detector_offset_in_us": 9600,
        },
    }


def test_valid_config(valid_config_dict):
    config = IBeatlesUserConfig(**valid_config_dict)
    assert isinstance(config, IBeatlesUserConfig)


def test_default_values(temp_dir):
    raw_data_dir = os.path.join(temp_dir, "raw_data")
    os.makedirs(raw_data_dir)

    minimal_config = {
        "raw_data": {"raw_data_dir": raw_data_dir},
        "output": {
            "normalized_data_dir": os.path.join(temp_dir, "normalized"),
            "analysis_results_dir": os.path.join(temp_dir, "analysis"),
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
    assert config.raw_data.raw_data_extension == ".tif"  # Check default extension


def test_custom_material(temp_dir):
    raw_data_dir = os.path.join(temp_dir, "raw_data")
    os.makedirs(raw_data_dir)

    config_dict = {
        "raw_data": {"raw_data_dir": raw_data_dir},
        "output": {
            "normalized_data_dir": os.path.join(temp_dir, "normalized"),
            "analysis_results_dir": os.path.join(temp_dir, "analysis"),
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


def test_invalid_config(temp_dir):
    invalid_config = {
        "raw_data": {
            "raw_data_dir": os.path.join(temp_dir, "non_existent_dir")
        },  # Non-existent directory
        "output": {
            "normalized_data_dir": os.path.join(temp_dir, "normalized"),
            "analysis_results_dir": os.path.join(temp_dir, "analysis"),
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


def test_invalid_material_specification(temp_dir):
    raw_data_dir = os.path.join(temp_dir, "raw_data")
    os.makedirs(raw_data_dir)

    invalid_material_config = {
        "raw_data": {"raw_data_dir": raw_data_dir},
        "output": {
            "normalized_data_dir": os.path.join(temp_dir, "normalized"),
            "analysis_results_dir": os.path.join(temp_dir, "analysis"),
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


def test_path_conversion(temp_dir):
    raw_data_dir = os.path.join(temp_dir, "raw_data")
    os.makedirs(raw_data_dir)

    config_dict = {
        "raw_data": {"raw_data_dir": raw_data_dir},
        "output": {
            "normalized_data_dir": os.path.join(temp_dir, "normalized"),
            "analysis_results_dir": os.path.join(temp_dir, "analysis"),
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
    assert isinstance(config.raw_data.raw_data_dir, Path)
    assert isinstance(config.output["normalized_data_dir"], Path)
    assert isinstance(config.output["analysis_results_dir"], Path)


def test_invalid_extension(temp_dir):
    raw_data_dir = os.path.join(temp_dir, "raw_data")
    os.makedirs(raw_data_dir)

    invalid_extension_config = {
        "raw_data": {
            "raw_data_dir": raw_data_dir,
            "raw_data_extension": ".jpg",  # Invalid extension
        },
        "output": {
            "normalized_data_dir": os.path.join(temp_dir, "normalized"),
            "analysis_results_dir": os.path.join(temp_dir, "analysis"),
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
        IBeatlesUserConfig(**invalid_extension_config)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
