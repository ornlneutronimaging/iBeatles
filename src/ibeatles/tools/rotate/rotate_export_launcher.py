from qtpy.QtWidgets import QDialog, QApplication
import logging

import warnings
warnings.filterwarnings("ignore")

from src.ibeatles import load_ui
from src.ibeatles import DataType
from src.ibeatles.tools.rotate.event_handler import EventHandler as RotateEventHandler
from src.ibeatles.tools.utilities.reload.reload import Reload


class RotateExportLauncher(QDialog):

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent
        QDialog.__init__(self, parent=parent)
        self.ui = load_ui('ui_rotate_export.ui', baseinstance=self)

    def ok_clicked(self):
        self.parent.ui.setEnabled(False)
        o_event = RotateEventHandler(parent=self.parent,
                                     top_parent=self.top_parent)
        output_folder = o_event.select_output_folder()
        if output_folder is None:
            logging.info("User canceled file browser!")
            self.close()

        self.close()
        full_output_folder_name = o_event.rotate_data(output_folder=output_folder)
        self.parent.close()

        if self.ui.reload_checkBox.isChecked():

            o_reload = Reload(parent=self.parent,
                              top_parent=self.top_parent)
            o_reload.run(data_type=DataType.normalized,
                         output_folder=full_output_folder_name)

        self.parent.ui.setEnabled(True)
        QApplication.restoreOverrideCursor()
