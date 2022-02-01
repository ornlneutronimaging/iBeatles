import pyqtgraph as pg
import numpy as np

from src.iBeatles.fitting.get import Get


class Display:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def display_bragg_peak_threshold(self):
        # clear all previously display bragg peak threshold
        if not (self.parent.kropff_threshold_current_item is None):
            self.parent.ui.kropff_fitting.removeItem(self.parent.kropff_threshold_current_item)
            self.parent.kropff_threshold_current_item = None

        # get list of row selected
        o_kropff = Get(parent=self.parent)
        if o_kropff.kropff_row_selected():
            row_selected = str(o_kropff.kropff_row_selected()[0])
        else:
            return

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        kropff_table_of_row_selected = kropff_table_dictionary[row_selected]
        # retrieve value of threshold range
        left = kropff_table_of_row_selected['bragg peak threshold']['left']
        right = kropff_table_of_row_selected['bragg peak threshold']['right']

        if left is None:
            return

        # display item and make it enabled or not according to is_manual mode or not
        lr = pg.LinearRegionItem(values=[left, right],
                                 orientation='vertical',
                                 brush=None,
                                 movable=True,
                                 bounds=None)
        lr.setZValue(-10)
        lr.sigRegionChangeFinished.connect(self.parent.kropff_bragg_edge_threshold_changed)
        self.parent.ui.kropff_fitting.addItem(lr)
        self.parent.kropff_threshold_current_item = lr

        self.display_lambda_0()

    def update_fitting_parameters_matplotlib(self):
        o_get = Get(parent=self.parent)
        matplotlib_ui = o_get.kropff_matplotlib_ui_selected()
        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        fitting_parameter_to_plot = o_get.kropff_fitting_parameters_radioButton_selected()

        def use_error_bar_plot(array):
            for _value in array:
                if _value is None:
                    return False
            return True

        parameter_array = []
        parameter_error_array = []
        for _row in kropff_table_dictionary.keys():
            _value = kropff_table_dictionary[_row][fitting_parameter_to_plot]['val']
            _error = kropff_table_dictionary[_row][fitting_parameter_to_plot]['err']
            parameter_array.append(_value)
            parameter_error_array.append(_error)

        x_array = np.arange(len(parameter_array))
        matplotlib_ui.axes.cla()
        # if fit_region == 'bragg_peak':
        #     plot_ui.axes.set_yscale("log")

        if use_error_bar_plot(parameter_error_array):
            matplotlib_ui.axes.errorbar(x_array,
                                        parameter_array,
                                        parameter_error_array,
                                        marker='s')
        else:
            matplotlib_ui.axes.plot(x_array,
                                    parameter_array,
                                    marker='s')

        matplotlib_ui.axes.set_xlabel("Row # (see Table tab)")
        matplotlib_ui.draw()

    def display_lambda_0(self):
        pyqtgraph_ui = self.parent.ui.kropff_fitting
        item = self.parent.lambda_0_item_in_kropff_fitting_plot
        