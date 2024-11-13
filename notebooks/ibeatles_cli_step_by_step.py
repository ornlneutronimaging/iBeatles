import marimo

__generated_with = "0.9.15"
app = marimo.App(width="full", auto_download=["html"])


@app.cell
def __():
    import marimo as mo

    return (mo,)


@app.cell
def __(mo):
    mo.md(
        r"""
        # Introduction

        Traditional Jupyter notebook has the following issues:

        - Reproducibility issue related to `out-of-order` execution.
        - Hidden state that mutate silently due to unexpected side effects from functions.
        - Buggy 3rd party interactive widgets that often requires special care during production.

        Key features of Marimo that helps with these issues:

        * Directed Acyclic Graph (**DAG**) based **static analysis** force all affected cells automatically update, ensuring consistent state.
        * No hidden state allowed. Once a cell is modified, all cells referencing it will get a force update; if a cell is deleted, all cell requiring its output/state will error out.
        * UI solutions comes with the notebook libraries using internal hooks to popular widget libraries.
        * Var needs to be share between cells, i.e. **Global** variables, must be **UQNIUE**; local var must have leading `_`, and it can be reused between cells.

        In this example, we will be using iBeatles CLI tutorial notebook to show the potential of Marimo as a notebook system.
        """
    )
    return


@app.cell
def __(mo):
    mo.md(r"""# Step-by-step guide for iBeatles CLI tutorial notebook""")
    return


@app.cell
def __():
    import logging
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    from lmfit import fit_report
    from scipy.ndimage import gaussian_filter1d
    from ibeatles.app.cli import load_data, load_config
    from ibeatles.core.config import OutputFileConfig
    from ibeatles.core.processing.normalization import normalize_data
    from ibeatles.core.fitting.binning import (
        get_bin_coordinates,
        get_bin_transmission,
    )
    from ibeatles.core.material import get_initial_bragg_edge_lambda
    from ibeatles.core.fitting.kropff.fitting import fit_bragg_edge_single_pass
    from ibeatles.core.strain.mapping import calculate_strain_mapping
    from ibeatles.core.strain.visualization import (
        plot_strain_map_overlay,
        plot_fitting_results_grid,
    )
    from ibeatles.core.strain.export import save_analysis_results
    from ibeatles.app.cli import perform_fitting

    # setup loggers and handlers

    # Set up a custom handler and formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    # Get the root logger and attach the handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = [handler]  # Replace existing handlers with the custom handler
    return (
        OutputFileConfig,
        calculate_strain_mapping,
        cm,
        fit_bragg_edge_single_pass,
        fit_report,
        formatter,
        gaussian_filter1d,
        get_bin_coordinates,
        get_bin_transmission,
        get_initial_bragg_edge_lambda,
        handler,
        load_config,
        load_data,
        logger,
        logging,
        mcolors,
        normalize_data,
        np,
        perform_fitting,
        plot_fitting_results_grid,
        plot_strain_map_overlay,
        plt,
        save_analysis_results,
    )


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Data Loading

        Loading data from disk using a configuration JSON file.
        """
    )
    return


@app.cell
def __(mo):
    # Ask user to specify configuration file to load
    config_file = mo.ui.file_browser(
        initial_path="../tests/data/json",
        multiple=False,
    )

    config_file
    return (config_file,)


@app.cell
def __(config_file, load_config, load_data, logging):
    # load config
    logging.info(f"Loading config file: {config_file.path()}")
    config = load_config(config_file.path())
    logging.info(config)

    # load data
    logging.info("Loading data")
    data_dict = load_data(config)
    logging.info(data_dict.keys())
    # make local var for raw data, open beam and spectra data
    raw_data_dict = data_dict["raw_data"]
    open_beam_dict = data_dict["open_beam"]
    spectra_dict = data_dict["spectra"]
    logging.info(raw_data_dict.keys())
    logging.info(open_beam_dict.keys())
    logging.info(spectra_dict.keys())
    return config, data_dict, open_beam_dict, raw_data_dict, spectra_dict


@app.cell
def __(plt, spectra_dict):
    # plot the overall spectra from the data
    wavelength_in_meters = spectra_dict["lambda_array"]
    wavelength_in_angstrom = wavelength_in_meters * 1e10
    counts = spectra_dict["counts_array"]

    # plot the overall spectra
    fig_spectra, ax_spectra = plt.subplots()
    ax_spectra.plot(wavelength_in_meters, counts)
    ax_spectra.set_xlabel("Wavelength (m)")
    ax_spectra.set_ylabel("Counts")
    ax_spectra.set_title("Overall Spectra")
    # turn on grid
    ax_spectra.grid(True)
    # tight layout
    plt.tight_layout()

    fig_spectra
    return (
        ax_spectra,
        counts,
        fig_spectra,
        wavelength_in_angstrom,
        wavelength_in_meters,
    )


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Pre-processing data

        Using NeuNorm to normalize the data.
        """
    )
    return


