import numpy as np

from src.ibeatles.step6 import Get
from src.ibeatles.step6 import Display
from src.ibeatles.fitting.kropff.get import Get as GetKropff


class EventHandler:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

        self.width = self.parent.image_size['width']
        self.height = self.parent.image_size['height']

        o_get = GetKropff(grand_parent=self.grand_parent)
        self.nbr_row = o_get.nbr_row()
        self.nbr_column = o_get.nbr_column()

    def process_data(self):
        self.calculate_d_array()
        self.calculate_strain_mapping_array()

    def calculate_d_array(self):
        d_array = np.empty((self.height, self.width))
        d_array[:] = np.NaN

        compact_d_array = np.empty((self.nbr_row, self.nbr_column))

        d_dict = {}

        top_left_corner_of_roi = [self.height, self.width]

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        for _row_index in kropff_table_dictionary.keys():
            _row_entry = kropff_table_dictionary[_row_index]

            bin_coordinates = _row_entry['bin_coordinates']
            x0 = bin_coordinates['x0']
            x1 = bin_coordinates['x1']
            y0 = bin_coordinates['y0']
            y1 = bin_coordinates['y1']

            row_index = _row_entry['row_index']
            column_index = _row_entry['column_index']

            if x0 < top_left_corner_of_roi[1]:
                top_left_corner_of_roi[1] = x0

            if y0 < top_left_corner_of_roi[0]:
                top_left_corner_of_roi[0] = y0

            lambda_hkl = _row_entry['lambda_hkl']['val']
            lambda_hkl_err = _row_entry['lambda_hkl']['err']
            if lambda_hkl_err is None:
                lambda_hkl_err = np.sqrt(lambda_hkl)

            d_array[y0:y1, x0:x1] = float(lambda_hkl)/2.
            compact_d_array[row_index, column_index] = float(lambda_hkl)/2.

            d_dict[_row_index] = {'val': float(lambda_hkl)/2.,
                                  'err': float(lambda_hkl_err)/2.}

        self.parent.d_array = d_array
        self.parent.compact_d_array = compact_d_array
        self.parent.d_dict = d_dict
        self.parent.top_left_corner_of_roi = top_left_corner_of_roi

    def calculate_strain_mapping_array(self):
        d_array = self.parent.d_array
        compact_d_array = self.parent.compact_d_array

        o_get = Get(parent=self.parent)
        d0 = o_get.active_d0()

        self.parent.strain_mapping_array = (d_array - d0) / d0
        self.parent.compact_strain_mapping_array = (compact_d_array - d0) / d0

    def min_max_changed(self):
        o_display = Display(parent=self.parent,
                            grand_parent=self.grand_parent)
        o_display.run()

    def interpolation_cmap_method_changed(self):
        o_display = Display(parent=self.parent,
                            grand_parent=self.grand_parent)
        o_display.run()
