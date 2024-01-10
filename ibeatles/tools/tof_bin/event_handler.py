import os
from qtpy.QtWidgets import QFileDialog
import logging

from ibeatles import DataType
from ibeatles.session import SessionSubKeys
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message



class EventHandler:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def check_widgets(self):
        folder_selected = self.parent.ui.folder_selected.text()
        if os.path.exists(folder_selected):
            enabled_state = True
        else:
            enabled_state = False

        self.parent.ui.bin_tabWidget.setEnabled(enabled_state)
        self.parent.ui.x_axis_groupBox.setEnabled(enabled_state)
        self.parent.ui.stats_tabWidget.setEnabled(enabled_state)
        self.parent.ui.bin_bottom_tabWidget.setEnabled(enabled_state)
        self.parent.ui.bin_settings_pushButton.setEnabled(enabled_state)
        self.parent.ui.export_bin_table_pushButton.setEnabled(enabled_state)
        self.parent.ui.export_pushButton.setEnabled(enabled_state)

    def select_input_folder(self):
        default_path = self.top_parent.session_dict[DataType.sample][SessionSubKeys.current_folder]
        folder = str(QFileDialog.getExistingDirectory(caption="Select folder containing images to load",
                                                      directory=default_path,
                                                      options=QFileDialog.ShowDirsOnly))
        if folder == "":
            logging.info("User Canceled the selection of folder!")
            return

        list_tif_files = FileHandler.get_list_of_tif(folder=folder)
        if not list_tif_files:
            logging.info(f"-> folder does not contain any tif file!")
            show_status_message(parent=self.parent,
                                message=f"Folder {os.path.basename(folder)} does not contain any TIFF files!",
                                duration_s=5,
                                status=StatusMessageStatus.error)
            return

        self.parent.ui.folder_selected.setText(folder)
        logging.info(f"Users selected the folder: {folder}")
        self.parent.list_tif_files = list_tif_files