@app.cell
def __(
    config,
    normalize_data,
    open_beam_dict,
    raw_data_dict,
    spectra_dict,
):
    data_normalized, output_path = normalize_data(
        sample_data=raw_data_dict["data"],
        ob_data=open_beam_dict["data"],
        time_spectra=spectra_dict,
        config=config,
        output_folder=config.output["normalized_data_dir"],
    )
    return data_normalized, output_path


@app.cell
def __(data_normalized, mo):
    proj_norm_index = mo.ui.slider(
        start=0,
        stop=len(data_normalized) - 1,
        value=0,
        step=1,
        label="Projection Index",
    )
    return (proj_norm_index,)


@app.cell
def __(cm, data_normalized, mo, np, plt, proj_norm_index):
    proj_norm_i = data_normalized[proj_norm_index.value].T
    proj_norm_i_clipped = np.array(proj_norm_i)
    proj_norm_i_clipped[proj_norm_i_clipped > 1.0] = (
        np.nan
    )  # remove anyting above 1.0, as transmission cannot be above 1.0

    fig_proj, ax_proj = plt.subplots(1, 4, figsize=(15, 5))
    ax_proj[0].imshow(proj_norm_i, cmap=cm.viridis)
    ax_proj[0].set_title("Normalized Data")
    # add colorbar
    cbar = plt.colorbar(
        mappable=ax_proj[0].imshow(proj_norm_i, cmap=cm.viridis),
        ax=ax_proj[0],
    )
    cbar.set_label("Transmission")
    ax_proj[1].imshow(proj_norm_i_clipped, cmap=cm.viridis)
    # add colorbar
    cbar = plt.colorbar(
        mappable=ax_proj[1].imshow(proj_norm_i_clipped, cmap=cm.viridis),
        ax=ax_proj[1],
    )
    cbar.set_label("Transmission")
    ax_proj[1].set_title("Clipped Data")

    # compute the histogram
    hist_proj_i, bin_edges_proj_i = np.histogram(proj_norm_i, bins=100, density=True)
    cdf_proj_i = np.cumsum(hist_proj_i)

    # plot
    ax_proj[2].plot(bin_edges_proj_i[:-1], hist_proj_i)
    ax_proj[2].set_title("Histogram")
    ax_proj[2].set_xlabel("Transmission")
    ax_proj[2].set_ylabel("Density")
    ax_proj[3].plot(bin_edges_proj_i[:-1], cdf_proj_i)
    ax_proj[3].set_title("Cumulative Distribution")
    ax_proj[3].set_xlabel("Transmission")
    ax_proj[3].set_ylabel("Cumulative Density")

    # tight layout
    plt.tight_layout()

    # widget display
    mo.vstack(
        [
            fig_proj,
            mo.vstack(
                [
                    proj_norm_index,
                    mo.md(f"Projection Index: {proj_norm_index.value}"),
                ]
            ),
        ]
    )
    return (
        ax_proj,
        bin_edges_proj_i,
        cbar,
        cdf_proj_i,
        fig_proj,
        hist_proj_i,
        proj_norm_i,
        proj_norm_i_clipped,
    )


@app.cell
def __(mo):
    mo.md(r"""## Kropff fitting to locate a Bragg Edge""")
    return


@app.cell
def __(
    config,
    data_normalized,
    get_bin_coordinates,
    get_bin_transmission,
    logger,
    logging,
    wavelength_in_meters,
):
    logging.info(config.analysis.pixel_binning)
    # generate binning coordinates
    logger.info("Generating binning coordinates")
    bin_coordinates = get_bin_coordinates(
        image_shape=data_normalized[0].shape,
        **config.analysis.pixel_binning.model_dump(),  # to dict for unpacking
    )
    # computed binned transmission
    logger.info("Binning transmission")
    lambda_min_in_meters = config.analysis.fitting.lambda_min
    lambda_max_in_meters = config.analysis.fitting.lambda_max
    lambda_range_in_meters = lambda_min_in_meters, lambda_max_in_meters
    # to angstrom (for later fitting use)
    lambda_min_in_angstrom = lambda_min_in_meters * 1e10
    lambda_max_in_angstrom = lambda_max_in_meters * 1e10
    lambda_range_in_angstrom = lambda_min_in_angstrom, lambda_max_in_angstrom

    bin_transmission = {}
    for _i, _bin_coords in enumerate(bin_coordinates):
        _wave_length_bin_meters, _transmission_bin = get_bin_transmission(
            images=data_normalized,  # need the whole stack
            wavelengths=wavelength_in_meters,
            bin_coords=_bin_coords,
            # lambda_range=lambda_range_in_meters,  # Change in one cell force an update on any other cells that depend on it
        )
        bin_transmission[str(_i)] = {
            "wavelengths": _wave_length_bin_meters,
            "transmission": _transmission_bin,
            "coordinates": _bin_coords,
        }
    return (
        bin_coordinates,
        bin_transmission,
        lambda_max_in_angstrom,
        lambda_max_in_meters,
        lambda_min_in_angstrom,
        lambda_min_in_meters,
        lambda_range_in_angstrom,
        lambda_range_in_meters,
    )


