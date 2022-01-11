import numpy as np

from .get import Get


class KropffHandler:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def update_fitting_plot(self):
        self.parent.ui.kropff_fitting.clear()

        o_get = Get(parent=self.parent, grand_parent=self.grand_parent)
        yaxis, xaxis = o_get.y_axis_and_x_axis_for_given_rows_selected()

        self.parent.ui.kropff_fitting.setLabel("left", 'Cross Section (arbitrary units, -log(counts))')
        self.parent.ui.kropff_fitting.setLabel("bottom", u'\u03BB (\u212B)')

        for _yaxis in yaxis:
            _yaxis = -np.log(_yaxis)
            self.parent.ui.kropff_fitting.plot(xaxis, _yaxis, symbol='o')
            self.kropff_automatic_bragg_peak_threshold_finder_changed(xaxis=xaxis,
                                                                      yaxis=_yaxis)

    def kropff_automatic_bragg_peak_threshold_finder_changed(self, xaxis=None, yaxis=None):
        o_get = Get(parent=self.parent)
        if o_get.is_automatic_bragg_peak_threshold_finder_activated():
            print("automatic calculation of bragg peak threshold")
        else:
            print("manual selection of bragg peak threshold")

