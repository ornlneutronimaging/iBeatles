import marimo

__generated_with = "0.9.33"
app = marimo.App(width="medium")


@app.cell
def __():
    import marimo as mo
    import json
    import copy
    from ibeatles.core.config import IBeatlesUserConfig

    return IBeatlesUserConfig, copy, json, mo


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
def __(base_ibeatles_config, copy, folders_selector_sample, mo):
    # After the users have selected the folders for different sample input, we will create a list of IBeatlesUserConfig objects for each sample
    batch_config_list = []
    num_samples = len(folders_selector_sample.value)

    mo.md(f"""Number of samples selected: **{num_samples}**""")

    for _i in range(num_samples):
        # duplicate the base configuration
        _sample_config = copy.deepcopy(base_ibeatles_config)
        # update the raw data path
        _sample_config.raw_data.raw_data_dir = folders_selector_sample.value[_i]
        # append
        batch_config_list.append(_sample_config)
    return batch_config_list, num_samples


@app.cell
def __(batch_config_list, mo, num_samples):
    # visualize as tabs of accordians
    _tabs = {}

    for _i in range(num_samples):
        _acc = mo.accordion(batch_config_list[_i].dict())
        _tabs[f"Sample {_i}"] = _acc

    # display the tabs
    mo.vstack(
        [
            mo.md(r"""Samples to be processed"""),
            mo.ui.tabs(_tabs),
        ]
    )
    return


@app.cell
def __(mo):
    mo.md(r"""## Verify Processing Parameters""")
    return


@app.cell
def __():
    return


@app.cell
def __(mo):
    mo.md(r"""## Running Batch Processing""")
    return


@app.cell
def __():
    return


@app.cell
def __(mo):
    mo.md(r"""## Summary of results""")
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
