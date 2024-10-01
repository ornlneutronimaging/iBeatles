import os
import pytest
import numpy as np
from unittest.mock import patch, Mock, call
import time
from ibeatles.core.io.data_loading import (
    cleanup_list_of_files,
    load_image,
    load_tiff,
    load_fits,
    process_tiff_metadata,
    process_fits_metadata,
    load_data_from_folder,
    get_time_spectra_filename,
    load_time_spectra,
)


@pytest.fixture
def sample_tiff_data():
    return np.random.rand(100, 100)


@pytest.fixture
def sample_fits_data():
    return np.random.rand(100, 100)


def test_cleanup_list_of_files():
    files = [
        "file1.txt",
        "file2.txt",
        "file3.txt",
        "file4.txt",
        "file5.txt",
        "file6.txt",
    ]
    assert cleanup_list_of_files(files) == files

    files_2 = [
        "file1.txt",
        "file2.txt",
        "file3.txt",
        "file4.txt",
        "file5.txt",
        "longfile6.txt",
    ]
    assert cleanup_list_of_files(files_2) == [
        "file1.txt",
        "file2.txt",
        "file3.txt",
        "file4.txt",
        "file5.txt",
    ]

    files_3 = [
        "file1.txt",
        "longfile2.txt",
        "file3.txt",
        "file4.txt",
        "file5.txt",
        "file6.txt",
        "file7.txt",
    ]
    with pytest.raises(ValueError):
        cleanup_list_of_files(files_3)


@patch("ibeatles.core.io.data_loading.load_tiff")
@patch("ibeatles.core.io.data_loading.load_fits")
def test_load_image(mock_load_fits, mock_load_tiff):
    load_image("image.tif")
    mock_load_tiff.assert_called_once()

    load_image("image.fits")
    mock_load_fits.assert_called_once()

    with pytest.raises(ValueError):
        load_image("image.jpg")


@patch("PIL.Image.open")
def test_load_tiff(mock_image_open, sample_tiff_data):
    mock_image = mock_image_open.return_value.__enter__.return_value
    mock_image.tag_v2.as_dict.return_value = {}
    mock_image.__array__ = Mock(return_value=sample_tiff_data)

    data, metadata = load_tiff("image.tif")
    assert data.shape == (100, 100)
    assert isinstance(metadata, dict)


@patch("astropy.io.fits.open")
@patch("os.path.getmtime")
def test_load_fits(mock_getmtime, mock_fits_open, sample_fits_data):
    # Mock the file modification time
    mock_getmtime.return_value = str(time.time())  # Current time

    mock_hdul = mock_fits_open.return_value.__enter__.return_value
    mock_hdul[0].data = sample_fits_data
    mock_hdul[0].header = {"EXPOSURE": 100, "NAXIS1": 100, "NAXIS2": 100, "BITPIX": 32}
    # Note: We're not setting 'DATE' in the header to test the fallback behavior

    data, metadata = load_fits("image.fits")

    assert np.array_equal(data, sample_fits_data)
    assert isinstance(metadata, dict)
    assert "acquisition_time" in metadata
    assert isinstance(
        metadata["acquisition_time"]["value"], str
    )  # Should be a time string
    assert metadata["acquisition_duration"]["value"] == 100
    assert metadata["image_size"]["value"] == "100 x 100"
    assert metadata["image_type"]["value"] == "32 bits"
    assert "min_counts" in metadata
    assert "max_counts" in metadata

    # Verify that getmtime was called when 'DATE' was not in the header
    mock_getmtime.assert_called_once_with("image.fits")


def test_process_tiff_metadata():
    metadata = {
        65000: [1234567890],
        65021: ["Duration: 100"],
        65028: ["Width: 100"],
        65029: ["Height: 100"],
        258: [16],
    }
    data = np.zeros((100, 100))
    processed = process_tiff_metadata(metadata, data, "image.tif")
    assert isinstance(processed, dict)
    assert "acquisition_time" in processed
    assert "image_size" in processed
    assert "image_type" in processed


