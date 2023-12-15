from qtpy.QtWidgets import QFileDialog
import logging
import json

from ..session import SessionKeys
from ..utilities.status_message_config import StatusMessageStatus, show_status_message
from ..bin.manual_event_handler import ManualEventHandler as BinManualEventHandler


class LoadBinTable:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def run(self):
        working_dir = self.parent.session[SessionKeys.top_folder]
        bin_table = QFileDialog.getOpenFileName(caption="Select table bin",
                                                directory=working_dir,
                                                filter="table bin (*.json)")

        bin_table_file_name = bin_table[0]
        if not bin_table_file_name:
            self.logger.info("User cancel loading bin file!")
            return

        with open(bin_table_file_name, 'r') as json_file:
            table = json.load(json_file)

        show_status_message(parent=self.parent,
                            message=f"Bin table loaded from file {bin_table_file_name}",
                            status=StatusMessageStatus.ready,
                            duration_s=10)
        self.logger.info(f"Loaded {bin_table_file_name}!")

        self.parent.manual_bins = table

        o_event = BinManualEventHandler(parent=self.parent)
        o_event.clear_all_items()
        o_event.populate_table_with_this_table(table=table)
        self.parent.update_statistics()
