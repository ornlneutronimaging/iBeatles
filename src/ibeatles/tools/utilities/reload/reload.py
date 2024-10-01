import logging
import os

from src.ibeatles import DataType
from src.ibeatles.session import SessionSubKeys
from src.ibeatles.utilities.file_handler import FileHandler
from src.ibeatles.step1.data_handler import DataHandler
from src.ibeatles.step1.event_handler import EventHandler as Step1EventHandler
from src.ibeatles.step3.event_handler import EventHandler as Step3EventHandler


class Reload:
    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def run(self, data_type=DataType.normalized, output_folder=None):
        if data_type == DataType.none:
            return

        list_tiff = FileHandler.get_list_of_tif(folder=output_folder)
        self.top_parent.session_dict[data_type][SessionSubKeys.list_files] = [
            os.path.basename(_file) for _file in list_tiff
        ]
        self.top_parent.session_dict[data_type][SessionSubKeys.current_folder] = (
            os.path.dirname(list_tiff[0])
        )

        if data_type == DataType.sample:
            self._raw_data(
                list_files=list_tiff, load_data_tab_index=0, data_type=data_type
            )
        elif data_type == DataType.ob:
            self._raw_data(
                list_files=list_tiff, load_data_tab_index=1, data_type=data_type
            )
        elif data_type == DataType.normalized:
            self._normalized_data(list_files=list_tiff)

    def _normalized_data(self, list_files=None):
        """this takes care of loading the files back in the normalized tab"""
        data_type = DataType.normalized
        logging.info(f"Reloading TOF combine data in {data_type}")
        o_load = DataHandler(parent=self.top_parent, data_type=data_type)
        folder = os.path.dirname(list_files[0])
        o_load.import_files_from_folder(folder=folder, extension=[".tiff", ".tif"])
        o_load.import_time_spectra()
        o_event_step3 = Step3EventHandler(parent=self.top_parent, data_type=data_type)
        o_event_step3.update_ui_after_loading_data(folder=folder)
        o_event_step3.check_time_spectra_status()
        self.top_parent.infos_window_update(data_type=data_type)
        self.top_parent.ui.normalized_splitter.setSizes([20, 450])
        self.top_parent.ui.main_tools_tabWidget.setCurrentIndex(1)
        self.top_parent.ui.tabWidget.setCurrentIndex(2)

    def _raw_data(
        self, list_files=None, load_data_tab_index=0, data_type=DataType.sample
    ):
        """This takes care of loading the files into the appropriate sample or OB tab"""
        logging.info(f"Reloading TOF combine data in {data_type}")
        o_load = DataHandler(parent=self.top_parent, data_type=data_type)
        folder = os.path.dirname(list_files[0])
        o_load.import_files_from_folder(folder=folder, extension=[".tiff", ".tif"])
        o_event_step1 = Step1EventHandler(parent=self.top_parent, data_type=data_type)
        o_event_step1.import_button_clicked_step2(folder=folder)
        self.top_parent.ui.load_data_tab.setCurrentIndex(load_data_tab_index)
        self.top_parent.load_data_tab_changed(tab_index=load_data_tab_index)
        self.top_parent.ui.tabWidget.setCurrentIndex(0)
        self.top_parent.ui.main_tools_tabWidget.setCurrentIndex(0)