@app.cell
def __(bin_coordinates, mo):
    bin_range_slider = mo.ui.range_slider(
        start=0,
        stop=len(bin_coordinates),
        step=1,
        value=[10, 50],
        full_width=False,
    )
    return (bin_range_slider,)


@app.cell
def __(bin_range_slider, bin_transmission, cm, mcolors, mo, plt):
    # visualize the binning
    _keys = list(bin_transmission.keys())
    _norm = mcolors.Normalize(vmin=min(_keys), vmax=max(_keys))
    _cmap = cm.viridis
    # plot
    fig_bin_spectra, ax_bin_spectra = plt.subplots()
    # plot the selected bins
    _bins_to_plot = range(bin_range_slider.value[0], bin_range_slider.value[1])
    for _i in _bins_to_plot:
        _color = _cmap(_norm(_i))
        _value = bin_transmission[str(_i)]
        ax_bin_spectra.plot(
            _value["wavelengths"],
            _value["transmission"],
            color=_color,
            linewidth=0.5,
            alpha=0.5,
        )
    # add colorbar as label
    _sm = plt.cm.ScalarMappable(cmap=_cmap, norm=_norm)
    _sm.set_array([])
    _cbar = fig_bin_spectra.colorbar(_sm, ax=ax_bin_spectra)
    _cbar.set_label("Bin Index")
    # label the rest of the plot
    ax_bin_spectra.set_xlabel("Wavelength (m)")
    ax_bin_spectra.set_ylabel("Transmission")

    # control display
    mo.vstack(
        [
            fig_bin_spectra,
            mo.vstack(
                [bin_range_slider, mo.md(f"Bin Range: {bin_range_slider.value}")]
            ),
        ]
    )
    return ax_bin_spectra, fig_bin_spectra


@app.cell
def __(mo):
    mo.md(r"""individual fitting with each bin""")
    return


@app.cell
def __(bin_coordinates, mo):
    fitting_bit_id = mo.ui.slider(start=0, stop=len(bin_coordinates) - 1, value=0)
    return (fitting_bit_id,)


