import logging

from .save_tab import SaveTab
from .. import DataType


class SaveNormalizationTab(SaveTab):

    def normalization(self):
        """ record the ROI selected"""

        list_roi = self.parent.list_roi[DataType.normalization]
        state = self.parent.image_view_settings[DataType.normalization]['state']
        histogram = self.parent.image_view_settings[DataType.normalization]['histogram']

        logging.info("Recording normalization information")
        logging.info(f" roi: {list_roi}")
        logging.info(f" state: {state}")
        logging.info(f" histogram: {histogram}")

        self.session_dict[DataType.normalization]['roi'] = list_roi
        self.session_dict[DataType.normalization]['image view state'] = state
        self.session_dict[DataType.normalization]['image view histogram'] = histogram
