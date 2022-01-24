import numpy as np
import logging
import pyqtgraph as pg

from src.iBeatles.fitting.get import Get
from src.iBeatles.fitting.kropff.kropff_bragg_peak_threshold_calculator import KropffBraggPeakThresholdCalculator


class KropffHandler:

    default_threshold_width = 3

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
            is_manual = False
        else:
            logging.info("Manual selection of Bragg peak threshold!")
            is_manual = True
        self.display_bragg_peak_threshold(is_manual=is_manual)
        self.grand_parent.session_dict['fitting']['kropff']["automatic bragg peak threshold finder"] = not is_manual

    def display_bragg_peak_threshold(self, is_manual=False):

        # clear all previously display bragg peak threshold
        if not (self.parent.kropff_threshold_current_item is None):
            self.parent.ui.kropff_fitting.removeItem(self.parent.kropff_threshold_current_item)
            self.parent.kropff_threshold_current_item = None

        # get list of row selected
        o_kropff = Get(parent=self.parent)
        row_selected = str(o_kropff.kropff_row_selected()[0])

        if is_manual:
            # retrieve item of selected row
            # if item is None, make a default selection in the center
            is_item_movable = True

        else:
            # calculate threshold for all rows
            is_item_movable = False
            o_calculator = KropffBraggPeakThresholdCalculator(parent=self.parent,
                                                              grand_parent=self.grand_parent)
            o_calculator.run_automatic_mode()

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        kropff_table_of_row_selected = kropff_table_dictionary[row_selected]
        # retrieve value of threshold range
        left = kropff_table_of_row_selected['bragg peak threshold']['left']
        right = kropff_table_of_row_selected['bragg peak threshold']['right']

        if (not np.isfinite(left)) or (not np.isfinite(right)):
            left, right = self.make_a_rough_estimate_of_threshold(table_of_row_selected=kropff_table_of_row_selected)
            kropff_table_of_row_selected['bragg peak threshold']['left'] = left
            kropff_table_of_row_selected['bragg peak threshold']['right'] = right
        else:
            pass

        # display item and make it enabled or not according to is_manual mode or not
        lr = pg.LinearRegionItem(values=[left, right],
                                 orientation='vertical',
                                 brush=None,
                                 movable=is_item_movable,
                                 bounds=None)
        lr.setZValue(-10)
        if is_item_movable:
            lr.sigRegionChangeFinished.connect(self.parent.kropff_bragg_edge_threshold_changed)
            # lr.sigRegionChanged.connect(self.parent.bragg_edge_linear_region_changing)
        self.parent.ui.kropff_fitting.addItem(lr)
        self.parent.kropff_threshold_current_item = lr

    def make_a_rough_estimate_of_threshold(self, table_of_row_selected=None):
        xaxis = table_of_row_selected['xaxis']
        yaxis = table_of_row_selected['yaxis']

        nbr_x = len(xaxis)
        if nbr_x > self.default_threshold_width:
            center_index = np.floor(nbr_x / 2)
            left_index = int(center_index - np.floor(self.default_threshold_width/2))
            right_index = int(center_index + np.floor(self.default_threshold_width/2))

        else:
            left_index = 0
            right_index = nbr_x - 1

        return xaxis[left_index], xaxis[right_index]

    def kropff_bragg_edge_threshold_changed(self):
        lr = self.parent.kropff_threshold_current_item
        [left, right] = lr.getRegion()

        o_kropff = Get(parent=self.parent)
        row_selected = str(o_kropff.kropff_row_selected()[0])

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        kropff_table_of_row_selected = kropff_table_dictionary[row_selected]
        kropff_table_of_row_selected['bragg peak threshold']['left'] = left
        kropff_table_of_row_selected['bragg peak threshold']['right'] = right
