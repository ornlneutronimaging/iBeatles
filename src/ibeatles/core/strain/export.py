#!/usr/bin/env python
"""Export functions for strain mapping analysis results."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Any
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from lmfit.model import ModelResult

from ibeatles.core.config import (
    OutputFileConfig,
    BinCoordinates,
)


logger = logging.getLogger(__name__)


def generate_output_filename(
    input_folder: str | Path,
    analysis_type: str,
    extension: str,
    timestamp: Optional[datetime] = None,
) -> Path:
    """Generate standardized output filename with timestamp.

    Parameters
    ----------
    input_folder : str | Path
        Original input data folder name to use as base
    analysis_type : str
        Type of analysis result (e.g., 'strain_map', 'fitting_grid')
    extension : str
        File extension without dot (e.g., 'png', 'pdf', 'csv')
    timestamp : Optional[datetime]
        Timestamp to use, defaults to current time if None

    Returns
    -------
    Path
        Complete output filepath

    Example
    -------
    >>> generate_output_filename('fe_sample', 'strain_map', 'png')
    Path('fe_sample_strain_map_20240108_153042.png')
    """
    input_folder = Path(input_folder)
    base_name = input_folder.stem

    if timestamp is None:
        timestamp = datetime.now()

    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
    filename = f"{base_name}_{analysis_type}_{timestamp_str}.{extension}"

    return Path(filename)


def save_strain_map(
    figure: Figure,
    output_path: Path,
    config: OutputFileConfig,
) -> None:
    """Save strain map overlay plot.

    Parameters
    ----------
    figure : Figure
        Matplotlib figure containing the strain map
    output_path : Path
        Path to save the figure
    config : OutputFileConfig
        Output configuration including format and DPI settings

    Raises
    ------
    ValueError
        If output path already exists
    IOError
        If saving fails
    """
    output_path = Path(output_path)
    if output_path.exists():
        raise ValueError(f"Output path {output_path} already exists")

    try:
        figure.savefig(
            output_path,
            format=config.strain_map_format,
            dpi=config.figure_dpi,
            bbox_inches="tight",
        )
        logger.info(f"Saved strain map to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save strain map: {str(e)}")
        raise IOError(f"Failed to save strain map: {str(e)}")


def save_fitting_grid(
    figure: Figure,
    output_path: Path,
    config: OutputFileConfig,
) -> None:
    """Save fitting results grid plot.

    Parameters
    ----------
    figure : Figure
        Matplotlib figure containing the fitting grid
    output_path : Path
        Path to save the figure
    config : OutputFileConfig
        Output configuration including format and DPI settings

    Raises
    ------
    ValueError
        If output path already exists
    IOError
        If saving fails
    """
    output_path = Path(output_path)
    if output_path.exists():
        raise ValueError(f"Output path {output_path} already exists")

    try:
        figure.savefig(
            output_path,
            format=config.fitting_grid_format,
            dpi=config.figure_dpi,
            bbox_inches="tight",
        )
        logger.info(f"Saved fitting grid to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save fitting grid: {str(e)}")
        raise IOError(f"Failed to save fitting grid: {str(e)}")


def save_analysis_results(
    fit_results: Dict[str, Optional[ModelResult]],
    bin_coordinates: Dict[str, BinCoordinates],
    strain_results: Dict[str, Dict[str, float]],
    metadata: Dict[str, Any],
    output_path: Path,
    config: OutputFileConfig,
) -> pd.DataFrame:
    """Save fitting and strain results as CSV with metadata header.

    Parameters
    ----------
    fit_results : Dict[str, Optional[ModelResult]]
        Dictionary of fitting results for each bin
    bin_coordinates : Dict[str, BinCoordinates]
        Dictionary of bin coordinates
    strain_results : Dict[str, Dict[str, float]]
        Dictionary of strain calculation results
    metadata : Dict[str, Any]
        Analysis metadata to include in header
    output_path : Path
        Path to save the CSV file
    config : OutputFileConfig
        Output configuration including CSV format settings

    Returns
    -------
    pd.DataFrame
        DataFrame containing the analysis results

    Raises
    ------
    ValueError
        If output path already exists
    IOError
        If saving fails
    """
    output_path = Path(output_path)
    if output_path.exists():
        raise ValueError(f"Output path {output_path} already exists")

    # Prepare metadata header
    header_lines = []
    if config.csv_format.include_metadata_header:
        comment_char = config.csv_format.metadata_comment_char
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header_lines.extend(
            [
                f"{comment_char} Analysis Timestamp: {timestamp}",
                f"{comment_char} Material: {metadata.get('material_name', 'Unknown')}",
                f"{comment_char} d0: {metadata.get('d0', 'Unknown')} Å",
                f"{comment_char} Distance Source-Detector: {metadata.get('distance_source_detector', 'Unknown')} m",
                f"{comment_char} Detector Offset: {metadata.get('detector_offset', 'Unknown')} µs",
                f"{comment_char}",
            ]
        )

    # Create DataFrame
    data = []
    for bin_id in fit_results.keys():
        result = fit_results[bin_id]
        coords = bin_coordinates[int(bin_id)]
        strain_data = strain_results.get(bin_id, {})

        if result is not None:
            # extract fitting results
            # NOTE: sometimes the uncertainty estimate fails due to a, b, sigma, tau at the
            #       boundaries of the parameter space. In this case, the stderr is NaN.
            lambda_hkl = result.best_values.get("bragg_edge_wavelength", np.nan)
            lambda_hkl_err = result.params["bragg_edge_wavelength"].stderr
            d_spacing = lambda_hkl / 2.0
            d_spacing_err = lambda_hkl_err / 2.0 if lambda_hkl_err else np.nan
            row = {
                "bin_id": bin_id,
                "x0": coords.x0,
                "y0": coords.y0,
                "x1": coords.x1,
                "y1": coords.y1,
                "row_index": coords.row_index,
                "column_index": coords.column_index,
                "lambda_hkl": lambda_hkl,
                "lambda_hkl_err": lambda_hkl_err,
                "d_spacing": d_spacing,
                "d_spacing_err": d_spacing_err,
                "strain": strain_data.get("strain", np.nan),
                "strain_err": strain_data.get("error", np.nan),
                "r_squared": result.rsquared,
                "chi_squared": result.chisqr,
            }
            data.append(row)

    df = pd.DataFrame(data)

    try:
        # Write header lines first if enabled
        if config.csv_format.include_metadata_header and header_lines:
            with open(output_path, "w") as f:
                f.write("\n".join(header_lines) + "\n")

            # Append data
            df.to_csv(
                output_path,
                mode="a",
                index=False,
                sep=config.csv_format.delimiter,
                na_rep=config.csv_format.na_rep,
            )
        else:
            # Write data directly
            df.to_csv(
                output_path,
                index=False,
                sep=config.csv_format.delimiter,
            )

        logger.info(f"Saved analysis results to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save analysis results: {str(e)}")
        raise IOError(f"Failed to save analysis results: {str(e)}")

    return df
