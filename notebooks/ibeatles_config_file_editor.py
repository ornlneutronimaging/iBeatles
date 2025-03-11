import marimo

__generated_with = "0.11.17"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    mo.Html("<font color=blue size=10>iBeatles config file editor</font>")

    DEBUG = True
    if DEBUG:
        initial_path = "~/SNS/SNAP/IPTS-27829/"
    else:
        initial_path = "/SNS/VENUS/"
    return DEBUG, initial_path, mo


@app.cell
def _(initial_path, mo):
    config_file = mo.ui.file_browser(
        initial_path=initial_path, filetypes=[".json"], multiple=False
    )
    config_file
    return (config_file,)


@app.cell
def _(config_file, mo):
    if config_file.value:
        _text = "Config file content"
    else:
        _text = ""
    mo.md(_text)

    return


@app.cell
def _(config_file):
    import json
    import os

    data = None
    if len(config_file.value) > 0:
        if os.path.exists(config_file.value[0].path):
            with open(config_file.value[0].path) as json_file:
                data = json.load(json_file)

    data
    return data, json, json_file, os


@app.cell
def _(data, mo):
    mo.vstack(
        [
            mo.md("##raw data dir"),
            mo.hstack(
                [
                    mo.ui.text(
                        value=data["raw_data"]["raw_data_dir"],
                        full_width=True,
                    ),
                    mo.ui.button(label="...", full_width=False),
                ],
                widths=[10, 1],
            ),
        ]
    )

    return


@app.cell
def _(data, mo):
    mo.vstack(
        [
            mo.md("##open beam dir"),
            mo.hstack(
                [
                    mo.ui.text(
                        value=data["open_beam"]["open_beam_data_dir"],
                        full_width=True,
                    ),
                    mo.ui.button(label="...", full_width=False),
                ],
                widths=[10, 1],
            ),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""##normalization""")
    return


@app.cell
def _(data, mo):
    _stack = []
    mo.md("###sample background")
    for _index, _roi in enumerate(data["normalization"]["sample_background"]):
        _x0 = _roi["x0"]
        _y0 = _roi["y0"]
        _width = _roi["width"]
        _height = _roi["height"]
        _stack.append(
            mo.vstack(
                [
                    mo.md(f"ROI #{_index}"),
                    mo.vstack(
                        [
                            mo.ui.text(value=str(_x0), full_width=False, label="x0"),
                            mo.ui.text(
                                value=str(_y0),
                                full_width=False,
                                label="y0",
                            ),
                            mo.ui.text(
                                value=str(_width),
                                full_width=False,
                                label="width",
                            ),
                            mo.ui.text(
                                value=str(_height),
                                full_width=False,
                                label="height",
                            ),
                        ]
                    ),
                ]
            )
        )
    _stack
    return


@app.cell
def _(mo):
    mo.md("""##Material""")
    return


@app.cell
def _(data, mo):
    _element = data["analysis"]["material"]["element"]
    mo.ui.text(_element, disabled=True)
    return


@app.cell
def _(mo):
    mo.md("""##Pixel binning""")
    return


@app.cell
def _(data, mo):
    _bins = data["analysis"]["pixel_binning"]
    _x0 = str(_bins["x0"])
    _y0 = str(_bins["y0"])
    _width = str(_bins["width"])
    _height = str(_bins["height"])
    _size = str(_bins["bins_size"])
    mo.vstack(
        [
            mo.ui.text(value=_x0, label="x0"),
            mo.ui.text(value=_y0, label="y0"),
            mo.ui.text(value=_width, label="width"),
            mo.ui.text(value=_height, label="height"),
            mo.ui.text(value=_size, label="Bin size"),
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""##Fitting parameters""")
    return


@app.cell
def _(data, mo):
    _fitting = data["analysis"]["fitting"]
    _lambda_min = f"{_fitting['lambda_min']:.5e}"
    _lambda_max = f"{_fitting['lambda_max']:.5e}"
    mo.vstack(
        [
            mo.ui.text(value=_lambda_min, label="Lambda min"),
            mo.ui.text(value=_lambda_max, label="Lambda max"),
        ]
    )

    return


@app.cell
def _(mo):
    mo.md("""##Strain mapping settings""")
    return


@app.cell
def _(data, mo):
    _strain = data["analysis"]["strain_mapping"]
    _d0 = str(_strain["d0"])
    mo.ui.text(value=_d0, label="d0")
    return


@app.cell
def _(mo):
    mo.md("""##Instrument settings""")
    return


@app.cell
def _(data, mo):
    mo.vstack(
        [
            mo.ui.text(
                label="distance source_detector (m)",
                value=data["analysis"]["distance_source_detector_in_m"],
            ),
            mo.ui.text(
                label="detector offset (us)",
                value=data["analysis"]["detector_offset_in_us"],
            ),
        ]
    )
    return


app._unparsable_cell(
    r"""
    \"distance_source_detector_in_m\":\"19.855\"
    \"detector_offset_in_us\":\"5000\"
    """,
    name="_",
)


@app.cell
def _(mo):
    mo.md("""##Output""")
    return


@app.cell
def _(data, mo):
    mo.vstack(
        [
            mo.ui.text(
                label="normalized data dir",
                value=data["output"]["normalized_data_dir"],
                full_width=True,
            ),
            mo.ui.text(
                label="analysis results dir",
                full_width=True,
                value=data["output"]["analysis_results_dir"],
            ),
            mo.ui.text(
                label="strain_results_dir",
                value=data["output"]["strain_results_dir"],
                full_width=True,
            ),
        ]
    )
    return


app._unparsable_cell(
    r"""
    \"normalized_data_dir\":\"/Users/j35/SNS/SNAP/IPTS-27829/normalized_03m_10d_2025y_15h_45mn\"
    \"analysis_results_dir\":\"/Users/j35/SNS/SNAP/IPTS-27829/analysis_03m_10d_2025y_15h_45mn\"
    \"strain_results_dir\":\"/Users/j35/SNS/SNAP/IPTS-27829/strain_03m_10d_2025y_15h_45mn\"
    """,
    name="_",
)


if __name__ == "__main__":
    app.run()
