"""Command line interface for iBeatles."""

#!/usr/bin/env python3
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ibeatles.core.config import IBeatlesUserConfig
from ibeatles.core.io.data_loading import (
    load_data_from_folder,
    load_time_spectra,
    get_time_spectra_filename,
)

# Placeholder imports (to be implemented later)
# from ibeatles.core.normalization import normalize_data
# from ibeatles.core.fitting import perform_fitting
# from ibeatles.core.strain_calculation import calculate_strain


def setup_logging(log_file: Optional[Path] = None) -> None:
    """
    Set up logging for the application.

    Parameters
    ----------
    log_file : Path, optional
        Path to the log file. If not provided, logs will be saved in the current working directory.

    Returns
    -------
    None
    """
    if log_file is None:
        log_file = Path.cwd() / "ibeatles_cli.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
    )


def load_config(config_path: Path) -> IBeatlesUserConfig:
    """
    Load and parse the configuration file.

    Parameters
    ----------
    config_path : Path
        Path to the JSON configuration file.

    Returns
    -------
    IBeatlesUserConfig
        Parsed configuration object.
    """
    with open(config_path, "r") as f:
        config_data = json.load(f)
    return IBeatlesUserConfig(**config_data)


def load_data(config: IBeatlesUserConfig) -> Dict[str, Any]:
    """
    Load raw data, open beam, and spectra files.

    Parameters
    ----------
    config : IBeatlesUserConfig
        Parsed configuration object.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing loaded data.
    """
    logging.info("Loading data...")
    # Raw data is mandatory
    raw_data = load_data_from_folder(
        config.raw_data["raw_data_dir"],
        file_extension=config.raw_data["raw_data_extension"],
    )
    # Open beam is optional
    if config.open_beam:
        open_beam = load_data_from_folder(
            config.open_beam["open_beam_data_dir"],
            file_extension=config.open_beam["open_beam_data_extension"],
        )
    else:
        open_beam = None
    # Spectra file is needed, but specify the path in the configuration file is optional
    if config.spectra_file_path:
        spectra = load_time_spectra(
            config.spectra_file_path,
            config.analysis.distance_source_detector_in_m,
            config.analysis.detector_offset_in_us,
        )
    else:
        # try to load spectra file from the raw data directory
        spectra_file = get_time_spectra_filename(config.raw_data["raw_data_dir"])
        if spectra_file:
            spectra = load_time_spectra(
                spectra_file,
                config.analysis.distance_source_detector_in_m,
                config.analysis.detector_offset_in_us,
            )
        else:
            raise ValueError("Spectra file not found")
    return {"raw_data": raw_data, "open_beam": open_beam, "spectra": spectra}


def normalize_data(data: Dict[str, Any], config: IBeatlesUserConfig) -> Dict[str, Any]:
    """
    Perform data normalization.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing loaded data.
    config : IBeatlesUserConfig
        Parsed configuration object.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing normalized data.
    """
    # Placeholder implementation
    logging.info("Normalizing data...")
    # normalized_data = normalize_data(data['raw_data'], data['open_beam'], config)
    return {"normalized_data": None}


def perform_fitting(data: Dict[str, Any], config: IBeatlesUserConfig) -> Dict[str, Any]:
    """
    Perform fitting on the normalized data.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing normalized data.
    config : IBeatlesUserConfig
        Parsed configuration object.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing fitting results.
    """
    # Placeholder implementation
    logging.info("Performing fitting...")
    # fitting_results = perform_fitting(data['normalized_data'], config)
    return {"fitting_results": None}


def calculate_strain(
    data: Dict[str, Any], config: IBeatlesUserConfig
) -> Dict[str, Any]:
    """
    Calculate strain based on fitted d-spacing.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing fitting results.
    config : IBeatlesUserConfig
        Parsed configuration object.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing strain calculation results.
    """
    # Placeholder implementation
    logging.info("Calculating strain...")
    # strain_results = calculate_strain(data['fitting_results'], config)
    return {"strain_results": None}


def save_normalization_results(
    data: Dict[str, Any], config: IBeatlesUserConfig
) -> None:
    """
    Save normalization results to disk.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing normalized data.
    config : IBeatlesUserConfig
        Parsed configuration object.

    Returns
    -------
    None
    """
    # Placeholder implementation
    output_dir = config.output["normalized_data_dir"]
    logging.info(f"Saving normalization results to {output_dir}...")
    # Save normalized data
    # Example: np.save(output_dir / "normalized_data.npy", data["normalized_data"])


def save_analysis_results(data: Dict[str, Any], config: IBeatlesUserConfig) -> None:
    """
    Save analysis results (strain map data and images) to disk.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing fitting results and strain calculation results.
    config : IBeatlesUserConfig
        Parsed configuration object.

    Returns
    -------
    None
    """
    # Placeholder implementation
    output_dir = config.output["analysis_results_dir"]
    logging.info(f"Saving analysis results to {output_dir}...")
    # Save fitting results
    # Example: np.save(output_dir / "fitting_results.npy", data["fitting_results"])
    # Save strain map data
    # Example: np.save(output_dir / "strain_map.npy", data["strain_results"])
    # Save strain map image
    # Example: plt.imsave(output_dir / "strain_map.png", data["strain_results"])


def main(config_path: Path, log_file: Optional[Path] = None) -> None:
    """
    Main function to run the iBeatles CLI application.

    Parameters
    ----------
    config_path : Path
        Path to the configuration file.
    log_file : Path, optional
        Path to the log file.

    Returns
    -------
    None
    """
    setup_logging(log_file)

    try:
        # Load configuration
        config = load_config(config_path)

        # Load data
        rst_dict = load_data(config)
        raw_data = rst_dict["raw_data"]
        open_beam = rst_dict["open_beam"]
        # spectra = rst_dict['spectra']

        # Proceed with normalization, fitting, etc.
        normalized_data = normalize_data(
            {"raw_data": raw_data, "open_beam": open_beam}, config
        )
        save_normalization_results(normalized_data, config)

        fitting_results = perform_fitting(normalized_data, config)
        strain_results = calculate_strain(fitting_results, config)

        analysis_results = {**fitting_results, **strain_results}
        save_analysis_results(analysis_results, config)

        logging.info("iBeatles CLI application completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iBeatles CLI Application")
    parser.add_argument("config", type=Path, help="Path to the configuration file")
    parser.add_argument("--log", type=Path, help="Path to the log file (optional)")
    args = parser.parse_args()

    main(args.config, args.log)
