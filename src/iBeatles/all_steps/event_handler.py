from .. import DataType
from ..utilities.status_message_config import StatusMessageStatus, show_status_message
from qtpy.QtWidgets import QMessageBox
import logging


class EventHandler:

    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type

    def _display_status_message_warning(self, message=""):
        show_status_message(parent=self.parent,
                            status=StatusMessageStatus.warning,
                            message=message,
                            duration_s=5)

    def is_step_selected_allowed(self, step_index_requested=0):
        """ 0: load data
            1: normalization
            2: normalized
            3: bin
            4: fit
            5: strain mapping
            6: rotation
        """

        # load tab
        # validate all the time
        if step_index_requested == 0:
            return True

        # normalization
        # validate only if data loaded
        if step_index_requested == 1:

            if self.parent.data_metadata[DataType.sample]['data'] == []:
                message = "Please load some sample data!"
                self._display_status_message_warning(message=message)
                self._display_message_box(message=message)
                EventHandler._update_logging(step_requested=step_index_requested,
                                             message=message)
                return False
            return True

        # normalized
        # validate all the time
        if step_index_requested == 2:
            return True

        # bin
        # validate only if normalized data loaded
        if step_index_requested == 3:
            if self.parent.data_metadata[DataType.normalized]['data'] == []:
                message = "Please load some normalized data!"
                self._display_status_message_warning(message=message)
                self._display_message_box(message=message)
                EventHandler._update_logging(step_requested=step_index_requested,
                                             message=message)
                return False
            return True

        # fitting
        # validate if there is a bin region selected
        if step_index_requested == 4:
            if self.parent.data_metadata[DataType.normalized]['data'] == []:
                message = "Please load some normalized data!"
                self._display_status_message_warning(message=message)
                self._display_message_box(message=message)
                EventHandler._update_logging(step_requested=step_index_requested,
                                             message=message)
                return False
            if not self.parent.there_is_a_roi:
                message = "Please select a region to bin first (step binning)!"
                self._display_status_message_warning(message=message)
                self._display_message_box(message=message)
                EventHandler._update_logging(step_requested=step_index_requested,
                                             message=message)
                return False
            return True

        # strain mapping
        # validate if fitting has been performed
        if step_index_requested == 5:
            if self.parent.march_table_dictionary == {}:
                message = "Please fit the data to be able to visualize the strain mapping!"
                self._display_status_message_warning(message=message)
                self._display_message_box(message=message)
                EventHandler._update_logging(step_requested=step_index_requested,
                                             message=message)
                return False
            return True

        # rotation
        # validate if normalized data loaded
        if step_index_requested == 6:
            if self.parent.data_metadata[DataType.normalized]['data'] == []:
                message = "Please load some normalized data!"
                self._display_status_message_warning(message=message)
                self._display_message_box(message=message)
                EventHandler._update_logging(step_requested=step_index_requested,
                                             message=message)
                return False
            return True

        return True

    def _display_message_box(self, message=""):
        dlg = QMessageBox(self.parent)
        dlg.setWindowTitle("Unable to start this step!")
        dlg.setText(message)
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.setIcon(QMessageBox.Warning)
        button = dlg.exec()

        if button == QMessageBox.Ok:
            dlg.close()

    @staticmethod
    def _update_logging(step_requested=-1, message=""):
        logging.info(f"Error requesting step #{step_requested}")
        logging.info(message)
