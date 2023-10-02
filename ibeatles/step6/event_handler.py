import numpy as np

from ibeatles.step6.get import Get
from ibeatles.step6 import ParametersToDisplay
from ibeatles.step6.display import Display


class EventHandler:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def calculate_d_array(self):
        width = self.parent.image_size['width']
        height = self.parent.image_size['height']

        d_array = np.zeros((height, width))
        # d_array[:] = np.NaN
        d_dict = {}

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        for _row_index in kropff_table_dictionary.keys():
            _row_entry = kropff_table_dictionary[_row_index]

            bin_coordinates = _row_entry['bin_coordinates']

            x0 = bin_coordinates['x0']
            x1 = bin_coordinates['x1']
            y0 = bin_coordinates['y0']
            y1 = bin_coordinates['y1']

            lambda_hkl = _row_entry['lambda_hkl']['val']
            lambda_hkl_err = _row_entry['lambda_hkl']['err']
            if lambda_hkl_err is None:
                lambda_hkl_err = np.sqrt(lambda_hkl)

            d_array[y0:y1, x0:x1] = float(lambda_hkl)/2.
            d_dict[_row_index] = {'val': float(lambda_hkl)/2.,
                                  'err': float(lambda_hkl_err)/2.}

        self.parent.d_array = d_array
        self.parent.d_dict = d_dict

    def min_max_changed(self):
        o_display = Display(parent=self.parent,
                            grand_parent=self.grand_parent)
        o_display.run()
