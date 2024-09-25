"""Data loading functions."""

#!/usr/bin/env python
import os
import glob
import numpy as np
from typing import List, Dict, Any, Tuple
from pathlib import Path
from astropy.io import fits
from PIL import Image
from neutronbraggedge.experiment_handler.tof import TOF
from neutronbraggedge.experiment_handler.experiment import Experiment


def cleanup_list_of_files(list_of_files: List[str], base_number: int = 5) -> List[str]:
    """
    Keep only the files that have the same number of characters as the first n files.

    Parameters
    ----------
    list_of_files : List[str]
        List of file names to clean up.
    base_number : int, optional
        Number of files to use as a base for comparison (default is 5).

    Returns
    -------
    List[str]
        Cleaned list of file names.

    Raises
    ------
    ValueError
        If the format of the input files does not match.
    """
    if len(list_of_files) == 0:
        return []

    len_base_files = [len(file) for file in list_of_files[:base_number]]

    # Make sure all the lengths of the base number files match
    if len(set(len_base_files)) > 1:
        raise ValueError("Format Input File Do Not Match!")

    len_file = len_base_files[0]
    return [file for file in list_of_files if len(file) == len_file]


def load_image(file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Load an image file and return its data and metadata.

    Parameters
    ----------
    file_path : str
        Path to the image file.

    Returns
    -------
    Tuple[np.ndarray, Dict[str, Any]]
        A tuple containing the image data as a numpy array and a dictionary of metadata.
    """
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension in [".tiff", ".tif"]:
        return load_tiff(file_path)
    elif file_extension == ".fits":
        return load_fits(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}")


def load_tiff(file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Load a TIFF image file.

    Parameters
    ----------
    file_path : str
        Path to the TIFF file.

    Returns
    -------
    Tuple[np.ndarray, Dict[str, Any]]
        A tuple containing the image data as a numpy array and a dictionary of metadata.
    """
    with Image.open(file_path) as img:
        data = np.array(img)
        # Replace NaN and Inf values with 0 to avoid computation issues
        data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)
        metadata = img.tag_v2.as_dict() if hasattr(img, "tag_v2") else {}

    return data, process_tiff_metadata(metadata, data, file_path)


