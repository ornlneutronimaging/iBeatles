"""Command line interface for iBeatles."""

#!/usr/bin/env python3
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from scipy.ndimage import gaussian_filter1d

from ibeatles.core.config import IBeatlesUserConfig
from ibeatles.core.io.data_loading import (
    load_data_from_folder,
    load_time_spectra,
    get_time_spectra_filename,
)
from ibeatles.core.processing.normalization import normalize_data
from ibeatles.core.fitting.binning import get_bin_coordinates, get_bin_transmission
from ibeatles.core.material import get_initial_bragg_edge_lambda
from ibeatles.core.fitting.kropff.fitting import fit_bragg_edge_single_pass

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
        config.raw_data.raw_data_dir,
        file_extension=config.raw_data.raw_data_extension,
    )
    # Open beam is optional
    if config.open_beam:
        open_beam = load_data_from_folder(
            config.open_beam.open_beam_data_dir,
            file_extension=config.open_beam.open_beam_data_extension,
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
        spectra_file = get_time_spectra_filename(config.raw_data.raw_data_dir)
        if spectra_file:
            spectra = load_time_spectra(
                spectra_file,
                config.analysis.distance_source_detector_in_m,
                config.analysis.detector_offset_in_us,
            )
        else:
            raise ValueError("Spectra file not found")
    return {"raw_data": raw_data, "open_beam": open_beam, "spectra": spectra}


def perform_binning(
    data: Dict[str, Any], config: IBeatlesUserConfig, spectra_dict: dict
) -> Dict[str, Any]:
    """
    Perform binning on the normalized data.

    Parameters
    ----------
    data : Dict[str, Any]
        Dictionary containing normalized data.
    config : IBeatlesUserConfig
        Parsed configuration object.
    spectra_dict:
        Dictionary containing time spectra data.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing binning results.
    """
    # Build binning coordinates
    bins = get_bin_coordinates(
        image_shape=data[0].shape,
        **config.analysis.pixel_binning.model_dump(),  # to dict for unpacking
    )
    # extract wavelength data from spectra dict
    # default unit is SI unit (meters)
    wavelengths_m = spectra_dict["lambda_array"]
    # execute binning
    bin_transmission = {}
    for i, bin_coord in enumerate(bins):
        wavelengths_bin, transmission_bin = get_bin_transmission(
            images=data,
            wavelengths=wavelengths_m,
            bin_coords=bin_coord,
            lambda_range=None,
        )
        bin_transmission[str(i)] = {
            "wavelengths": wavelengths_bin,
            "transmission": transmission_bin,
            "coordinates": bin_coord,
        }

    return bin_transmission


def perform_fitting(
    bin_transmission_dict: Dict[str, Any], config: IBeatlesUserConfig
) -> Dict[str, Any]:
    """
    Perform fitting on the normalized data.

    Parameters
    ----------
    bin_transmission_dict : Dict[str, Any]
        Dictionary containing binning results, from function perform_binning.
    config : IBeatlesUserConfig
        Parsed configuration object.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing fitting results.
    """
    # step_0: prepare the lambda range
    lambda_min_angstrom = config.analysis.fitting.lambda_min * 1e10
    lambda_max_angstrom = config.analysis.fitting.lambda_max * 1e10
    lambda_range_angstrom = lambda_min_angstrom, lambda_max_angstrom
    # step_1: get the reference (zero strain) Bragg edge value
    lambda_0_angstrom = get_initial_bragg_edge_lambda(
        material_config=config.analysis.material,
        lambda_range=lambda_range_angstrom,
    )
    # step_2: setup the initial guess and bounds
    # NOTE: the only critical value here is the reference Bragg edge wavelength
    initial_parameters = {
        "a0": 0.1,
        "b0": 0.1,
        "a_hkl": 0.1,
        "b_hkl": 0.1,
        "bragg_edge_wavelength": lambda_0_angstrom,  # use the reference Bragg edge as the initial guess
        "sigma": 0.01,
        "tau": 0.01,
    }
    parameter_bounds = {
        "bragg_edge_wavelength": {
            "min": lambda_min_angstrom,
            "max": lambda_max_angstrom,
        },
        "sigma": {"min": 0.001, "max": 0.2},
        "tau": {"min": 0.001, "max": 0.2},
    }
    # step_3: fitting
    fit_results = {}  # (str(bin_id): lmfit.model.ModelResult)
    for key, value in bin_transmission_dict.items():
        wavelengths_angstrom = value["wavelengths"] * 1e10
        transmission = value["transmission"]
        # step_3.1: prepare the fitting range
        mask = (wavelengths_angstrom > lambda_min_angstrom) & (
            wavelengths_angstrom < lambda_max_angstrom
        )
        wavelengths_fitting_angstrom = wavelengths_angstrom[mask]
        transmission_fitting = transmission[mask]
        # step_3.2: fitting a smooth version first to get better initial guess
        # NOTE: eventually we will always get a fit for over-smoothed data, so we need to gradually increase the sigma
        #       although the quality of the initial guess decreases with the increase of sigma
        ratio = 0.10
        fit_success = False
        while not fit_success:
            sigma = int(len(transmission_fitting) * ratio)
            transmission_smooth = gaussian_filter1d(transmission_fitting, sigma=sigma)
            fit_result_smoothed = fit_bragg_edge_single_pass(
                wavelengths=wavelengths_fitting_angstrom,
                transmission=transmission_smooth,
                initial_parameters=initial_parameters,
                parameter_bounds=parameter_bounds,
            )
            if fit_result_smoothed is None:
                logging.info(f"Failed fitting with sigma = {sigma}")
                ratio += 0.02
                continue
            else:
                fit_success = True
        # step_3.3: fitting
        fit_result = fit_bragg_edge_single_pass(
            wavelengths=wavelengths_fitting_angstrom,
            transmission=transmission_fitting,
            initial_parameters=fit_result_smoothed.best_values,
            parameter_bounds=parameter_bounds,
        )
        fit_results[key] = fit_result

    return fit_results


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
        raw_data_dict = rst_dict["raw_data"]
        open_beam_dict = rst_dict["open_beam"]
        spectra_dict = rst_dict["spectra"]

        # Perform normalization
        normalized_data, output_path = normalize_data(
            sample_data=raw_data_dict["data"],
            ob_data=open_beam_dict["data"] if open_beam_dict else None,
            time_spectra=spectra_dict,
            config=config,
            output_folder=config.output["normalized_data_dir"],
        )
        logging.info(f"Normalized data saved to {output_path}.")

        # Binning
        logging.info("Performing binning...")
        binning_results = perform_binning(
            data=normalized_data,
            config=config,
            spectra_dict=spectra_dict,
        )

        # Fitting
        logging.info("Performing fitting...")
        fitting_results = perform_fitting(
            bin_transmission_dict=binning_results,
            config=config,
        )

        # Dummy implementation of the remaining processing steps
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
