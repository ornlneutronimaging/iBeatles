import marimo

__generated_with = "0.9.14"
app = marimo.App(width="full", app_title="BraggEdgeFit_iBeatles")


@app.cell
def __(mo):
    mo.md("""# Step by Step Bragg Edge Fitting with iBeatles""")
    return


@app.cell
def __():
    import marimo as mo
    import logging
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import matplotlib.colors as mcolors
    from scipy.ndimage import gaussian_filter1d
    from ibeatles.app.cli import load_data, load_config
    from ibeatles.core.processing.normalization import normalize_data
    from ibeatles.core.fitting.binning import (
        get_bin_coordinates,
        get_bin_transmission,
    )
    from ibeatles.core.material import get_initial_bragg_edge_lambda
    from ibeatles.core.fitting.kropff.fitting import fit_bragg_edge_single_pass
    return (
        cm,
        fit_bragg_edge_single_pass,
        gaussian_filter1d,
        get_bin_coordinates,
        get_bin_transmission,
        get_initial_bragg_edge_lambda,
        load_config,
        load_data,
        logging,
        mcolors,
        mo,
        normalize_data,
        np,
        plt,
    )


@app.cell
def __(logging):
    # Set up a custom handler and formatter
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    # Get the root logger and attach the handler
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers = [
        handler
    ]  # Replace existing handlers with the custom handler
    return formatter, handler, logger


@app.cell
def __(mo):
    mo.md(r"""## Data Loading""")
    return


@app.cell
def __(mo):
    mo.md(r"""Select a demo configuration file""")
    return


@app.cell
def __(mo):
    file_browser = mo.ui.file_browser(
        initial_path="../tests/data/json/", multiple=False
    )
    file_browser
    return (file_browser,)


@app.cell
def __(file_browser, load_config, load_data, logging):
    # load config
    logging.info("Loading config file")
    config_file = file_browser.path()
    config = load_config(config_file)
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
    return (
        config,
        config_file,
        data_dict,
        open_beam_dict,
        raw_data_dict,
        spectra_dict,
    )


@app.cell
def __(plt, spectra_dict):
    # plot the sepctrum
    lambda_array = spectra_dict["lambda_array"]
    counts_array = spectra_dict["counts_array"]

    fig_spectra, ax_spectra = plt.subplots(1, 1, figsize=(10, 5))
    ax_spectra.plot(lambda_array, counts_array)
    ax_spectra.set_xlabel("Wavelength (m)")
    ax_spectra.set_ylabel("Counts")
    return ax_spectra, counts_array, fig_spectra, lambda_array


@app.cell
def __(mo):
    mo.md(r"""## Data Normalization""")
    return


@app.cell
def __(
    config,
    normalize_data,
    open_beam_dict,
    raw_data_dict,
    spectra_dict,
):
    normalized_data, output_path = normalize_data(
        sample_data=raw_data_dict["data"],
        ob_data=open_beam_dict["data"],
        time_spectra=spectra_dict,
        config=config,
        output_folder=config.output["normalized_data_dir"],
    )
    return normalized_data, output_path


@app.cell
def __(mo):
    mo.md(r"""display original and clipped image""")
    return


@app.cell
def __(mo, normalized_data):
    image_id = mo.ui.slider(start=0, stop=len(normalized_data))
    image_id
    return (image_id,)


@app.cell
def __(image_id, normalized_data, np, plt):
    img = normalized_data[image_id.value].T
    img_clipped = np.array(img)
    img_clipped[img > 1.0] = np.nan

    fig_proj, ax_proj = plt.subplots(1, 2, figsize=(6, 3))
    ax_proj[0].imshow(img)
    ax_proj[0].set_title("original")
    ax_proj[1].imshow(img_clipped)
    ax_proj[1].set_title("clipped")
    return ax_proj, fig_proj, img, img_clipped


