import logging
import os

from ibeatles import DataType
from ibeatles.session import SessionSubKeys
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.session.load_load_data_tab import LoadLoadDataTab
from ibeatles.session.load_normalized_tab import LoadNormalized
from ibeatles.utilities.gui_handler import GuiHandler


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
            o_load = LoadLoadDataTab(parent=self.top_parent)
            o_load.sample()
            o_gui.set_tab(tab_index=0)
            self.top_parent.load_data_tab_changed(0)
            self.top_parent.ui.sample_ob_splitter.setSizes([20, 450])
            return

        if data_type == DataType.ob:
            logging.info(f"Reloading TOF combine in {data_type}")
            o_load = LoadLoadDataTab(parent=self.top_parent)
            o_load.ob()
            o_gui.set_tab(tab_index=1)
            self.top_parent.load_data_tab_changed(1)
            self.top_parent.ui.sample_ob_splitter.setSizes([20, 450])
            return

        if data_type == DataType.normalized:
            logging.info(f"Reloading TOF combine in {data_type}")
            o_load = LoadNormalized(parent=self.top_parent)
            o_load.all()

            return
