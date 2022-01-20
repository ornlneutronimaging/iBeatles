import numpy as np
import logging

from .get import Get


class KropffHandler:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def update_fitting_plot(self):
        self.parent.ui.kropff_fitting.clear()

        o_get = Get(parent=self.parent, grand_parent=self.grand_parent)
        yaxis, xaxis = o_get.y_axis_and_x_axis_for_given_rows_selected()

        self.parent.ui.kropff_fitting.setLabel("left", 'Cross Section (arbitrary units, -log(counts))')
        self.parent.ui.kropff_fitting.setLabel("bottom", u'\u03BB (\u212B)')

        for _yaxis in yaxis:
            _yaxis = -np.log(_yaxis)
            self.parent.ui.kropff_fitting.plot(xaxis, _yaxis, symbol='o')

    def kropff_automatic_bragg_peak_threshold_finder_changed(self):
        o_get = Get(parent=self.parent, grand_parent=self.grand_parent)
        automatic_bragg_peak_threshold_finder_activated = o_get.is_automatic_bragg_peak_threshold_finder_activated()
        if automatic_bragg_peak_threshold_finder_activated:
            logging.info("Automatic calculation of Bragg peak threshold!")
            logging.info(f"-> algorithm selected: {self.parent.kropff_automatic_threshold_finder_algorithm}")
        else:
            logging.info("Manual selection of Bragg peak threshold!")
            self.display_bragg_peak_threshold(is_manual=True)

    def display_bragg_peak_threshold(self, is_manual=False):
        pass

        # clear all previously display bragg peak threshold

        # get list of row selected

        # create a vertical linear region range pg.LinearRegionItem (see selected_bin_handler.py line 156)
        # for

        # save
