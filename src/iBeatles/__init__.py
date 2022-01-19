import os
from qtpy.uic import loadUi
from src.iBeatles import ui
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

root = os.path.dirname(os.path.realpath(__file__))
refresh_image = os.path.join(root, "icons/refresh.png")
up_icon = os.path.join(root, "icons/up_arrow.png")
down_icon = os.path.join(root, "icons/down_arrow.png")
settings_icon = os.path.join(root, "icons/plotSettings.png")

DEFAULT_ROI = ['default', '0', '0', '20', '20', '0']
DEFAULT_NORMALIZATION_ROI = [True, '0', '0', '20', '20', 'background']
DEFAULT_BIN = [0, 0, 20, 20, 10]
BINNING_LINE_COLOR = (255, 0, 0, 255, 1.)


class DataType:
    sample = 'sample'
    ob = 'ob'
    df = 'df'
    normalized = 'normalized'
    normalization = 'normalization'
    bin = "bin"
    fitting = "fitting"


class RegionType:
    sample = 'sample'
    background = 'background'


def load_ui(ui_filename, baseinstance):
    ui_filename = os.path.split(ui_filename)[-1]
    ui_path = os.path.dirname(ui.__file__)

    # get the location of the ui directory
    # this function assumes that all ui files are there
    filename = os.path.join(ui_path, ui_filename)

    return loadUi(filename, baseinstance=baseinstance)