import logging

from .save_tab import SaveTab


class SaveBinTab(SaveTab):

    def bin(self):
        """ record the ROI selected"""

        [x0, y0, width, height, bin_size] = self.parent.binning_roi

        logging.info("Recording parameters of bin tab")
        logging.info(f" x0:{x0}, y0:{y0}, width:{width}, height:{height}, bin_size:{bin_size}")

        self.session_dict['bin']['roi'] = [x0, y0, width, height, bin_size]
