#!/usr/bin/env python
"""Unit tests for the normalization process."""

import numpy as np
import pytest
from pathlib import Path
import tempfile

from ibeatles.core.processing.normalization import normalize_data
from ibeatles.core.config import (
    IBeatlesUserConfig,
    RawData,
    OpenBeamData,
    NormalizationConfig,
    MovingAverage,
    AnalysisConfig,
    Material,
    PixelBinning,
    FittingConfig,
    StrainMapping,
    KernelType,
    SampleBackground,
)


@pytest.fixture
def sample_data():
    return np.random.rand(5, 10, 10)  # 5 images of 10x10


@pytest.fixture
def ob_data():
    return np.random.rand(5, 10, 10)  # 5 images of 10x10


@pytest.fixture
def time_spectra(temp_dir):
    file_path = temp_dir / "time_spectra.txt"
    file_path.write_text("Dummy time spectra content")
    return {
        "filename": str(file_path),
        "short_filename": file_path.name,
        "tof_array": np.linspace(0, 100, 5),
        "counts_array": np.random.rand(5),
        "lambda_array": np.linspace(0.5, 5, 5),
    }


@pytest.fixture
def config(temp_dir):
    raw_data_dir = temp_dir / "raw_data"
    raw_data_dir.mkdir()
    ob_data_dir = temp_dir / "ob_data"
    ob_data_dir.mkdir()
    output_dir = temp_dir / "output"
    output_dir.mkdir()

    return IBeatlesUserConfig(
        raw_data=RawData(raw_data_dir=str(raw_data_dir), raw_data_extension=".tif"),
        open_beam=OpenBeamData(
            open_beam_data_dir=str(ob_data_dir), open_beam_data_extension=".tif"
        ),
        normalization=NormalizationConfig(
            sample_background=SampleBackground(x0=0, y0=0, width=5, height=5),
            moving_average=MovingAverage(
                active=True, dimension="2D", size={"y": 3, "x": 3}, type=KernelType.box
            ),
            processing_order="Moving average, Normalization",
        ),
        analysis=AnalysisConfig(
            material=Material(element="Fe"),
            pixel_binning=PixelBinning(x0=0, y0=0, width=10, height=10, bins_size=1),
            fitting=FittingConfig(lambda_min=0.5, lambda_max=5.0),
            strain_mapping=StrainMapping(),
            distance_source_detector_in_m=10.0,
            detector_offset_in_us=4500.0,
        ),
        output={
            "normalized_data_dir": str(output_dir),
            "analysis_results_dir": str(output_dir),
        },
    )


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


def test_normalize_data_with_ob(sample_data, ob_data, time_spectra, config, temp_dir):
    """
    Test normalization process with both sample and open beam data.
    This test checks if:
    1. The normalization process runs without errors
    2. The output data has the expected shape
    3. The output folder is created and contains the expected files
    4. The time spectra file is copied to the output folder
    """
    normalized_data, output_path = normalize_data(
        sample_data, ob_data, time_spectra, config, str(temp_dir)
    )

    assert (
        np.array(normalized_data).shape == sample_data.shape
    ), "Normalized data shape should match input data shape"
    assert Path(output_path).exists(), "Output folder should be created"
    assert Path(output_path).is_dir(), "Output path should be a directory"
    assert (
        Path(output_path) / time_spectra["short_filename"]
    ).exists(), "Time spectra file should be copied to output folder"

    # Check if normalized data files were created (assuming NeuNorm creates separate files)
    normalized_files = list(Path(output_path).glob("*normalized*.tif"))
    assert len(normalized_files) > 0, "Normalized data files should be created"


def test_normalize_data_without_ob(sample_data, time_spectra, config, temp_dir):
    """
    Test normalization process without open beam data.
    This test checks if:
    1. The normalization process runs without errors when open beam data is not provided
    2. The output data has the expected shape
    """
    normalized_data, output_path = normalize_data(
        sample_data, None, time_spectra, config, str(temp_dir)
    )

    assert (
        np.array(normalized_data).shape == sample_data.shape
    ), "Normalized data shape should match input data shape"
    assert Path(output_path).exists(), "Output folder should be created"


def test_normalize_data_without_moving_average(
    sample_data, ob_data, time_spectra, config, temp_dir
):
    """
    Test normalization process with moving average disabled.
    This test checks if:
    1. The normalization process runs without errors when moving average is disabled
    2. The output data has the expected shape
    """
    config.normalization.moving_average.active = False
    normalized_data, _ = normalize_data(
        sample_data, ob_data, time_spectra, config, str(temp_dir)
    )

    assert (
        np.array(normalized_data).shape == sample_data.shape
    ), "Normalized data shape should match input data shape"


def test_normalize_data_with_different_processing_order(
    sample_data, ob_data, time_spectra, config, temp_dir
):
    """
    Test normalization process with a different processing order.
    This test checks if:
    1. The normalization process runs without errors when the processing order is changed
    2. The output data has the expected shape
    """
    config.normalization.processing_order = "Normalization, Moving Average"
    normalized_data, _ = normalize_data(
        sample_data, ob_data, time_spectra, config, str(temp_dir)
    )

    assert (
        np.array(normalized_data).shape == sample_data.shape
    ), "Normalized data shape should match input data shape"
