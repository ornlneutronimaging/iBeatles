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

        for row_key in kropff_table_dictionary.keys():
            print(f"row_key: {row_key}")

            xaxis = kropff_table_dictionary[row_key]['xaxis']
            yaxis = kropff_table_dictionary[row_key]['yaxis']

            print(f"-> xaxis: {xaxis}")
            print(f"-> yaxis: {yaxis}")

        # o_algo = Algorithms(kropff_table_dictionary=kropff_table_dictionary,
        #                     algorithm_selected=algorithm_selected,
        #                     progress_bar_ui=progress_bar_ui)
        # print(f"o_algo.get_peak_value_array: {o_algo.get_peak_value_array(algorithm_selected)}")
