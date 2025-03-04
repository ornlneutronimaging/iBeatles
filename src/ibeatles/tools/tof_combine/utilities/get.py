import os
from os.path import expanduser
from pathlib import Path
import tomli
import copy
import numpy as np

from src.ibeatles import DataType

from src.ibeatles.tools.utilities import TimeSpectraKeys
from src.ibeatles.tools.utilities import CombineAlgorithm

from src.ibeatles.tools.tof_combine.utilities.table_handler import TableHandler
from src.ibeatles.tools.tof_combine import SessionKeys as TofSessionKeys


class Get:
    def __init__(self, parent=None):
        self.parent = parent

    def combine_algorithm(self):
        if self.parent.ui.combine_mean_radioButton.isChecked():
            return CombineAlgorithm.mean
        elif self.parent.ui.combine_median_radioButton.isChecked():
            return CombineAlgorithm.median
        else:
            raise NotImplementedError("Combine algorithm not implemented!")

    def combine_x_axis_selected(self):
        if self.parent.combine_file_index_radio_button.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.tof_radio_button.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.lambda_radio_button.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError("xaxis not implemented in the combine tab!")

    def list_of_folders_status(self):
        """return a dict of the folder status (True if the checkbox is checked)"""
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        nbr_row = o_table.row_count()
        dict_folders_status = {}
        for _row_index in np.arange(nbr_row):
            _horizontal_widget = o_table.get_widget(row=_row_index, column=0)
            radio_button = _horizontal_widget.layout().itemAt(1).widget()
            if radio_button.isChecked():
                dict_folders_status[_row_index] = True
            else:
                dict_folders_status[_row_index] = False

        return dict_folders_status

    def number_of_folders_we_want_to_combine(self):
        """return the number of folders with the radio button checked (we want to be part of the combine)"""
        nbr_folders = 0
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        nbr_row = o_table.row_count()
        for _row_index in np.arange(nbr_row):
            _horizontal_widget = o_table.get_widget(row=_row_index, column=0)
            radio_button = _horizontal_widget.layout().itemAt(1).widget()
            if radio_button.isChecked():
                nbr_folders += 1

        return nbr_folders

    def row_of_that_folder(self, folder):
        """returns the row number where the folder has been found"""
        for _row in self.parent.dict_data_folders.keys():
            if self.parent.dict_data_folders[_row][TofSessionKeys.folder] == folder:
                return _row
        return -1

    def list_array_to_combine(self):
        """return the list of array to combine (list folders with checkbox checked"""

        list_row_to_use = []
        for _row in self.parent.dict_data_folders.keys():
            if self.parent.dict_data_folders[_row][TofSessionKeys.use]:
                list_row_to_use.append(_row)

        if not list_row_to_use:
            return None

        list_array = []
        for _row in list_row_to_use:
            list_array.append(
                copy.deepcopy(self.parent.dict_data_folders[_row][TofSessionKeys.data])
            )

        return list_array

    def manual_working_row(self, working_item_id=None):
        list_item_id = self.parent.list_of_manual_bins_item
        for _row, item in enumerate(list_item_id):
            if item == working_item_id:
                return _row
        return -1

    def combine_export_mode(self):
        if self.parent.ui.none_radioButton.isChecked():
            return DataType.none
        elif self.parent.ui.sample_radioButton.isChecked():
            return DataType.sample
        elif self.parent.ui.ob_radioButton.isChecked():
            return DataType.ob
        elif self.parent.ui.normalized_radioButton.isChecked():
            return DataType.normalized
        else:
            raise NotImplementedError("export mode not implemented yet!")

    @staticmethod
    def full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name

    @staticmethod
    def version():
        setup_cfg = "pyproject.toml"
        this_folder = os.path.abspath(os.path.dirname(__file__))
        top_path = Path(this_folder).parent.parent
        full_path_setup_cfg = str(Path(top_path) / Path(setup_cfg))

        ## to read from pyproject.toml file
        with open(full_path_setup_cfg, "rb") as fp:
            config = tomli.load(fp)
        version = config["project"]["version"]

        ## to read from setup.cfg file
        # config = configparser.ConfigParser()
        # config.read(full_path_setup_cfg)
        # version = config['project']['version']
        return version
