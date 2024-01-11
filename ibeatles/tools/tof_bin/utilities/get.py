import os
from os.path import expanduser
from pathlib import Path
import tomli
import copy
import numpy as np

from ibeatles import DataType

from ibeatles.tools.utilities import TimeSpectraKeys
from ibeatles.tools.utilities import CombineAlgorithm

# from ibeatles.tools.tof_combine.utilities.table_handler import TableHandler
# from ibeatles.tools.tof_combine import SessionKeys as TofSessionKeys


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def x_axis_selected(self):
        if self.parent.bin_file_index_radioButton.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.bin_tof_radioButton.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.bin_lambda_radioButton.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError("xaxis not implemented in the bin tab!")