@patch("os.path.getmtime")
def test_process_fits_metadata(mock_getmtime):
    # Mock the file modification time
    mock_timestamp = time.time()
    mock_getmtime.return_value = mock_timestamp

    header = {
        "DATE": "2024-01-01",
        "EXPOSURE": 100,
        "NAXIS1": 100,
        "NAXIS2": 100,
        "BITPIX": 16,
    }
    data = np.zeros((100, 100))

    processed = process_fits_metadata(header, data, "image.fits")

    assert isinstance(processed, dict)
    assert processed["acquisition_time"]["value"] == "2024-01-01"
    assert processed["acquisition_duration"]["value"] == 100
    assert processed["image_size"]["value"] == "100 x 100"
    assert processed["image_type"]["value"] == "16 bits"
    assert processed["min_counts"]["value"] == 0
    assert processed["max_counts"]["value"] == 0

    # Test fallback behavior when 'DATE' is not in the header
    header_without_date = header.copy()
    del header_without_date["DATE"]

    processed_without_date = process_fits_metadata(
        header_without_date, data, "image.fits"
    )

    assert isinstance(processed_without_date, dict)
    assert processed_without_date["acquisition_time"]["value"] == mock_timestamp


@patch("ibeatles.core.io.data_loading.glob.glob")
@patch("ibeatles.core.io.data_loading.load_image")
def test_load_data_from_folder(mock_load_image, mock_glob):
    mock_glob.return_value = ["image1.tif", "image2.tif"]
    mock_load_image.return_value = (np.zeros((100, 100)), {})

    result = load_data_from_folder("/path/to/folder")
    assert "data" in result
    assert "metadata" in result
    assert "file_list" in result
    assert "folder" in result
    assert "size" in result


@patch("ibeatles.core.io.data_loading.glob.glob")
@patch("os.path.exists")
def test_get_time_spectra_filename(mock_exists, mock_glob):
    # Test when file is found
    mock_glob.return_value = ["/path/to/folder/file_Spectra.txt"]
    mock_exists.return_value = True
    result = get_time_spectra_filename("/path/to/folder")
    assert result == "/path/to/folder/file_Spectra.txt"

    # Test when no files match the pattern
    mock_glob.return_value = []
    result = get_time_spectra_filename("/path/to/folder")
    assert result == ""

    # Test when file is found but doesn't exist
    mock_glob.return_value = ["/path/to/folder/file_Spectra.txt"]
    mock_exists.return_value = False
    result = get_time_spectra_filename("/path/to/folder")
    assert result == ""

    # Verify the correct arguments were passed to glob
    mock_glob.assert_called_with(os.path.join("/path/to/folder", "*_Spectra.txt"))


@patch("ibeatles.core.io.data_loading.TOF")
@patch("ibeatles.core.io.data_loading.Experiment")
@patch("os.path.isfile")
def test_load_time_spectra(mock_isfile, mock_experiment, mock_tof):
    # Test successful loading
    mock_isfile.return_value = True

    mock_tof_instance = mock_tof.return_value
    mock_tof_instance.tof_array = np.array([1, 2, 3])
    mock_tof_instance.counts_array = np.array([10, 20, 30])

    mock_exp_instance = mock_experiment.return_value
    mock_exp_instance.lambda_array = np.array([0.1, 0.2, 0.3])

    result = load_time_spectra(
        file_path="spectra.txt",
        distance_source_detector_m=10,
        detector_offset_micros=5000,
    )

    assert result["filename"] == "spectra.txt"
    assert result["short_filename"] == "spectra.txt"
    np.testing.assert_array_equal(result["tof_array"], np.array([1, 2, 3]))
    np.testing.assert_array_equal(result["counts_array"], np.array([10, 20, 30]))
    np.testing.assert_array_equal(result["lambda_array"], np.array([0.1, 0.2, 0.3]))

    mock_tof.assert_called_once_with(filename="spectra.txt")

    # Use call() to create an expected call object
    expected_call = call(
        tof=np.array([1, 2, 3]),
        distance_source_detector_m=10,
        detector_offset_micros=5000,
    )

    # Assert that mock_experiment was called once with the expected arguments
    assert mock_experiment.call_count == 1
    actual_call = mock_experiment.call_args

    # Compare non-array arguments
    assert (
        actual_call.kwargs["distance_source_detector_m"]
        == expected_call.kwargs["distance_source_detector_m"]
    )
    assert (
        actual_call.kwargs["detector_offset_micros"]
        == expected_call.kwargs["detector_offset_micros"]
    )

    # Compare array argument
    np.testing.assert_array_equal(
        actual_call.kwargs["tof"], expected_call.kwargs["tof"]
    )

    # Test file not found scenario
    mock_isfile.return_value = False
    with pytest.raises(FileNotFoundError):
        load_time_spectra(
            file_path="nonexistent.txt",
            distance_source_detector_m=10,
            detector_offset_micros=5000,
        )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
