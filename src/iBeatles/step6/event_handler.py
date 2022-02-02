import numpy as np


class EventHandler:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def calculate_d_array(self):
        width = self.parent.image_size['width']
        height = self.parent.image_size['height']

        d_array = np.empty((height, width))

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        for _row_index in kropff_table_dictionary.keys():
            _row_entry = kropff_table_dictionary[_row_index]

            bin_coordinates = _row_entry['bin_coordinates']

            x0 = bin_coordinates['x0']
            x1 = bin_coordinates['x1']
            y0 = bin_coordinates['y0']
            y1 = bin_coordinates['y1']

            lambda_hkl = _row_entry['lambda_hkl']['val']

            d_array[y0:y1, x0:x1] = np.float(lambda_hkl)/2.

        self.parent.d_array = d_array