@app.cell
def __(img, np, plt):
    hist_proj, bin_edges_proj = np.histogram(
        img.flatten(), bins=1000, density=True
    )
    cdf_proj = np.cumsum(hist_proj)

    fig_cdf, ax_cdf = plt.subplots(1, 2, figsize=(6, 3))
    ax_cdf[0].plot(bin_edges_proj[:-1], hist_proj)
    ax_cdf[0].set_title("Histogram")
    ax_cdf[0].set_xlabel("Intensity")
    ax_cdf[0].set_ylabel("Frequency")

    ax_cdf[1].plot(bin_edges_proj[:-1], cdf_proj)
    ax_cdf[1].set_title("Cumulative Distribution")
    ax_cdf[1].set_xlabel("Intensity")
    ax_cdf[1].set_ylabel("Frequency")
    return ax_cdf, bin_edges_proj, cdf_proj, fig_cdf, hist_proj


@app.cell
def __(mo):
    mo.md(r"""## Kropff fitting""")
    return


@app.cell
def __(
    config,
    get_bin_coordinates,
    get_bin_transmission,
    logging,
    normalized_data,
    spectra_dict,
):
    logging.info(config.analysis.pixel_binning)

    # create bins based on config
    bins = get_bin_coordinates(
        image_shape=normalized_data[0].shape,
        **config.analysis.pixel_binning.model_dump(),  # to dict for unpacking
    )

    # prepare wavelengths
    wavelengths = spectra_dict["lambda_array"]
    lambda_range = (
        config.analysis.fitting.lambda_min,
        config.analysis.fitting.lambda_max,
    )

    # binning
    bin_transmission = {}

    for i, bin_coord in enumerate(bins):
        wavelengths_bin, transmission_bin = get_bin_transmission(
            images=normalized_data,
            wavelengths=wavelengths,
            bin_coords=bin_coord,
            lambda_range=None,
        )
        bin_transmission[str(i)] = {
            "wavelengths": wavelengths_bin,
            "transmission": transmission_bin,
            "coordinates": bin_coord,
        }
    return (
        bin_coord,
        bin_transmission,
        bins,
        i,
        lambda_range,
        transmission_bin,
        wavelengths,
        wavelengths_bin,
    )


@app.cell
def __(mo):
    mo.md(r"""Select bin range to visualize the spectra""")
    return


@app.cell
def __(bins, mo):
    bin_range_slider = mo.ui.range_slider(
        start=0, stop=len(bins), step=1, value=[0, 10], full_width=False
    )
    return (bin_range_slider,)


@app.cell
def __(bin_range_slider, mo):
    mo.hstack([bin_range_slider, mo.md(f"Has value: {bin_range_slider.value}")])
    return


@app.cell
def __(bin_range_slider, bin_transmission, cm, mcolors, plt):
    # Normalize the keys for colormap
    keys = list(bin_transmission.keys())
    norm = mcolors.Normalize(vmin=min(keys), vmax=max(keys))
    cmap = cm.viridis
    # plot
    fig_spectra_bin, ax_spectra_bin = plt.subplots(figsize=(8, 4))
    # Plot each curve with color from colormap
    bin_range_start = bin_range_slider.value[0]
    bin_range_end = bin_range_slider.value[1]
    for bin_id in range(bin_range_start, bin_range_end):
        color = cmap(norm(bin_id))
        value = bin_transmission[str(bin_id)]
        ax_spectra_bin.plot(
            value["wavelengths"],
            value["transmission"],
            color=color,
            linewidth=0.5,
            alpha=0.5,
        )

    # Add color bar with label
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Required for ScalarMappable
    cbar = fig_spectra_bin.colorbar(
        sm, ax=ax_spectra_bin
    )  # Associate color bar with the current axis
    cbar.set_label("Bin ID")  # Replace with the appropriate label for your keys

    # Label axes
    ax_spectra_bin.set_xlabel("Wavelength (m)")
    ax_spectra_bin.set_ylabel("Transmission")
    return (
        ax_spectra_bin,
        bin_id,
        bin_range_end,
        bin_range_start,
        cbar,
        cmap,
        color,
        fig_spectra_bin,
        keys,
        norm,
        sm,
        value,
    )


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