def load_fits(file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Load a FITS image file.

    Parameters
    ----------
    file_path : str
        Path to the FITS file.

    Returns
    -------
    Tuple[np.ndarray, Dict[str, Any]]
        A tuple containing the image data as a numpy array and a dictionary of metadata.
    """
    with fits.open(file_path) as hdul:
        data = hdul[0].data
        # Replace NaN and Inf values with 0 to avoid computation issues
        data = np.nan_to_num(data, nan=0, posinf=0, neginf=0)
        header = hdul[0].header

    return data, process_fits_metadata(header, data, file_path)


def process_tiff_metadata(
    metadata: Dict[str, Any], data: np.ndarray, file_path: str
) -> Dict[str, Dict[str, Any]]:
    """
    Process TIFF metadata and extract relevant information.

    Parameters
    ----------
    metadata : Dict[str, Any]
        Raw metadata dictionary from the TIFF file.
    data : np.ndarray
        Image data.
    file_path : str
        Path to the TIFF file.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        Processed metadata dictionary.
    """
    processed_metadata = {
        "acquisition_duration": {"name": "Acquisition Duration", "value": 0},
        "acquisition_time": {"name": "Acquisition Time", "value": ""},
        "image_size": {"name": "Image(s) Size", "value": ""},
        "image_type": {"name": "Image Type", "value": ""},
        "min_counts": {"name": "min counts", "value": 0},
        "max_counts": {"name": "max counts", "value": 0},
    }

    # Acquisition time
    acquisition_time = metadata.get(65000, [metadata.get(279, [None])])[0]
    if acquisition_time is None:
        acquisition_time = os.path.getmtime(file_path)
    processed_metadata["acquisition_time"]["value"] = acquisition_time

    # Acquisition duration
    acquisition_duration = metadata.get(65021, ["N/A"])[0]
    if isinstance(acquisition_duration, str) and ":" in acquisition_duration:
        acquisition_duration = acquisition_duration.split(":")[1]
    processed_metadata["acquisition_duration"]["value"] = acquisition_duration

    # Image size
    size_x = metadata.get(65028, [metadata.get(256, [data.shape[1]])])[0]
    size_y = metadata.get(65029, [metadata.get(257, [data.shape[0]])])[0]
    if isinstance(size_x, str) and ":" in size_x:
        size_x = size_x.split(":")[1]
    if isinstance(size_y, str) and ":" in size_y:
        size_y = size_y.split(":")[1]
    processed_metadata["image_size"]["value"] = f"{size_x} x {size_y}"

    # Image type
    bits = metadata.get(258, [data.dtype.itemsize * 8])[0]
    processed_metadata["image_type"]["value"] = f"{bits} bits"

    # Min and max counts
    processed_metadata["min_counts"]["value"] = np.min(data)
    processed_metadata["max_counts"]["value"] = np.max(data)

    return processed_metadata


def process_fits_metadata(
    header: fits.Header, data: np.ndarray, file_path: str
) -> Dict[str, Dict[str, Any]]:
    """
    Process FITS metadata and extract relevant information.

    Parameters
    ----------
    header : fits.Header
        FITS file header.
    data : np.ndarray
        Image data.
    file_path : str
        Path to the FITS file.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        Processed metadata dictionary.
    """
    processed_metadata = {
        "acquisition_duration": {"name": "Acquisition Duration", "value": 0},
        "acquisition_time": {"name": "Acquisition Time", "value": ""},
        "image_size": {"name": "Image(s) Size", "value": ""},
        "image_type": {"name": "Image Type", "value": ""},
        "min_counts": {"name": "min counts", "value": 0},
        "max_counts": {"name": "max counts", "value": 0},
    }

    processed_metadata["acquisition_time"]["value"] = header.get(
        "DATE", os.path.getmtime(file_path)
    )
    processed_metadata["acquisition_duration"]["value"] = header.get(
        "EXPOSURE", header.get("TIMEBIN", "N/A")
    )
    processed_metadata["image_size"]["value"] = (
        f"{header.get('NAXIS1', data.shape[1])} x {header.get('NAXIS2', data.shape[0])}"
    )
    processed_metadata["image_type"]["value"] = (
        f"{header.get('BITPIX', data.dtype.itemsize * 8)} bits"
    )
    processed_metadata["min_counts"]["value"] = np.min(data)
    processed_metadata["max_counts"]["value"] = np.max(data)

    return processed_metadata


def load_data_from_folder(folder: str, file_extension: str = ".tif") -> Dict[str, Any]:
    """
    Load raw data from a specified folder.

    Parameters
    ----------
    folder : str
        Path to the folder containing raw data files.
    file_extension : str, optional
        File extension of the raw data files (default is '.tif').

    Returns
    -------
    Dict[str, Any]
        Dictionary containing loaded raw data and metadata.
    """
    file_list = glob.glob(os.path.join(folder, f"*{file_extension}"))
    file_list.sort()

    # Clean up the list of files
    short_list_of_files = [os.path.basename(file) for file in file_list]
    short_list_of_files = cleanup_list_of_files(short_list_of_files)

    data = []
    metadata = []
    for file in short_list_of_files:
        full_file_name = os.path.join(folder, file)
        img_data, img_metadata = load_image(full_file_name)
        data.append(img_data)
        metadata.append(img_metadata)

    # Get image size from the first image
    if data:
        height, width = data[0].shape
        size = {"width": width, "height": height}
    else:
        size = {"width": 0, "height": 0}

    return {
        "data": np.array(data),
        "metadata": metadata,
        "file_list": short_list_of_files,
        "folder": folder,
        "size": size,
    }


def get_time_spectra_filename(folder: str, match_pattern: str = "*_Spectra.txt") -> str:
    """
    Find the time spectra file in the folder.

    Parameters
    ----------
    folder : str
        Folder to search for the time spectra file.
    match_pattern : str, optional
        Pattern to match the time spectra file, unix style (default is "*_Spectra.txt").

    Returns
    -------
    str
        Full path to the time spectra file, or an empty string if not found.
    """
    search_path = Path(folder) / match_pattern
    search_results = sorted(glob.glob(str(search_path)))

    if search_results and os.path.exists(search_results[0]):
        return search_results[0]
    else:
        return ""


def load_time_spectra(
    file_path: str,
    distance_source_detector_m: float,
    detector_offset_micros: float,
) -> Dict[str, Any]:
    """
    Load time spectra data from a specified file and calculate lambda scale.

    Parameters
    ----------
    file_path : str
        Path to the time spectra file.
    distance_source_detector_m : float
        Distance from the source to the detector in meters.
    detector_offset_micros : float
        Detector offset in microseconds

    Returns
    -------
    Dict[str, Any]
        Dictionary containing loaded time spectra data and calculated lambda array.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Time spectra file not found: {file_path}")

    tof_handler = TOF(filename=file_path)
    tof_array = tof_handler.tof_array
    counts_array = tof_handler.counts_array

    # Calculate lambda scale
    exp = Experiment(
        tof=tof_array,
        distance_source_detector_m=distance_source_detector_m,
        detector_offset_micros=detector_offset_micros,
    )
    lambda_array = exp.lambda_array

    return {
        "filename": file_path,
        "short_filename": os.path.basename(file_path),
        "tof_array": tof_array,
        "counts_array": counts_array,
        "lambda_array": lambda_array,
    }
