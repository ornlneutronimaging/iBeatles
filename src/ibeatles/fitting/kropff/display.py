import pyqtgraph as pg
import numpy as np

from src.ibeatles.fitting.kropff.get import Get as GetKropff
from src.ibeatles.utilities.display import Display as UtilitiesDisplay


class Display:
    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def display_bragg_peak_threshold(self):
        # clear all previously display bragg peak threshold
        if self.parent.kropff_threshold_current_item is not None:
            self.parent.ui.kropff_fitting.removeItem(
                self.parent.kropff_threshold_current_item
            )
            self.parent.kropff_threshold_current_item = None

        # get list of row selected
        o_kropff = GetKropff(parent=self.parent)
        if o_kropff.kropff_row_selected():
            row_selected = str(o_kropff.kropff_row_selected()[0])
        else:
            return

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        kropff_table_of_row_selected = kropff_table_dictionary[row_selected]

        # retrieve value of threshold range
        left = kropff_table_of_row_selected["bragg peak threshold"]["left"]
        right = kropff_table_of_row_selected["bragg peak threshold"]["right"]

        if left is None:
            return

        # display item and make it enabled or not according to is_manual mode or not
        lr = pg.LinearRegionItem(
            values=[left, right],
            orientation="vertical",
            brush=None,
            movable=True,
            bounds=None,
        )
        lr.setZValue(-10)
        lr.sigRegionChangeFinished.connect(
            self.parent.kropff_bragg_edge_threshold_changed
        )
        self.parent.ui.kropff_fitting.addItem(lr)
        self.parent.kropff_threshold_current_item = lr

        self.display_lambda_0()
        self.display_lambda_calculated()

    def update_fitting_parameters_matplotlib(self):
        o_get = GetKropff(parent=self.parent)
        matplotlib_ui = o_get.kropff_matplotlib_ui_selected()
        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        fitting_parameter_to_plot = (
            o_get.kropff_fitting_parameters_radioButton_selected()
        )

        if not fitting_parameter_to_plot:
            return

        def use_error_bar_plot(array):
            for _value in array:
                if _value is None:
                    return False
            return True

        parameter_array = []
        parameter_error_array = []
        for _row in kropff_table_dictionary.keys():
            _value = kropff_table_dictionary[_row][fitting_parameter_to_plot]["val"]
            _error = kropff_table_dictionary[_row][fitting_parameter_to_plot]["err"]
            parameter_array.append(_value)
            parameter_error_array.append(_error)

        x_array = np.arange(len(parameter_array))
        matplotlib_ui.axes.cla()
        # if fit_region == 'bragg_peak':
        #     plot_ui.axes.set_yscale("log")

        if len(np.where(np.isnan(parameter_array))[0]) == len(parameter_array):
            # nothing to plot because all data points are NaN
            return

        if use_error_bar_plot(parameter_error_array):
            matplotlib_ui.axes.errorbar(
                x_array,
                parameter_array,
                parameter_error_array,
                marker="o",
                linestyle="",
                markeredgecolor="red",
                markerfacecolor="green",
                label="\u03bb_calculated",
                ecolor="red",
            )
        else:
            matplotlib_ui.axes.plot(
                x_array,
                parameter_array,
                marker="o",
                linestyle="",
                markeredgecolor="red",
                markerfacecolor="green",
                label="\u03bb_calculated",
            )

        matplotlib_ui.axes.set_xlabel("Row # (see Table tab)")
        matplotlib_ui.axes.set_ylabel(fitting_parameter_to_plot)

        # for the lambda_hkl, display the lambda_0 as a reference
        if fitting_parameter_to_plot == "lambda_hkl":
            lambda_0 = float(str(self.parent.ui.bragg_edge_calculated.text()))
            matplotlib_ui.axes.hlines(
                lambda_0,
                xmin=0,
                xmax=len(x_array),
                colors="b",
                linestyles="dotted",
                label="\u03bb\u2080",
            )
            matplotlib_ui.axes.legend(loc="upper center")

        matplotlib_ui.draw()

    def display_lambda_0(self):
        pyqtgraph_ui = self.parent.ui.kropff_fitting
        item = self.parent.lambda_0_item_in_kropff_fitting_plot
        lambda_position = float(str(self.parent.ui.bragg_edge_calculated.text()))

        o_utility_display = UtilitiesDisplay(ui=pyqtgraph_ui)
        new_item = o_utility_display.vertical_line(
            item=item, x_position=lambda_position
        )
        self.parent.lambda_0_item_in_kropff_fitting_plot = new_item

    def display_lambda_calculated(self):
        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        o_kropff = GetKropff(parent=self.parent)
        row_selected = str(o_kropff.kropff_row_selected()[0])
        kropff_table_of_row_selected = kropff_table_dictionary[row_selected]
        lambda_value = kropff_table_of_row_selected["lambda_hkl"]["val"]

        # in bragg edge plot (top plot)
        item = self.parent.lambda_calculated_item_in_bragg_edge_plot
        o_utility_display = UtilitiesDisplay(ui=self.parent.bragg_edge_plot)
        new_item = o_utility_display.vertical_line(
            item=item,
            x_position=lambda_value,
            label="\u03bb_calculated",
            pen=pg.mkPen(color="g", width=1.5),
        )
        self.parent.lambda_calculated_item_in_bragg_edge_plot = new_item

        # in kropff fitting plot (bottom right)
        item = self.parent.lambda_calculated_item_in_kropff_fitting_plot
        o_utility_display = UtilitiesDisplay(ui=self.parent.ui.kropff_fitting)
        new_item = o_utility_display.vertical_line(
            item=item,
            x_position=lambda_value,
            label="\u03bb_calculated",
            pen=pg.mkPen(color="g", width=1.5),
        )
        self.parent.lambda_calculated_item_in_kropff_fitting_plot = new_item
