import logging

from .save_tab import SaveTab
from ..step2 import RegionType
from .. import DataType


class SaveNormalizationTab(SaveTab):

    def normalization(self):
        """ record the ROI selected"""

        list_roi = self.parent.list_roi['normalization']

        logging.info("Recording normalization information")
        logging.info(f" roi: {list_roi}")

        self.session_dict[DataType.normalization]['roi'] = list_roi
