import logging

from src.iBeatles.fitting.kropff.kropff_automatic_threshold_algorithms import Algorithms
from src.iBeatles.fitting import KropffThresholdFinder


class KropffBraggPeakThresholdCalculator:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def run_automatic_mode(self):
        logging.info(f"Automatic Bragg peak threshold calculator")
        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        algorithm_selected = self.parent.kropff_automatic_threshold_finder_algorithm
        logging.info(f"-> algorithm selected: {algorithm_selected}")
        progress_bar_ui = self.parent.eventProgress

        algorithm_selected = KropffThresholdFinder.sliding_average

        o_algo = Algorithms(kropff_table_dictionary=kropff_table_dictionary,
                            algorithm_selected=algorithm_selected,
                            progress_bar_ui=progress_bar_ui)

        list_of_threshold_calculated = o_algo.get_peak_value_array(algorithm_selected)
        for _row_index, _row in enumerate(kropff_table_dictionary.keys()):
            x_axis = kropff_table_dictionary[_row]['xaxis']
            left_index = list_of_threshold_calculated[_row_index] - 3
            right_index = list_of_threshold_calculated[_row_index] + 3
            if right_index >= len(x_axis):
                right_index = len(x_axis) - 1
            kropff_table_dictionary[_row]['bragg peak threshold']['left'] = x_axis[left_index]
            kropff_table_dictionary[_row]['bragg peak threshold']['right'] = x_axis[right_index]

        self.grand_parent.kropff_table_dictionary = kropff_table_dictionary

        print(f"o_algo.get_peak_value_array: {o_algo.get_peak_value_array(algorithm_selected)}")
