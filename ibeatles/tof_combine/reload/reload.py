import logging
import os

from ibeatles import DataType
from ibeatles.session import SessionSubKeys
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.session.load_load_data_tab import LoadLoadDataTab
from ibeatles.session.load_normalized_tab import LoadNormalized
from ibeatles.utilities.gui_handler import GuiHandler
from ibeatles.step1.data_handler import DataHandler
from ibeatles.step1.event_handler import EventHandler as Step1EventHandler


class Reload:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def run(self, data_type=DataType.normalized, output_folder=None):

        if data_type == DataType.none:
            return

        list_tiff = FileHandler.get_list_of_tif(folder=output_folder)
        self.top_parent.session_dict[data_type][SessionSubKeys.list_files] = [os.path.basename(_file) for _file in list_tiff]
        self.top_parent.session_dict[data_type][SessionSubKeys.current_folder] = os.path.dirname(list_tiff[0])
        o_gui = GuiHandler(parent=self.top_parent)

        if data_type == DataType.sample:
            logging.info(f"Reloading TOF combine data in {data_type}")
            o_load = DataHandler(parent=self.top_parent,
                                 data_type=data_type)
            folder = os.path.dirname(list_tiff[0])
            o_load.import_files_from_folder(folder=folder,
                                            extension=[".tiff", ".tif"])
            o_event_step1 = Step1EventHandler(parent=self.top_parent,
                                              data_type=data_type)
            o_event_step1.import_button_clicked_step2(folder=folder)
            self.top_parent.ui.load_data_tab.setCurrentIndex(0)
            self.top_parent.load_data_tab_changed(tab_index=0)
            self.top_parent.ui.tabWidget.setCurrentIndex(0)
            self.top_parent.ui.main_tools_tabWidget.setCurrentIndex(0)
            return

        if data_type == DataType.ob:
            logging.info(f"Reloading TOF combine in {data_type}")
            o_load = DataHandler(parent=self.top_parent,
                                 data_type=data_type)
            folder = os.path.dirname(list_tiff[0])
            o_load.import_files_from_folder(folder=folder,
                                            extension=[".tiff", ".tif"])
            o_event_step1 = Step1EventHandler(parent=self.top_parent,
                                              data_type=data_type)
            o_event_step1.import_button_clicked_step2(folder=folder)
            self.top_parent.ui.load_data_tab.setCurrentIndex(1)
            self.top_parent.load_data_tab_changed(tab_index=1)
            self.top_parent.ui.tabWidget.setCurrentIndex(0)
            self.top_parent.ui.main_tools_tabWidget.setCurrentIndex(0)
            return

        if data_type == DataType.normalized:
            logging.info(f"Reloading TOF combine in {data_type}")
            o_load = LoadNormalized(parent=self.top_parent)
            o_load.all()
            return
