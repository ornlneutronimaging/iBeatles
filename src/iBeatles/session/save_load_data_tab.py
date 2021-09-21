import logging

from .. import DataType
from .save_tab import SaveTab


class SaveLoadDataTab(SaveTab):

    def sample(self):
        """record all the parameters of the Load Data tab / Sample accordion tab"""

        data_type = DataType.sample

        list_files = self.parent.list_files[data_type]
        current_folder = self.parent.data_metadata[data_type]['folder']
        time_spectra_filename = self.parent.data_metadata[data_type]['time_spectra']['filename']
        list_files_selected = [int(index) for index in self.parent.list_file_selected[data_type]]

        logging.info("Recording parameters of Load Data / Sample")
        logging.info(f" len(list files) = {len(list_files)}")
        logging.info(f" current folder: {current_folder}")
        logging.info(f" time spectra filename: {time_spectra_filename}")
        logging.info(f" list files selected: {list_files_selected}")

        self.session_dict[data_type]['list files'] = list_files
        self.session_dict[data_type]['current folder'] = current_folder
        self.session_dict[data_type]['time spectra filename'] = time_spectra_filename
        self.session_dict[data_type]['list files selected'] = list_files_selected

    def ob(self):
        """record all the parameters of the Load Data tab / ob accordion tab"""

        data_type = DataType.ob

        list_files = self.parent.list_files[data_type]
        current_folder = self.parent.data_metadata[data_type]['folder']
        list_files_selected = [int(index) for index in self.parent.list_file_selected[data_type]]

        logging.info("Recording parameters of Load Data / OB")
        logging.info(f" len(list files) = {len(list_files)}")
        logging.info(f" current folder: {current_folder}")
        logging.info(f" list files selected: {list_files_selected}")

        self.session_dict[data_type]['list files'] = list_files
        self.session_dict[data_type]['current folder'] = current_folder
        self.session_dict[data_type]['list files selected'] = list_files_selected
