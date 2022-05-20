import logging
import numpy as np

from ibeatles.fitting.kropff.kropff_automatic_threshold_algorithms import Algorithms
from ibeatles.utilities.table_handler import TableHandler


class KropffBraggPeakThresholdCalculator:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def run_automatic_mode(self):
        print(f"in run automatic_mode")
        logging.info(f"Automatic Bragg peak threshold calculator")
        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        algorithm_selected = self.parent.kropff_automatic_threshold_finder_algorithm
        logging.info(f"-> algorithm selected: {algorithm_selected}")
        progress_bar_ui = self.parent.eventProgress

        o_algo = Algorithms(kropff_table_dictionary=kropff_table_dictionary,
                            algorithm_selected=algorithm_selected,
                            progress_bar_ui=progress_bar_ui)

        list_of_threshold_calculated = o_algo.get_peak_value_array(algorithm_selected)
        logging.info(f"-> list of threshold found: {list_of_threshold_calculated}")

        threshold_width = np.int(self.parent.ui.kropff_threshold_width_slider.value())

        for _row_index, _row in enumerate(kropff_table_dictionary.keys()):
            print(f"-> _row_index: {_row_index}")
            print(f"-> _row: {_row}")
            x_axis = kropff_table_dictionary[_row]['xaxis']
            print(f"-> x_axis: {x_axis}")
            left_index = list_of_threshold_calculated[_row_index] - threshold_width
            right_index = list_of_threshold_calculated[_row_index] + threshold_width
            if right_index >= len(x_axis):
                right_index = len(x_axis) - 1
            kropff_table_dictionary[_row]['bragg peak threshold']['left'] = x_axis[left_index]
            kropff_table_dictionary[_row]['bragg peak threshold']['right'] = x_axis[right_index]

        self.grand_parent.kropff_table_dictionary = kropff_table_dictionary

    def save_all_profiles(self, force=False):
        o_table = TableHandler(table_ui=self.parent.ui.high_lda_tableWidget)
        nbr_row = o_table.row_count()
        table_dictionary = self.grand_parent.kropff_table_dictionary
        data_2d = self.grand_parent.data_metadata['normalized']['data']

        # index of selection in bragg edge plot
        [left_index, right_index] = self.grand_parent.fitting_bragg_edge_linear_selection

        run_calculation = False
        for _row in np.arange(nbr_row):
            _bin_entry = table_dictionary[str(_row)]

            if force:
                run_calculation = True
            elif _bin_entry['yaxis'] is None:
                run_calculation = True

            if run_calculation:
                _bin_x0 = _bin_entry['bin_coordinates']['x0']
                _bin_x1 = _bin_entry['bin_coordinates']['x1']
                _bin_y0 = _bin_entry['bin_coordinates']['y0']
                _bin_y1 = _bin_entry['bin_coordinates']['y1']

                yaxis = data_2d[left_index: right_index,
                                _bin_x0: _bin_x1,
                                _bin_y0: _bin_y1,
                                ]  # noqa: E124
                yaxis = np.nanmean(yaxis, axis=1)
                yaxis = np.array(np.nanmean(yaxis, axis=1), dtype=float)
                _bin_entry['yaxis'] = yaxis
                self.grand_parent.kropff_table_dictionary[str(_row)] = _bin_entry

                # index of selection in bragg edge plot
                [left_index, right_index] = self.grand_parent.fitting_bragg_edge_linear_selection
                full_x_axis = self.parent.bragg_edge_data['x_axis']
                xaxis = np.array(full_x_axis[left_index: right_index], dtype=float)
                _bin_entry['xaxis'] = xaxis
