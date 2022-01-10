import numpy as np

from .get import Get


class KropffHandler:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def update_fitting_plot(self):
        # index of selection in bragg edge plot
        [left_index, right_index] = self.grand_parent.fitting_bragg_edge_linear_selection

        data_2d = np.array(self.grand_parent.data_metadata['normalized']['data'])
        full_x_axis = self.parent.bragg_edge_data['x_axis']
        x_axis = np.array(full_x_axis[left_index: right_index], dtype=float)

        o_get = Get(parent=self.parent, grand_parent=self.grand_parent)
        y_axis = o_get.y_axis_for_given_rows_selected()
        print(f"x_axis: {x_axis}")
        print(f"y_axis: {y_axis}")
