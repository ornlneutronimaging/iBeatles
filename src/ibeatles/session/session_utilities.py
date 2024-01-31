from ..all_steps.event_handler import EventHandler as GeneralEventHandler
from ..binning.binning_launcher import BinningLauncher
from ..fitting.fitting_launcher import FittingLauncher
from .. import DataType


class SessionUtilities:

    def __init__(self, parent=None):
        self.parent = parent

    def jump_to_tab_of_data_type(self, data_type=DataType.sample):
        if data_type == DataType.sample:
            return
        elif data_type == DataType.normalization:
            self.parent.ui.tabWidget.setCurrentIndex(1)
        elif data_type == DataType.normalized:
            self.parent.ui.tabWidget.setCurrentIndex(2)
        elif data_type == DataType.bin:
            o_event = GeneralEventHandler(parent=self.parent)
            if o_event.is_step_selected_allowed(step_index_requested=3):
                BinningLauncher(parent=self.parent)
        elif data_type == DataType.fitting:
            self.parent.table_loaded_from_session = True
            o_event = GeneralEventHandler(parent=self.parent)
            if o_event.is_step_selected_allowed(step_index_requested=4):
                BinningLauncher(parent=self.parent)
                FittingLauncher(parent=self.parent)
            self.parent.table_loaded_from_session = False
