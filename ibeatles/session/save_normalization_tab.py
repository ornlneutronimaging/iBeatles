import logging

from ibeatles import DataType
from ibeatles.utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities

from ibeatles.session import SessionKeys, SessionSubKeys
from ibeatles.session.save_tab import SaveTab


class SaveNormalizationTab(SaveTab):

    def normalization(self):
        """ record the ROI selected"""

        data_type = DataType.normalization
        list_roi = self.parent.list_roi[data_type]

        o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                    image_view=self.parent.step2_ui['image_view'],
                                    data_type=data_type)
        state = o_pyqt.get_state()
        o_pyqt.save_histogram_level()
        histogram = self.parent.image_view_settings[data_type]['histogram']

        logging.info("Recording normalization information")
        logging.info(f" roi: {list_roi}")
        logging.info(f" state: {state}")
        logging.info(f" histogram: {histogram}")

        self.session_dict[data_type][SessionSubKeys.roi] = list_roi
        self.session_dict[data_type][SessionSubKeys.image_view_state] = state
        self.session_dict[data_type][SessionSubKeys.image_view_histogram] = histogram
