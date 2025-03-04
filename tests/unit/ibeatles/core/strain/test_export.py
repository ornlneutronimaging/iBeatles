#!/usr/bin/env python
"""Unit tests for ibeatles.core.export module."""

import pytest
import pandas as pd
from datetime import datetime
from pathlib import Path
from matplotlib import pyplot as plt
from lmfit import Model
from lmfit.model import ModelResult, Parameters

from ibeatles.core.config import (
    OutputFileConfig,
    BinCoordinates,
)
from ibeatles.core.strain.export import (
    generate_output_filename,
    save_strain_map,
    save_fitting_grid,
    save_analysis_results,
)


@pytest.fixture
def output_config():
    """Create default output configuration."""
    return OutputFileConfig()


@pytest.fixture
def mock_fit_result():
    """Create a mock ModelResult."""
    model = Model(lambda x: x)
    params = Parameters()
    params.add("bragg_edge_wavelength", value=2.8664)

    result = ModelResult(model, params)
    result.best_values = {"bragg_edge_wavelength": 2.8664}
    result.rsquared = 0.98
    result.chisqr = 0.02
    return result


@pytest.fixture
def mock_bin_coordinates():
    """Create mock bin coordinates."""
    return BinCoordinates(x0=0, y0=0, x1=10, y1=10, row_index=0, column_index=0)


@pytest.fixture
def mock_strain_results():
    """Create mock strain results."""
    return {"0": {"strain": 0.001, "error": 0.0001, "quality": 0.98}}


@pytest.fixture
def mock_metadata():
    """Create mock metadata."""
    return {
        "material_name": "Fe",
        "d0": 3.52,
        "distance_source_detector": 19.855,
        "detector_offset": 9600,
    }


def test_generate_output_filename():
    """Test filename generation with various inputs."""
    # Test with fixed timestamp
    timestamp = datetime(2024, 1, 8, 15, 30, 42)
    filename = generate_output_filename(
        "fe_sample", "strain_map", "png", timestamp=timestamp
    )
    assert filename == Path("fe_sample_strain_map_20240108_153042.png")

    # Test with Path input
    filename = generate_output_filename(
        Path("data/fe_sample"), "strain_map", "png", timestamp=timestamp
    )
    assert filename == Path("fe_sample_strain_map_20240108_153042.png")

    # Test current timestamp (should not raise error)
    filename = generate_output_filename("fe_sample", "strain_map", "png")
    assert isinstance(filename, Path)


def test_save_strain_map(output_config, tmp_path):
    """Test saving strain map figure."""
    # Create a simple figure
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])

    output_path = tmp_path / "strain_map.png"

    # Test successful save
    save_strain_map(fig, output_path, output_config)
    assert output_path.exists()

    # Test file exists error
    with pytest.raises(ValueError, match="already exists"):
        save_strain_map(fig, output_path, output_config)

    plt.close(fig)


def test_save_fitting_grid(output_config, tmp_path):
    """Test saving fitting grid figure."""
    # Create a simple figure
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 2, 3])

    output_path = tmp_path / "fitting_grid.pdf"

    # Test successful save
    save_fitting_grid(fig, output_path, output_config)
    assert output_path.exists()

    # Test file exists error
    with pytest.raises(ValueError, match="already exists"):
        save_fitting_grid(fig, output_path, output_config)

    plt.close(fig)


def test_save_analysis_results(
    output_config,
    tmp_path,
    mock_fit_result,
    mock_bin_coordinates,
    mock_strain_results,
    mock_metadata,
):
    """Test saving analysis results to CSV."""
    output_path = tmp_path / "results.csv"

    fit_results = {"0": mock_fit_result}
    bin_coordinates = [mock_bin_coordinates]

    # Test with metadata header
    save_analysis_results(
        fit_results,
        bin_coordinates,
        mock_strain_results,
        mock_metadata,
        output_path,
        output_config,
    )

    assert output_path.exists()

    # Read the file and check content
    with open(output_path) as f:
        content = f.readlines()

    # Check metadata header
    assert content[0].startswith("#")
    assert "Material: Fe" in content[1]
    assert "d0: 3.52" in content[2]

    # Check CSV data
    df = pd.read_csv(output_path, comment="#")
    assert len(df) == 1  # One row
    assert "bin_id" in df.columns
    assert "strain" in df.columns
    assert df.loc[0, "lambda_hkl"] == pytest.approx(2.8664)
    assert df.loc[0, "r_squared"] == pytest.approx(0.98)


def test_save_analysis_results_no_header(
    output_config,
    tmp_path,
    mock_fit_result,
    mock_bin_coordinates,
    mock_strain_results,
    mock_metadata,
):
    """Test saving analysis results without metadata header."""
    output_path = tmp_path / "results_no_header.csv"

    # Modify config to disable header
    output_config.csv_format.include_metadata_header = False

    fit_results = {"0": mock_fit_result}
    bin_coordinates = [mock_bin_coordinates]

    save_analysis_results(
        fit_results,
        bin_coordinates,
        mock_strain_results,
        mock_metadata,
        output_path,
        output_config,
    )

    # Read the file and check content
    with open(output_path) as f:
        content = f.readlines()

    # First line should be CSV header, not metadata
    assert not content[0].startswith("#")
    assert "bin_id" in content[0]


def test_save_analysis_results_custom_delimiter(
    output_config,
    tmp_path,
    mock_fit_result,
    mock_bin_coordinates,
    mock_strain_results,
    mock_metadata,
):
    """Test saving analysis results with custom delimiter."""
    output_path = tmp_path / "results_semicolon.csv"

    # Modify config to use semicolon delimiter
    output_config.csv_format.delimiter = ";"

    fit_results = {"0": mock_fit_result}
    bin_coordinates = [mock_bin_coordinates]

    save_analysis_results(
        fit_results,
        bin_coordinates,
        mock_strain_results,
        mock_metadata,
        output_path,
        output_config,
    )

    # Read with pandas and check delimiter
    df = pd.read_csv(output_path, comment="#", sep=";")
    assert len(df) == 1


def test_failed_fit_results(
    output_config, tmp_path, mock_bin_coordinates, mock_strain_results, mock_metadata
):
    """Test handling of failed fits in results."""
    output_path = tmp_path / "results_failed.csv"

    # Include a None result to simulate failed fit
    fit_results = {"0": None}
    bin_coordinates = [mock_bin_coordinates]

    save_analysis_results(
        fit_results,
        bin_coordinates,
        mock_strain_results,
        mock_metadata,
        output_path,
        output_config,
    )

    # Should create file but with no data rows
    with pytest.raises(pd.errors.EmptyDataError):
        pd.read_csv(output_path, comment="#")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
