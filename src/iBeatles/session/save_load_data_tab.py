import logging

from .. import DataType
from .save_tab import SaveTab


class SaveLoadDataTab(SaveTab):

    def sample(self):
        """record all the parameters of the Load Data tab / Sample accordion tab"""

        list_files = self.parent.list_files[DataType.sample]
        current_folder = self.parent.data_metadata[DataType.sample]['folder']
        time_spectra_filename = self.parent.data_metadata[DataType.sample]['time_spectra']['filename']
        list_files_selected = [int(index) for index in self.parent.list_file_selected[DataType.sample]]

        logging.info("Recording parameters of Load Data / Sample")
        logging.info(f" len(list files) = {len(list_files)}")
        logging.info(f" current folder: {current_folder}")
        logging.info(f" time spectra filename: {time_spectra_filename}")
        logging.info(f" list files selected: {list_files_selected}")

        self.session_dict[DataType.sample]['list files'] = list_files
        self.session_dict[DataType.sample]['current folder'] = current_folder
        self.session_dict[DataType.sample]['time spectra filename'] = time_spectra_filename
        self.session_dict[DataType.sample]['list files selected'] = list_files_selected
