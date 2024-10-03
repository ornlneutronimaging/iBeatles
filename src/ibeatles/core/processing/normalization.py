#!/usr/bin/env python
"""Normalization functions for the TOF imaging data."""

import numpy as np
from typing import Optional, Dict, Any, Tuple, List
from pathlib import Path
import shutil
import logging

from NeuNorm.normalization import Normalization as NeuNormNormalization
from NeuNorm.roi import ROI

from ibeatles.core.config import IBeatlesUserConfig
from ibeatles.core.processing.moving_average import moving_average


def normalize_data(
    sample_data: np.ndarray,
    ob_data: Optional[np.ndarray],
    time_spectra: Dict[str, Any],
    config: IBeatlesUserConfig,
    output_folder: str,
) -> Tuple[np.ndarray, str]:
    """
    Normalize the input data based on the provided configuration.

    Parameters:
    -----------
    sample_data : np.ndarray
        The raw sample data to be normalized.
    ob_data : Optional[np.ndarray]
        The open beam data, if available.
    time_spectra : Dict[str, Any]
        Time spectra information as returned by load_time_spectra function.
    config : IBeatlesUserConfig
        Configuration object containing normalization settings.
    output_folder : str
        Base output folder for normalized data.

    Returns:
    --------
    Tuple[np.ndarray, str]
        A tuple containing the normalized data and the full path to the output folder.
    """
    logging.info("Starting normalization process")

    # Create NeuNorm object
    o_norm = NeuNormNormalization()
    o_norm.load(data=sample_data)
    if ob_data is not None:
        o_norm.load(data=ob_data, data_type="ob")

    # Apply moving average if configured
    if config.normalization.moving_average.active:
        logging.info("Applying moving average")
        if config.normalization.processing_order == "Moving average, Normalization":
            o_norm.data["sample"]["data"] = moving_average(
                np.array(
                    o_norm.data["sample"]["data"]
                ),  # NeuNorm is return a list of arrays
                config.normalization.moving_average,
            )
            if ob_data is not None:
                o_norm.data["ob"]["data"] = moving_average(
                    np.array(o_norm.data["ob"]["data"]),
                    config.normalization.moving_average,
                )

    # Perform normalization
    logging.info("Performing normalization")
    background_roi = _get_background_roi(config)

    if ob_data is None:
        o_norm.normalization(roi=background_roi, use_only_sample=True)
    else:
        o_norm.normalization(roi=background_roi if background_roi else None)

    # Apply moving average after normalization if configured
    if (
        config.normalization.moving_average.active
        and config.normalization.processing_order == "Normalization, Moving Average"
    ):
        logging.info("Applying moving average after normalization")
        normalized_data = moving_average(
            np.array(o_norm.get_normalized_data()),
            config.normalization.moving_average,
        )
        # manual replace the normalized data
        o_norm.data["normalized"] = normalized_data

    # Export normalized data
    full_output_folder = _create_output_folder(output_folder, config)
    o_norm.export(folder=full_output_folder)

    # Move time spectra file
    _copy_time_spectra(time_spectra, full_output_folder)

    return o_norm.get_normalized_data(), full_output_folder


def _get_background_roi(config: IBeatlesUserConfig) -> Optional[List[ROI]]:
    """Extract background ROI from configuration."""
    if config.normalization.sample_background:
        bg = config.normalization.sample_background
        return [ROI(x0=bg.x0, y0=bg.y0, width=bg.width, height=bg.height)]
    return None


def _create_output_folder(base_folder: str, config: IBeatlesUserConfig) -> str:
    """Create and return the full path to the output folder."""
    sample_name = Path(config.raw_data.raw_data_dir).name
    full_output_folder = Path(base_folder) / f"{sample_name}_normalized"
    full_output_folder.mkdir(parents=True, exist_ok=True)
    return str(full_output_folder)


def _copy_time_spectra(time_spectra: Dict[str, Any], output_folder: str) -> None:
    """Copy time spectra file to the output folder."""
    source_file = time_spectra["filename"]
    dest_file = Path(output_folder) / time_spectra["short_filename"]
    shutil.copy(str(source_file), str(dest_file))
    logging.info(f"Copied time spectra file to {dest_file}")
