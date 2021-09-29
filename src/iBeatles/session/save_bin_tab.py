import logging

from .save_tab import SaveTab


class SaveBinTab(SaveTab):

    def bin(self):
        """ record the ROI selected"""

        [x0, y0, width, height, bin_size] = self.parent.binning_roi
        binning_line_view = self.parent.binning_line_view['pos']
        formatted_binning_line_view = []
        for _entry in binning_line_view:
            _value1, _value2 = _entry
            formatted_binning_line_view.append([int(_value1), int(_value2)])

        logging.info("Recording parameters of bin tab")
        logging.info(f" x0:{x0}, y0:{y0}, width:{width}, height:{height}, bin_size:{bin_size}")
        logging.info(f" len(binning_line_view): {len(binning_line_view)}")

        self.session_dict['bin']['roi'] = [x0, y0, width, height, bin_size]
        self.session_dict['bin']['binning line view'] = list(formatted_binning_line_view)
