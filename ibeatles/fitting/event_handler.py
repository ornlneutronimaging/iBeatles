import logging
import numpy as np

from ..utilities.array_utilities import find_nearest_index
from ibeatles.utilities.math_tools import is_float
from .selected_bin_handler import SelectedBinsHandler


class EventHandler:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def bragg_edge_region_changed(self):
        """Updating the x-axis in all units (file index, tof and lambda"""

        # current xaxis is
        x_axis = self.grand_parent.normalized_lambda_bragg_edge_x_axis

        _lr = self.parent.fitting_lr
        if _lr is None:
            return
        selection = list(_lr.getRegion())

        left_index = find_nearest_index(array=x_axis, value=selection[0])
        right_index = find_nearest_index(array=x_axis, value=selection[1])

        list_selected = [left_index, right_index]
        self.grand_parent.fitting_bragg_edge_linear_selection = list_selected

        # display lambda left and right
        lambda_array = self.grand_parent.data_metadata['time_spectra']['normalized_lambda'] * 1e10
        _lambda_min = lambda_array[left_index]
        _lambda_max = lambda_array[right_index]

        self.parent.ui.lambda_min_lineEdit.setText("{:4.2f}".format(_lambda_min))
        self.parent.ui.lambda_max_lineEdit.setText("{:4.2f}".format(_lambda_max))

    def min_or_max_lambda_manually_changed(self):
        try:
            min_lambda = float(str(self.parent.ui.lambda_min_lineEdit.text()))
            max_lambda = float(str(self.parent.ui.lambda_max_lineEdit.text()))

            lambda_array = self.grand_parent.data_metadata['time_spectra']['normalized_lambda'] * 1e10

            left_index = find_nearest_index(array=lambda_array, value=min_lambda)
            right_index = find_nearest_index(array=lambda_array, value=max_lambda)

            self.grand_parent.fitting_bragg_edge_linear_selection = [left_index, right_index]

            o_bin_handler = SelectedBinsHandler(parent=self.parent,
                                                grand_parent=self.grand_parent)
            o_bin_handler.update_bragg_edge_plot()
        except ValueError:
            logging.info("lambda range not yet defined!")

    def hkl_list_changed(self, hkl):
        bragg_edges_array = self.grand_parent.selected_element_bragg_edges_array
        if bragg_edges_array:
            if str(hkl) == '':
                value = "N/A"
            else:
                hkl_array = self.grand_parent.selected_element_hkl_array
                str_hkl_list = ["{},{},{}".format(_hkl[0], _hkl[1], _hkl[2]) for _hkl in hkl_array]
                hkl_bragg_edges = dict(zip(str_hkl_list, bragg_edges_array))
                value = "{:04.3f}".format(hkl_bragg_edges[str(hkl)])
        else:
            value = "N/A"
        self.parent.ui.bragg_edge_calculated.setText(value)

    def check_widgets(self):
        tab_index = self.parent.ui.tabWidget.currentIndex()
        if tab_index == 0:
            show_plot_radio_buttons = True
        else:
            show_plot_radio_buttons = False

        self.parent.ui.plot_label.setVisible(show_plot_radio_buttons)
        self.parent.ui.active_bins_button.setVisible(show_plot_radio_buttons)
        self.parent.ui.locked_bins_button.setVisible(show_plot_radio_buttons)

    def automatically_select_best_lambda_0_for_that_range(self):
        if not self.parent.ui.automatic_hkl0_checkBox.isChecked():
            return

        if not (str(self.parent.ui.lambda_min_lineEdit.text())):
            return

        lambda_min_selected = float(str(self.parent.ui.lambda_min_lineEdit.text()))
        lambda_max_selected = float(str(self.parent.ui.lambda_max_lineEdit.text()))
        mid_lambda = np.mean([lambda_min_selected, lambda_max_selected])

        bragg_edges_array = self.grand_parent.selected_element_bragg_edges_array

        nearest_index = find_nearest_index(bragg_edges_array, mid_lambda)
        self.parent.ui.hkl_list_ui.setCurrentIndex(nearest_index)

    def automatic_hkl0_selection_clicked(self):
        flag_on = self.parent.ui.automatic_hkl0_checkBox.isChecked()
        self.parent.ui.hkl_list_ui.setEnabled(not flag_on)
