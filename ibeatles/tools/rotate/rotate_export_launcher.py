from qtpy.QtWidgets import QDialog
import logging

import warnings
warnings.filterwarnings("ignore")

from ibeatles import load_ui
from ibeatles.tools.rotate.event_handler import EventHandler as RotateEventHandler
from ibeatles import DataType
from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
from ibeatles.tools.tof_combine.utilities.get import Get


class RotateExportLauncher(QDialog):

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent
        QDialog.__init__(self, parent=parent)
        self.ui = load_ui('ui_rotate_export.ui', baseinstance=self)

    def ok_clicked(self):
        o_event = RotateEventHandler(parent=self.parent,
                                     top_parent=self.top_parent)
        output_folder = o_event.select_output_folder()
        if output_folder is None:
            logging.info("User canceled file browser!")
            self.close()

        o_event.rotate_data(output_folder=output_folder)
        self.close()
        self.parent.close()

        # o_get = Get(parent=self)
        # data_type_selected = o_get.combine_export_mode()
        # self.close()
        # output_folder = self.parent.combine_run(data_type_selected=data_type_selected)
        # self.parent.reload_run_in_main_ui(data_type_selected=data_type_selected,
        #                                   output_folder=output_folder)
        # self.parent.close()
        #
        # message = "Rotated images exported to {output_folder}"
        # if not (data_type_selected == DataType.none):
        #     message += f" and loaded back in {data_type_selected}"
        # message += "!"
        #
        # show_status_message(parent=self.top_parent,
        #                     message=message,
        #                     status=StatusMessageStatus.ready,
        #                     duration_s=10)
