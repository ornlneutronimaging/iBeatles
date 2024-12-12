import marimo

__generated_with = "0.9.34"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import json
    import copy
    import time
    from pathlib import Path
    from ibeatles.core.config import IBeatlesUserConfig
    from ibeatles.app.cli import main as ibeatles_main

    return IBeatlesUserConfig, Path, copy, ibeatles_main, json, mo, time


@app.cell
def __(mo):
    mo.md(r"""# Batch Bragg Edge Fitting with iBeatles""")
    return


@app.cell
def __(mo):
    mo.md(r"""## Load Configuration from Manual Session""")
    return


@app.cell
def __(mo):
    base_configuration_file = mo.ui.file(
        filetypes=[".JSON", ".json"],
        label="Select Configuration File",
        multiple=False,
        kind="area",
    )

    base_configuration_file
    return (base_configuration_file,)


@app.cell
def __(base_configuration_file, json, mo):
    ## display JSON content
    base_json_viewer = None
    if base_configuration_file.contents() is not None:
        base_json_viewer = mo.accordion(json.loads(base_configuration_file.contents()))
    return (base_json_viewer,)


@app.cell
def __(base_json_viewer, mo):
    mo.vstack(
        [
            mo.md(r"""Base Configuration JSON"""),
            base_json_viewer,
        ]
    )
    return


@app.cell
def __(IBeatlesUserConfig, base_configuration_file, json):
    # process the configuration file into a IBeatlesUserConfig object
    if base_configuration_file.contents() is not None:
        base_ibeatles_config = IBeatlesUserConfig(
            **json.loads(base_configuration_file.contents())
        )
    return (base_ibeatles_config,)


@app.cell
def __(mo):
    mo.md(r"""## Select Folder**s** for Batch Processing""")
    return


@app.cell
def __(mo):
    # select multiple folders for batch processing
    folders_selector_sample = mo.ui.file_browser(
        initial_path="~/tmp",
        multiple=True,
        selection_mode="directory",
        label="Select SAMPLE folders for batch processing",
        restrict_navigation=True,
    )
    return (folders_selector_sample,)


@app.cell
def __(folders_selector_sample):
    folders_selector_sample
    return


@app.cell
def __(Path, base_ibeatles_config, copy, folders_selector_sample, mo):
    # After the users have selected the folders for different sample input, we will create a list of IBeatlesUserConfig objects for each sample
    batch_config_list = []
    num_samples = len(folders_selector_sample.value)

    mo.md(f"""Number of samples selected: **{num_samples}**""")

    for _i in range(num_samples):
        # duplicate the base configuration
        _sample_config = copy.deepcopy(base_ibeatles_config)
        # update the raw data path
        _sample_config.raw_data.raw_data_dir = folders_selector_sample.value[_i].path
        # Update output file paths
        _sample_config.output["normalized_data_dir"] = Path(
            str(_sample_config.output["normalized_data_dir"]) + f"_{_i}"
        )
        _sample_config.output["analysis_results_dir"] = Path(
            str(_sample_config.output["analysis_results_dir"]) + f"_{_i}"
        )
        _sample_config.output["strain_results_dir"] = Path(
            str(_sample_config.output["strain_results_dir"]) + f"_{_i}"
        )

        # append
        batch_config_list.append(_sample_config)
    return batch_config_list, num_samples


@app.cell
def __(mo):
    mo.md(
        r"""
        ## Verify Processing Parameters

        Inspect the parameters to ensure all are correct
        """
    )
    return


@app.cell
def __(batch_config_list, mo, num_samples):
    # visualize as tabs of accordians
    _tabs = {}

    for _i in range(num_samples):
        _acc = mo.accordion(batch_config_list[_i].dict())
        _tabs[f"Sample {_i}"] = _acc

    # display the tabs
    config_items_viewer = mo.md(r"""No samples to process""")
    if num_samples > 0:
        config_items_viewer = mo.vstack(
            [
                mo.md(r"""Samples to be processed"""),
                mo.ui.tabs(_tabs),
            ]
        )

    config_items_viewer
    return (config_items_viewer,)


@app.cell
def __(mo):
    mo.md(r"""## Running Batch Processing""")
    return


@app.cell
def __(mo):
    exec_button = mo.ui.run_button(
        kind="success",
        disabled=False,
        tooltip="Run batch processing",
        label="Run Batch Processing",
    )
    return (exec_button,)


@app.cell
def __(exec_button):
    exec_button
    return


@app.cell
def __(batch_config_list, exec_button, ibeatles_main, mo, num_samples):
    if exec_button.value:
        # disable the button first
        exec_button.disabled = True
        for _i in mo.status.progress_bar(
            range(num_samples),
            title="Processing",
            subtitle="Please wait...",
            show_eta=True,
            show_rate=True,
        ):
            _config = batch_config_list[_i]
            with mo.redirect_stdout(), mo.redirect_stderr():
                print(f"Processing sample {_i}")
                ibeatles_main(_config)
        # re-enable the button
        exec_button.disabled = False
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
