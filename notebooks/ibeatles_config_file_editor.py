import marimo

__generated_with = "0.10.9"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import datetime
    import json
    import os

    TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"

    mo.Html("<font color=blue size=10>iBeatles config file editor</font>")

    DEBUG = True
    if DEBUG:
        initial_path = "~/SNS/SNAP/IPTS-27829/"
    else:
        initial_path = "/SNS/VENUS/"
    return DEBUG, TIMESTAMP_FORMAT, datetime, initial_path, json, mo, os


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
def _(config_file, json, os):
    data = None
    if len(config_file.value) > 0:
        if os.path.exists(config_file.value[0].path):
            with open(config_file.value[0].path) as json_file:
                data = json.load(json_file)

    data
    return data, json_file


@app.cell
def _(data, mo):
    mo.vstack(
        [
            mo.md("##raw data dir"),
            mo.ui.text(
                        value=data["raw_data"]["raw_data_dir"],
                        full_width=True,
                    ),
        ]
    )
    return


@app.cell
def _(data, mo):
    mo.vstack(
        [
            mo.md("##open beam dir"),
            mo.ui.text(
                        value=data["open_beam"]["open_beam_data_dir"],
                        full_width=True,
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
                            mo.ui.text(value=str(_x0),
                                       full_width=False,
                                       label=r"x<sub>0</sub>"),
                            mo.ui.text(
                                value=str(_y0),
                                full_width=False,
                                label=r"y<sub>0</sub>",
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
    _size = str(_bins["bin_size"])
    mo.vstack(
        [
            mo.ui.text(value=_x0, label=r"x<sub>0</sub>"),
            mo.ui.text(value=_y0, label=r"y<sub>0</sub>"),
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
            mo.ui.text(value=f"{float(_lambda_min) * 1e10: .4f}", label=u"\u03BB" + r"<sub>min</sub>" + " (\u212b)"),
            mo.ui.text(value=f"{float(_lambda_max) * 1e10: .4f}", label=u"\u03BB" + r"<sub>max</sub>" + " (\u212b)"),
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
    mo.ui.text(value=_d0, label=u"d\u2080" + f" (\u212b)")
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
                label=u"detector offset (\u03BCs)",
                value=data["analysis"]["detector_offset_in_us"],
            ),
        ]
    )
    return


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


@app.cell
def _(mo):
    mo.Html("<hr>")
    return


@app.cell
def _(mo):
    mo.md("""##Repeat analysis for each of the following folders""")
    return


@app.cell
def _(initial_path, mo):
    list_sample_folders_ui = mo.ui.file_browser(
        initial_path=initial_path, multiple=True, selection_mode='directory'
    )
    list_sample_folders_ui
    return (list_sample_folders_ui,)


@app.cell
def _(list_sample_folders_ui, mo):
    mo.vstack(
        [
            mo.Html(f"{len(list_sample_folders_ui.value)} folders (raw sample) have been selected!")
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("## Select where to create the config files & batch script")
    return


@app.cell
def _(initial_path, mo):
    output_folder_ui = mo.ui.file_browser(
        initial_path=initial_path,
        label="",
        multiple=False,
        selection_mode='directory'
    )
    output_folder_ui
    return (output_folder_ui,)


@app.cell
def _(datetime):
    def get_current_time_in_special_file_name_format():
        """format the current date and time into something like  04m_07d_2022y_08h_06mn"""
        current_time = datetime.datetime.now().strftime("%mm_%dd_%Yy_%Hh_%Mmn")
        return current_time
    return (get_current_time_in_special_file_name_format,)


@app.cell
def _(json):
    def save_json(json_file_name, json_dictionary=None):
        with open(json_file_name, "w") as outfile:
            json.dump(json_dictionary, outfile)
    return (save_json,)


@app.cell
def _(
    data,
    get_current_time_in_special_file_name_format,
    list_sample_folders_ui,
    os,
    output_folder_ui,
    save_json,
):
    def create_config_files(param):
        output_folder = output_folder_ui.value
        list_raw_sample_folders = list_sample_folders_ui.value
        config_file = data
        timestamp = get_current_time_in_special_file_name_format()

        for _raw_sample in list_raw_sample_folders:
            output_filename = os.path.join(output_folder, os.path.basename(_raw_sample), f"_config_{timestamp}")
            data['raw_data']['raw_data_dir'] = _raw_sample

            save_json(output_filename, json_dictionary=data)


    return (create_config_files,)


@app.cell
def _(create_config_files, list_sample_folders_ui, mo):
    create_config_button = mo.ui.button(label="Create config files and batch script",
                                        on_click=lambda x: create_config_files(x),
                                        disabled=len(list_sample_folders_ui.value) == 0,
                            )

    mo.vstack(
        [
            mo.md("#Create config files and batch script"),
            create_config_button
        ]
    )
    return (create_config_button,)


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
