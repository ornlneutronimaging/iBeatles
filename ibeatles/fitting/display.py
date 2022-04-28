import numpy as np

from ibeatles.utilities.display import Display as UtilitiesDisplay


class Display:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def display_lambda_0(self):
        pyqtgraph_ui = self.parent.bragg_edge_plot
        item = self.parent.lambda_0_item_in_bragg_edge_plot
        lambda_position = np.float(str(self.parent.ui.bragg_edge_calculated.text()))

        o_utility_display = UtilitiesDisplay(ui=pyqtgraph_ui)
        new_item = o_utility_display.vertical_line(item=item,
                                                   x_position=lambda_position)
        self.parent.lambda_0_item_in_bragg_edge_plot = new_item
