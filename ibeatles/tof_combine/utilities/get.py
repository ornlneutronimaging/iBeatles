import os
from os.path import expanduser
from pathlib import Path
import tomli
import copy
import numpy as np

from ibeatles.tof_combine.utilities.table_handler import TableHandler
from ibeatles.tof_combine.utilities import CombineAlgorithm, TimeSpectraKeys
from ibeatles.session import SessionKeys


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

    def list_array_to_combine(self):
        session = self.parent.session
        list_working_folders_status = session[SessionKeys.list_working_folders_status]
        raw_data_folders = self.parent.raw_data_folders
        list_working_folders = session[SessionKeys.list_working_folders]

        if list_working_folders is None:
            return

        list_array = []
        for _status, _folder_name in zip(list_working_folders_status, list_working_folders):
            if _status:
                list_array.append(copy.deepcopy(raw_data_folders[_folder_name]['data']))

        return list_array

    def list_of_folders_to_use(self):
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        nbr_row = o_table.row_count()
        list_of_folders_to_use = []
        list_of_folders_to_use_status = []
        for _row_index in np.arange(nbr_row):
            _horizontal_widget = o_table.get_widget(row=_row_index,
                                                    column=0)
            radio_button = _horizontal_widget.layout().itemAt(1).widget()
            if radio_button.isChecked():
                list_of_folders_to_use.append(o_table.get_item_str_from_cell(row=_row_index,
                                                                             column=2))
                status = True
            else:
                status = False
            list_of_folders_to_use_status.append(status)

        return list_of_folders_to_use

    def manual_working_row(self, working_item_id=None):
        list_item_id = self.parent.list_of_manual_bins_item
        for _row, item in enumerate(list_item_id):
            if item == working_item_id:
                return _row
        return -1

    @staticmethod
    def full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name

    @staticmethod
    def version():
        setup_cfg = 'pyproject.toml'
        this_folder = os.path.abspath(os.path.dirname(__file__))
        top_path = Path(this_folder).parent.parent
        full_path_setup_cfg = str(Path(top_path) / Path(setup_cfg))

        ## to read from pyproject.toml file
        with open(full_path_setup_cfg, 'rb') as fp:
            config = tomli.load(fp)
        version = config['project']['version']

        ## to read from setup.cfg file
        # config = configparser.ConfigParser()
        # config.read(full_path_setup_cfg)
        # version = config['project']['version']
        return version
