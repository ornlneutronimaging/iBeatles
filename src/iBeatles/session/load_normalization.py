from .. import DataType
from ..step2.gui_handler import Step2GuiHandler


class LoadNormalization:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def roi(self):

        session_dict = self.session_dict

        list_roi = session_dict[DataType.normalization]['roi']
        self.parent.list_roi[DataType.normalization] = list_roi

        o_step2 = Step2GuiHandler(parent=self.parent)
        o_step2.initialize_roi()
