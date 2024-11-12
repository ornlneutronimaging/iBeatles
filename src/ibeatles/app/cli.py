"""Command line interface for iBeatles."""

#!/usr/bin/env python3
import argparse
import json
import logging
import numpy as np
import matplotlib.pyplot as plt
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
from ibeatles.core.strain.mapping import calculate_strain_mapping
from ibeatles.core.strain.visualization import (
    plot_strain_map_overlay,
    plot_fitting_results_grid,
)
from ibeatles.core.strain.export import (
    generate_output_filename,
    save_strain_map,
    save_fitting_grid,
    save_analysis_results,
)


def setup_logging(
    log_file: Optional[Path] = None, log_level: int = logging.INFO
) -> logging.Logger:
    """
    Set up logging for the application.

    Parameters
    ----------
    log_file : Path, optional
        Path to the log file. If not provided, logs will be saved in the current working directory.
    log_level : int, optional
        Logging level. Defaults to logging.INFO.

    Returns
    -------
    logging.Logger
        Configured logger instance.
    """
    if log_file is None:
        log_file = Path.cwd() / "ibeatles_cli.log"

    logger = logging.getLogger("ibeatles_CLI")
    logger.setLevel(log_level)

    # Avoid adding handlers if they are already configured
    if not logger.hasHandlers():
        # Create file handler and stream handler
        file_handler = logging.FileHandler(log_file)
        stream_handler = logging.StreamHandler()

        # Set level for each handler
        file_handler.setLevel(log_level)
        stream_handler.setLevel(log_level)

        # Define formatter and add it to handlers
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

    return logger


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
    logger = logging.getLogger("ibeatles_CLI")
    logger.info(f"Loading configuration: {config_path}")

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
    logger = logging.getLogger("ibeatles_CLI")
    logger.info("Loading data...")

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
    logger = logging.getLogger("ibeatles_CLI")
    logger.info("Performing binning...")

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

    return bin_transmission, bins


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
    logger = logging.getLogger("ibeatles_CLI")
    logger.info("Performing fitting...")

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
                logger.info(
                    f"Bin_{key}: Failed fitting with sigma = {sigma}, increase sigma and try again..."
                )
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
    logger = setup_logging(log_file)

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
        logger.info(f"Normalized data saved to {output_path}.")

        # Binning
        binning_results, bins = perform_binning(
            data=normalized_data,
            config=config,
            spectra_dict=spectra_dict,
        )

        # Fitting
        logger.info("Performing fitting and strain mapping...")
        fitting_results = perform_fitting(
            bin_transmission_dict=binning_results,
            config=config,
        )
        # plot
        logger.info("Plotting fitting results grid...")
        lambda_min_angstrom = config.analysis.fitting.lambda_min * 1e10
        lambda_max_angstrom = config.analysis.fitting.lambda_max * 1e10
        lambda_range_angstrom = lambda_min_angstrom, lambda_max_angstrom
        lambda_0_angstrom = get_initial_bragg_edge_lambda(
            material_config=config.analysis.material,
            lambda_range=lambda_range_angstrom,
        )
        fig_fitting, _ = plot_fitting_results_grid(
            fit_results=fitting_results,
            bin_transmission=binning_results,
            reference_wavelength=lambda_0_angstrom,
        )
        # save figures
        logger.info("Saving fitting results...")
        output_path_strain = config.output.get("strain_results_dir", Path.cwd())
        # create the folder if not exist
        output_path_strain.mkdir(parents=True, exist_ok=True)
        # save fitting grid
        fn_fitting = generate_output_filename(
            input_folder=config.raw_data.raw_data_dir,
            analysis_type="fitting_grid",
            extension=config.analysis.strain_mapping.output_file_config.fitting_grid_format,
        )
        save_fitting_grid(
            figure=fig_fitting,
            output_path=output_path_strain / fn_fitting,
            config=config.analysis.strain_mapping.output_file_config,
        )
        # close the figure
        plt.close(fig_fitting)
        logger.info(f"Fitting results saved to {output_path_strain}.")

        # Calculate strain
        logger.info("Calculating strain mapping...")
        strain_results = calculate_strain_mapping(
            fit_results=fitting_results,
            d0=lambda_0_angstrom / 2.0,
            quality_threshold=config.analysis.strain_mapping.quality_threshold,
        )
        # plot
        logger.info("Plotting strain map overlay...")
        fig_strain, _ = plot_strain_map_overlay(
            strain_results=strain_results,
            bin_transmission=binning_results,
            integrated_image=np.sum(normalized_data, axis=0).T,
            colormap=config.analysis.strain_mapping.visualization.colormap,
            interpolation=config.analysis.strain_mapping.visualization.interpolation_method,
            alpha=config.analysis.strain_mapping.visualization.alpha,
        )
        # save figures
        logger.info("Saving strain map overlay...")
        fn_strain = generate_output_filename(
            input_folder=config.raw_data.raw_data_dir,
            analysis_type="strain_map",
            extension=config.analysis.strain_mapping.output_file_config.strain_map_format,
        )
        save_strain_map(
            figure=fig_strain,
            output_path=output_path_strain / fn_strain,
            config=config.analysis.strain_mapping.output_file_config,
        )
        # close the figure
        plt.close(fig_strain)
        logger.info(f"Strain map overlay saved to {output_path_strain}.")

        # Save analysis results
        logger.info("Saving analysis results...")
        output_path_analysis = config.output.get("analysis_results_dir", Path.cwd())
        output_path_analysis.mkdir(parents=True, exist_ok=True)
        # save analysis results
        fn_analysis = generate_output_filename(
            input_folder=config.raw_data.raw_data_dir,
            analysis_type="analysis_results",
            extension="csv",
        )
        # check if using custom material
        if config.analysis.material.custom_material:
            material_name = config.analysis.material.custom_material.name
        else:
            material_name = config.analysis.material.element
        # build the metadata header
        metadata = {
            "material_name": material_name,
            "d0": lambda_0_angstrom,
            "distance_source_detector": config.analysis.distance_source_detector_in_m,
            "detector_offset": config.analysis.detector_offset_in_us,
        }
        save_analysis_results(
            fit_results=fitting_results,
            bin_coordinates=bins,
            strain_results=strain_results,
            metadata=metadata,
            output_path=output_path_analysis / fn_analysis,
            config=config.analysis.strain_mapping.output_file_config,
        )
        logger.info(f"Analysis results saved to {output_path_strain}.")

        logger.info("iBeatles CLI application completed successfully.")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="iBeatles CLI Application")
    parser.add_argument("config", type=Path, help="Path to the configuration file")
    parser.add_argument("--log", type=Path, help="Path to the log file (optional)")
    args = parser.parse_args()

    main(args.config, args.log)
