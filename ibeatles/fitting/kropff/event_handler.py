import numpy as np
import copy
from qtpy.QtWidgets import QMenu
from qtpy import QtGui

from ibeatles.fitting.get import Get
from ibeatles.fitting.kropff.kropff_bragg_peak_threshold_calculator import KropffBraggPeakThresholdCalculator
from ibeatles import DataType, interact_me_style, normal_style
from ibeatles.fitting.kropff.fit_regions import FitRegions
from ibeatles.fitting.kropff.display import Display
from ibeatles.fitting.fitting_handler import FittingHandler
from ibeatles.utilities.table_handler import TableHandler

from ibeatles.fitting.kropff import LOCK_ROW_BACKGROUND, UNLOCK_ROW_BACKGROUND
from ibeatles.fitting.kropff import FittingKropffBraggPeakColumns

fit_rgb = (255, 0, 0)


class EventHandler:

    default_threshold_width = 3

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def reset_fitting_parameters(self):
        table_dictionary = self.grand_parent.kropff_table_dictionary

        kropff_table_dictionary_tempate = FittingHandler.kropff_table_dictionary_template
        for _row in table_dictionary.keys():
            for _template_key in kropff_table_dictionary_tempate.keys():
                table_dictionary[_row][_template_key] = copy.deepcopy(kropff_table_dictionary_tempate[_template_key])

    def _is_first_row_has_threshold_defined(self):
        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        kropff_table_of_second_row = kropff_table_dictionary['1']

        if kropff_table_of_second_row['bragg peak threshold']['left'] is None:
            return False

        if kropff_table_of_second_row['yaxis'] is None:
            self.record_all_xaxis_and_yaxis()
            if kropff_table_of_second_row['yaxis'] is None:
                return False

        return True

    def _we_are_ready_to_fit_all_regions(self):
        return self._is_first_row_has_threshold_defined()

    def check_widgets_helper(self):

        if self._we_are_ready_to_fit_all_regions():
            self.parent.ui.kropff_fit_allregions_pushButton.setEnabled(True)
            self.parent.ui.kropff_fit_allregions_pushButton.setStyleSheet(interact_me_style)
            self.parent.ui.automatic_bragg_peak_threshold_finder_pushButton.setStyleSheet(normal_style)
        else:
            self.parent.ui.kropff_fit_allregions_pushButton.setEnabled(False)
            self.parent.ui.kropff_fit_allregions_pushButton.setStyleSheet(normal_style)
            self.parent.ui.automatic_bragg_peak_threshold_finder_pushButton.setStyleSheet(interact_me_style)

    def record_all_xaxis_and_yaxis(self):
        table_dictionary = self.grand_parent.kropff_table_dictionary
        nbr_row = len(table_dictionary.keys())
        data_2d = self.grand_parent.data_metadata['normalized']['data']

        # index of selection in bragg edge plot
        [left_index, right_index] = self.grand_parent.fitting_bragg_edge_linear_selection
        full_x_axis = self.parent.bragg_edge_data['x_axis']
        xaxis = np.array(full_x_axis[left_index: right_index], dtype=float)

        for _row in np.arange(nbr_row):

            _bin_entry = table_dictionary[str(_row)]

            _bin_x0 = _bin_entry['bin_coordinates']['x0']
            _bin_x1 = _bin_entry['bin_coordinates']['x1']
            _bin_y0 = _bin_entry['bin_coordinates']['y0']
            _bin_y1 = _bin_entry['bin_coordinates']['y1']

            yaxis = data_2d[left_index: right_index,
                    _bin_x0: _bin_x1,
                    _bin_y0: _bin_y1,
                    ]  # noqa: E124
            yaxis = np.nanmean(yaxis, axis=1)
            yaxis = np.array(np.nanmean(yaxis, axis=1), dtype=float)
            _bin_entry['yaxis'] = yaxis
            _bin_entry['xaxis'] = xaxis

    def update_fitting_plot(self):
        self.parent.ui.kropff_fitting.clear()

        o_get = Get(parent=self.parent, grand_parent=self.grand_parent)
        yaxis, xaxis = o_get.y_axis_and_x_axis_for_given_rows_selected()

        self.parent.ui.kropff_fitting.setLabel("left", 'Cross Section (arbitrary units, -log(counts))')
        self.parent.ui.kropff_fitting.setLabel("bottom", u'\u03BB (\u212B)')

        for _yaxis in yaxis:
            _yaxis = -np.log(_yaxis)
            self.parent.ui.kropff_fitting.plot(xaxis, _yaxis, symbol='o', pen=None)

        xaxis_fitted, yaxis_fitted = o_get.y_axis_fitted_for_given_rows_selected()

        if yaxis_fitted:
            for _yaxis in yaxis_fitted:
                self.parent.ui.kropff_fitting.plot(xaxis_fitted,
                                                   _yaxis,
                                                   pen=(fit_rgb[0],
                                                        fit_rgb[1],
                                                        fit_rgb[2]))

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

    def bragg_peak_rigth_click(self):
        menu = QMenu(self.parent)

        lock_all_good_cells = menu.addAction("Lock all rows with good fits")
        unlock_all_rows = menu.addAction("Unlock all rows")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == lock_all_good_cells:
            self.bragg_peak_auto_lock_clicked()
        elif action == unlock_all_rows:
            self.unlock_all_bragg_peak_rows()

    def unlock_all_bragg_peak_rows(self):
        o_table = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)
        nbr_row = o_table.row_count()
        background_color = UNLOCK_ROW_BACKGROUND
        for _row in np.arange(nbr_row):
            o_table.set_background_color_of_row(row=_row,
                                                qcolor=background_color)

    def bragg_peak_auto_lock_clicked(self):
        o_table = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)
        nbr_row = o_table.row_count()

        for _row in np.arange(nbr_row):
            if self._we_can_not_lock_this_row(row=_row):
                background_color = UNLOCK_ROW_BACKGROUND
            else:
                background_color = LOCK_ROW_BACKGROUND
            o_table.set_background_color_of_row(row=_row,
                                                qcolor=background_color)

    def _we_can_not_lock_this_row(self, row=0):
        fit_conditions = self.parent.kropff_bragg_peak_good_fit_conditions
        o_table = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)

        # l_hkl_error
        if fit_conditions['l_hkl_error']['state']:
            max_l_hkl_error_value = fit_conditions['l_hkl_error']['value']
            table_value = o_table.get_item_float_from_cell(row=row, column=FittingKropffBraggPeakColumns.l_hkl_error)
            if table_value > max_l_hkl_error_value:
                return False

        # t_error
        if fit_conditions['t_error']['state']:
            max_t_error_value = fit_conditions['t_error']['value']
            table_value = o_table.get_item_float_from_cell(row=row, column=FittingKropffBraggPeakColumns.tau_error)
            if table_value > max_t_error_value:
                return False

        # sigma_error
        if fit_conditions['sigma_error']['state']:
            max_sigma_error_value = fit_conditions['sigma_error']['value']
            table_value = o_table.get_item_float_from_cell(row=row, column=FittingKropffBraggPeakColumns.sigma_error)
            if table_value > max_sigma_error_value:
                return False

        return True
