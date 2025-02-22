import os
from qtpy.uic import loadUi


def load_ui(ui_filename, baseinstance):
    ui_filename = os.path.split(ui_filename)[-1]
    ui_path = os.path.join(os.path.dirname(__file__), "..", "ui")
    filename = os.path.join(ui_path, ui_filename)
    return loadUi(filename, baseinstance=baseinstance)
