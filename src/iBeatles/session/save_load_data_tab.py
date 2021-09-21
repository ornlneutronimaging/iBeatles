import logging

from .. import DataType
from .save_tab import SaveTab


class SaveLoadDataTab(SaveTab):

    def sample(self):
        """record all the parameters of the Load Data tab / Sample accordion tab"""

        list_files_selected = self.parent.list_file_selected[DataType.sample]
        current_folder = self.parent.data_metadata[DataType.sample]['folder']
        time_spectra_filename = self.parent.data_metadata[DataType.sample]['time_spectra']['filename']
        time_spectra_folder = self.parent.data_metadata[DataType.sample]['time_spectra']['folder']

        logging.info("Recording parameters of Load Data / Sample")
        logging.info(f" len(list_files_selected) = {len(list_files_selected)}")
        logging.info(f" current_folder: {current_folder}")
        logging.info(f" time_spectra_filename: {time_spectra_filename}")
        logging.info(f" time_spectra_folder: {time_spectra_folder}")
