from .. import DataType
from ..step2.initialization import Initialization as Step2Initialization
from ..step2.gui_handler import Step2GuiHandler
from ..utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities


class LoadNormalization:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict
        self.data_type = DataType.normalization

    def roi(self):
        data_type = self.data_type
        session_dict = self.session_dict

        list_roi = session_dict[data_type]['roi']
        self.parent.list_roi[data_type] = list_roi

        o_step2 = Step2Initialization(parent=self.parent)
        o_step2.roi()

    def check_widgets(self):
        o_step2 = Step2GuiHandler(parent=self.parent)
        o_step2.check_run_normalization_button()

    def image_settings(self):
        data_type = self.data_type
        session_dict = self.session_dict

        self.parent.image_view_settings[data_type]['state'] = session_dict[data_type]['image view state']
        self.parent.image_view_settings[data_type]['histogram'] = session_dict[data_type]['image view histogram']

        o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                    image_view=self.parent.step2_ui['image_view'],
                                    data_type=data_type)
        o_pyqt.set_state(session_dict[data_type]['image view state'])
        o_pyqt.reload_histogram_level()
        histogram_level = session_dict[data_type]['image view histogram']
        o_pyqt.set_histogram_level(histogram_level=histogram_level)