@app.cell
def __(
    bin_transmission,
    config,
    fit_bragg_edge_single_pass,
    fit_report,
    fitting_bit_id,
    gaussian_filter1d,
    get_initial_bragg_edge_lambda,
    lambda_max_in_angstrom,
    lambda_min_in_angstrom,
    lambda_range_in_angstrom,
    logger,
    mo,
    plt,
    wavelength_in_angstrom,
):
    import io
    from contextlib import redirect_stdout

    _bin_data = bin_transmission[str(fitting_bit_id.value)]
    _lambda = wavelength_in_angstrom  # we fit with angstrom
    _transmission = _bin_data["transmission"]

    # get the reference strain-free lambda
    lambda_0_angstrom = get_initial_bragg_edge_lambda(
        material_config=config.analysis.material,
        lambda_range=lambda_range_in_angstrom,  # this is because the NeutronBraggEdge Lib uses Angstrom
    )

    # executing fitting
    # step 0: zoom in
    _mask = (_lambda > lambda_min_in_angstrom) & (_lambda < lambda_max_in_angstrom)
    _lambda_fitting = _lambda[_mask]
    _transmission_fitting = _transmission[_mask]
    # step 1: setup fitting parameters and fitting constraints
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
            "min": lambda_min_in_angstrom,
            "max": lambda_max_in_angstrom,
        },
        "sigma": {
            "min": 0.001,
            "max": 0.1,
        },  # This is the same for all cases to prevent shape function collapse
        "tau": {
            "min": 0.001,
            "max": 0.1,
        },  # This is the same for all cases to prevent shape function collapse
    }
    # step 2: initial fitting of adaptively smoothed curve for better initial guess
    # NOTE: due to non-capped adaptive smoothing, we will always fit something, but it may not be the best fit
    _ratio = 0.10
    _fit_success = False
    while not _fit_success:
        _sigma = int(len(_lambda_fitting) * _ratio)
        _transmission_smoothed = gaussian_filter1d(_transmission_fitting, _sigma)
        _fit_results_smoothed = fit_bragg_edge_single_pass(
            wavelengths=_lambda_fitting,
            transmission=_transmission_smoothed,
            initial_parameters=initial_parameters,
            parameter_bounds=parameter_bounds,
        )
        if _fit_results_smoothed is None:
            logger.info(f"Failed fitting with sigma: {_sigma}")
            _ratio += 0.02
        else:
            logger.info(f"Success fitting with sigma: {_sigma}")
            _fit_success = True
    # step 3: actual fitting
    fit_results_manual = fit_bragg_edge_single_pass(
        wavelengths=_lambda_fitting,
        transmission=_transmission_fitting,
        initial_parameters=_fit_results_smoothed.best_values,
        parameter_bounds=parameter_bounds,
    )

    # visualization
    fig_fitting_single_bin, ax_fitting_single_bin = plt.subplots(1, 3, figsize=(15, 5))
    # left: full range with highlighted fitting range
    ax_fitting_single_bin[0].plot(_lambda, _transmission, label="Data")
    ax_fitting_single_bin[0].axvspan(
        lambda_min_in_angstrom, lambda_max_in_angstrom, color="green", alpha=0.5
    )
    ax_fitting_single_bin[0].axvline(
        x=lambda_0_angstrom,
        color="red",
        linestyle="--",
        label="Initial Bragg Edge",
    )
    ax_fitting_single_bin[0].set_title("Full Range")
    ax_fitting_single_bin[0].set_xlabel("Wavelength (Å)")
    ax_fitting_single_bin[0].set_ylabel("Transmission")
    # middle: zoom-in, fitting of the smoothed curve
    _fit_results_smoothed.plot_fit(ax=ax_fitting_single_bin[1], datafmt=".", fitfmt="-")
    ax_fitting_single_bin[1].scatter(
        _lambda_fitting, _transmission_fitting, label="Data", color="black", s=1
    )
    # right: zoom-in, actual fitting result
    if fit_results_manual is not None:
        # plot
        fit_results_manual.plot_fit(
            ax=ax_fitting_single_bin[2], datafmt=".", fitfmt="-"
        )
        ax_fitting_single_bin[2].set_title("Fitting Result")
        ax_fitting_single_bin[2].legend()
    else:
        ax_fitting_single_bin[2].set_title("Fitting Failed")

    ax_fitting_single_bin[2].set_xlabel("Wavelength (Å)")
    ax_fitting_single_bin[2].set_ylabel("Transmission")

    mo.vstack(
        [
            mo.accordion(
                {
                    "Initial Fitting Results": fit_report(_fit_results_smoothed.params),
                    "Fitting Results": fit_report(fit_results_manual.params)
                    if fit_results_manual
                    else "Fitting Failed",
                },
            ),
            fig_fitting_single_bin,
            mo.vstack(
                [
                    fitting_bit_id,
                    mo.md(f"Fitting Bin Index: {fitting_bit_id.value}"),
                ]
            ),
        ]
    )
    return (
        ax_fitting_single_bin,
        fig_fitting_single_bin,
        fit_results_manual,
        initial_parameters,
        io,
        lambda_0_angstrom,
        parameter_bounds,
        redirect_stdout,
    )


@app.cell
def __(mo):
    mo.md(r"""process all bins""")
    return


@app.cell
def __(bin_transmission, config, logger, perform_fitting):
    logger.info("Performing fitting")
    fitting_results = perform_fitting(
        bin_transmission_dict=bin_transmission,
        config=config,
    )
    return (fitting_results,)


@app.cell
def __(mo):
    mo.md(r"""strain mapping""")
    return


@app.cell
def __(
    calculate_strain_mapping,
    config,
    fitting_results,
    lambda_0_angstrom,
    logger,
):
    logger.info("Performing strain mapping")
    strain_results = calculate_strain_mapping(
        fit_results=fitting_results,
        d0=lambda_0_angstrom,
        quality_threshold=config.analysis.strain_mapping.quality_threshold,
    )
    return (strain_results,)


@app.cell
def __(
    bin_transmission,
    config,
    data_normalized,
    mo,
    np,
    plot_strain_map_overlay,
    strain_results,
):
    fig_strain_map, ax_strain_map = plot_strain_map_overlay(
        strain_results=strain_results,
        bin_transmission=bin_transmission,
        integrated_image=np.sum(data_normalized, axis=0).T,
        colormap=config.analysis.strain_mapping.visualization.colormap,
        interpolation=config.analysis.strain_mapping.visualization.interpolation_method,
        alpha=config.analysis.strain_mapping.visualization.alpha,
    )
    fig_strain_map.set_size_inches(5, 5)

    mo.mpl.interactive(fig_strain_map)
    return ax_strain_map, fig_strain_map


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
