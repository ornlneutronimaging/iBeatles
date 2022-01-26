import numpy as np
import pyqtgraph as pg

from src.iBeatles.fitting.get import Get
from src.iBeatles.fitting.kropff.kropff_bragg_peak_threshold_calculator import KropffBraggPeakThresholdCalculator
from src.iBeatles import DataType
from src.iBeatles.fitting.kropff.fit_regions import FitRegions
from src.iBeatles.fitting.kropff.display import Display

fit_rgb = (0, 255, 0)


class EventHandler:

    default_threshold_width = 3

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def check_widgets_helper(self):
        pass

    def update_bragg_edge_threshold(self):
        pass

    def update_fitting_plot(self):
        self.parent.ui.kropff_fitting.clear()

        o_get = Get(parent=self.parent, grand_parent=self.grand_parent)
        yaxis, xaxis = o_get.y_axis_and_x_axis_for_given_rows_selected()

        self.parent.ui.kropff_fitting.setLabel("left", 'Cross Section (arbitrary units, -log(counts))')
        self.parent.ui.kropff_fitting.setLabel("bottom", u'\u03BB (\u212B)')

        for _yaxis in yaxis:
            _yaxis = -np.log(_yaxis)
            self.parent.ui.kropff_fitting.plot(xaxis, _yaxis, symbol='o')

        yaxis_fitted = o_get.y_axis_fitted_for_given_rows_selected()
        if yaxis_fitted:
            for _yaxis in yaxis_fitted:
                self.parent.ui.kropff_fitting.plot(xaxis,
                                                   _yaxis,
                                                   pen=fit_rgb)

    def kropff_automatic_bragg_peak_threshold_finder_clicked(self):
        o_kropff = KropffBraggPeakThresholdCalculator(parent=self.parent,
                                                      grand_parent=self.grand_parent)
        o_kropff.save_all_profiles()
        o_kropff.run_automatic_mode()

        o_display = Display(parent=self.parent,
                            grand_parent=self.grand_parent)
        o_display.display_bragg_peak_threshold()
        self.parent.ui.kropff_fit_allregions_pushButton.setEnabled(True)

    def kropff_bragg_edge_threshold_changed(self):
        lr = self.parent.kropff_threshold_current_item
        [left, right] = lr.getRegion()

        o_kropff = Get(parent=self.parent)
        row_selected = str(o_kropff.kropff_row_selected()[0])

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        kropff_table_of_row_selected = kropff_table_dictionary[row_selected]
        kropff_table_of_row_selected['bragg peak threshold']['left'] = left
        kropff_table_of_row_selected['bragg peak threshold']['right'] = right

    def parameters_changed(self):
        a0 = self.parent.ui.kropff_high_lda_a0_init.text()
        b0 = self.parent.ui.kropff_high_lda_b0_init.text()
        high_tof_graph = 'a0' if self.parent.ui.kropff_a0_radioButton.isChecked() else 'b0'

        ahkl = self.parent.ui.kropff_low_lda_ahkl_init.text()
        bhkl = self.parent.ui.kropff_low_lda_bhkl_init.text()
        low_tof_graph = 'ahkl' if self.parent.ui.kropff_ahkl_radioButton.isChecked() else 'bhkl'

        lambda_hkl = self.parent.ui.kropff_bragg_peak_ldahkl_init.text()
        tau = self.parent.ui.kropff_bragg_peak_tau_init.text()
        sigma = self.parent.ui.kropff_bragg_peak_sigma_comboBox.currentText()
        if self.parent.ui.kropff_lda_hkl_radioButton.isChecked():
            bragg_peak_graph = 'lambda_hkl'
        elif self.parent.ui.kropff_tau_radioButton.isChecked():
            bragg_peak_graph = 'tau'
        else:
            bragg_peak_graph = 'sigma'

        self.grand_parent.session_dict[DataType.fitting]['kropff']['high tof']['a0'] = a0
        self.grand_parent.session_dict[DataType.fitting]['kropff']['high tof']['b0'] = b0
        self.grand_parent.session_dict[DataType.fitting]['kropff']['high tof']['graph'] = high_tof_graph

        self.grand_parent.session_dict[DataType.fitting]['kropff']['low tof']['ahkl'] = ahkl
        self.grand_parent.session_dict[DataType.fitting]['kropff']['low tof']['bhkl'] = bhkl
        self.grand_parent.session_dict[DataType.fitting]['kropff']['low tof']['graph'] = low_tof_graph

        self.grand_parent.session_dict[DataType.fitting]['kropff']['bragg peak']['lambda_hkl'] = lambda_hkl
        self.grand_parent.session_dict[DataType.fitting]['kropff']['bragg peak']['tau'] = tau
        self.grand_parent.session_dict[DataType.fitting]['kropff']['bragg peak']['sigma'] = sigma
        self.grand_parent.session_dict[DataType.fitting]['kropff']['bragg peak']['graph'] = bragg_peak_graph

        self.grand_parent.session_dict[DataType.fitting]['kropff']['automatic bragg peak threshold algorithm'] = \
            self.parent.kropff_automatic_threshold_finder_algorithm

        self.grand_parent.session_dict[DataType.fitting]['kropff']['bragg peak threshold width'] = \
            self.parent.ui.kropff_threshold_width_slider.value()

    def fit_regions(self):
        o_fit = FitRegions(parent=self.parent,
                           grand_parent=self.grand_parent)
        o_fit.all_regions()
