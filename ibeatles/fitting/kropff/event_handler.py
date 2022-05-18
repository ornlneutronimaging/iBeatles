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

from ibeatles.fitting.kropff import LOCK_ROW_BACKGROUND, UNLOCK_ROW_BACKGROUND, REJECTED_ROW_BACKGROUND
from ibeatles.fitting.kropff import FittingKropffBraggPeakColumns
from ibeatles.fitting.kropff.checking_fitting_conditions import CheckingFittingConditions
from ibeatles.utilities.status_message_config import show_status_message, StatusMessageStatus

fit_rgb = (255, 0, 0)


class EventHandler:
    default_threshold_width = 3

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def reset_fitting_parameters(self):
        table_dictionary = self.grand_parent.kropff_table_dictionary

        kropff_table_dictionary_template = FittingHandler.kropff_table_dictionary_template
        for _row in table_dictionary.keys():
            for _template_key in kropff_table_dictionary_template.keys():
                table_dictionary[_row][_template_key] = copy.deepcopy(kropff_table_dictionary_template[_template_key])

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

        lambda_hkl = self.parent.kropff_lambda_settings['fix']
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

    def fit_bragg_peak(self):
        o_fit = FitRegions(parent=self.parent,
                           grand_parent=self.grand_parent)
        o_fit.bragg_peak()

    def bragg_peak_right_click(self):
        menu = QMenu(self.parent)

        lock_all_good_cells = None
        unlock_all_rows = None
        
        # lock_all_good_cells = menu.addAction("Lock all rows with good fits")
        unlock_all_rows = menu.addAction("Un-lock/Un-reject all rows")

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

    def unlock_all_rows_in_table_dictionary(self):
        table_dictionary = self.grand_parent.kropff_table_dictionary
        for _key in table_dictionary.keys():
            table_dictionary[_key]['lock'] = False
        self.grand_parent.kropff_table_dictionary = table_dictionary

    def bragg_peak_auto_lock_clicked(self):
        """if the condition found in the Bragg Edge table are met, the row of all the table will be locked"""

        o_table_bragg_peak = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)
        o_table_high_tof = TableHandler(table_ui=self.parent.ui.high_lda_tableWidget)
        o_table_low_tof = TableHandler(table_ui=self.parent.ui.low_lda_tableWidget)
        nbr_row = o_table_bragg_peak.row_count()

        table_dictionary = self.grand_parent.kropff_table_dictionary
        if self.parent.ui.checkBox.isChecked():

            for _row in np.arange(nbr_row):

                if table_dictionary[str(_row)]['rejected']:
                    background_color = REJECTED_ROW_BACKGROUND

                elif self._lets_lock_this_row(row=_row):
                    background_color = LOCK_ROW_BACKGROUND
                    table_dictionary[str(_row)]['lock'] = True
                else:
                    background_color = UNLOCK_ROW_BACKGROUND
                    table_dictionary[str(_row)]['lock'] = False
                o_table_bragg_peak.set_background_color_of_row(row=_row,
                                                               qcolor=background_color)
                o_table_high_tof.set_background_color_of_row(row=_row,
                                                             qcolor=background_color)
                o_table_low_tof.set_background_color_of_row(row=_row,
                                                            qcolor=background_color)

        else:
            for _row in np.arange(nbr_row):

                if table_dictionary[str(_row)]['rejected']:
                    background_color = REJECTED_ROW_BACKGROUND
                else:
                    background_color = UNLOCK_ROW_BACKGROUND

                o_table_bragg_peak.set_background_color_of_row(row=_row,
                                                               qcolor=background_color)
                o_table_high_tof.set_background_color_of_row(row=_row,
                                                             qcolor=background_color)
                o_table_low_tof.set_background_color_of_row(row=_row,
                                                            qcolor=background_color)

            self.unlock_all_rows_in_table_dictionary()

    def _lets_lock_this_row(self, row=0):
        fit_conditions = self.parent.kropff_bragg_peak_good_fit_conditions
        o_table = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)

        o_checking = CheckingFittingConditions(fit_conditions=fit_conditions)
        l_hkl_error = o_table.get_item_float_from_cell(row=row, column=FittingKropffBraggPeakColumns.l_hkl_error)
        t_error = o_table.get_item_float_from_cell(row=row, column=FittingKropffBraggPeakColumns.tau_error)
        sigma_error = o_table.get_item_float_from_cell(row=row, column=FittingKropffBraggPeakColumns.sigma_error)

        return o_checking.is_fitting_ok(l_hkl_error=l_hkl_error,
                                        t_error=t_error,
                                        sigma_error=sigma_error)

    def check_how_many_fitting_are_locked(self):
        table_dictionary = self.grand_parent.kropff_table_dictionary

        total_number_of_fitting = len(table_dictionary.keys())
        total_number_of_good_fitting = 0
        for _key in table_dictionary.keys():
            lock_state = table_dictionary[_key]['lock']
            if lock_state:
                total_number_of_good_fitting += 1

        percentage = 100 * (total_number_of_good_fitting / total_number_of_fitting)
        message = f"Percentage of Bragg peak fitted showing uncertainties within the constraint ranges defined:" \
                  f" {percentage:.2f}%"

        show_status_message(parent=self.parent,
                            message=message,
                            status=StatusMessageStatus.ready)

    def update_summary_table(self):
        table_dictionary = self.grand_parent.kropff_table_dictionary

        list_hkl = []
        list_hkl_error = []

        number_of_fits_locked = 0
        for _key in table_dictionary.keys():
            list_hkl.append(table_dictionary[_key]['lambda_hkl']['val'])
            list_hkl_error.append(table_dictionary[_key]['lambda_hkl']['err'])
            if table_dictionary[_key]['lock']:
                number_of_fits_locked += 1

        # import pprint
        # pprint.pprint(f"list_hkl: {list_hkl}")
        # pprint.pprint(f"list_hkl_error: {list_hkl_error}")

        # turning None into NaN
        list_hkl_without_none = [_value for _value in list_hkl if _value is not None]
        list_hkl_error_without_none = [_value for _value in list_hkl_error if _value is not None]

        number_of_fittings = len(list_hkl_without_none)
        number_of_fittings_with_error = len(list_hkl_error_without_none)
        total_number_of_bins = len(list_hkl)

        hkl_value_mean = np.mean(list_hkl_without_none)
        hkl_value_median = np.median(list_hkl_without_none)
        hkl_value_std = np.std(list_hkl_without_none)
        hkl_value_percentage_with_fit = 100 * (number_of_fittings / total_number_of_bins)

        hkl_error_value_mean = np.mean(list_hkl_error_without_none)
        hkl_error_value_median = np.median(list_hkl_error_without_none)
        hkl_error_value_std = np.std(list_hkl_error_without_none)
        hkl_error_value_percentage_with_fit = 100 * (number_of_fittings_with_error / total_number_of_bins)

        percentage_of_fits_locked = 100 * (number_of_fits_locked / total_number_of_bins)

        o_table = TableHandler(table_ui=self.parent.ui.kropff_summary_tableWidget)
        o_table.insert_item(row=0, column=1, value=hkl_value_mean, format_str="{:0.4f}", editable=False)
        o_table.insert_item(row=1, column=1, value=hkl_value_median, format_str="{:0.4f}", editable=False)
        o_table.insert_item(row=2, column=1, value=hkl_value_std, format_str="{:0.4f}", editable=False)
        o_table.insert_item(row=3, column=1, value=hkl_value_percentage_with_fit, format_str="{:0.2f}", editable=False)
        o_table.insert_item(row=4, column=1, value=percentage_of_fits_locked, format_str="{:0.2f}", editable=False)

        o_table.insert_item(row=0, column=2, value=hkl_error_value_mean, format_str="{:0.4f}", editable=False)
        o_table.insert_item(row=1, column=2, value=hkl_error_value_median, format_str="{:0.4f}", editable=False)
        o_table.insert_item(row=2, column=2, value=hkl_error_value_std, format_str="{:0.4f}", editable=False)
        o_table.insert_item(row=3, column=2, value=hkl_error_value_percentage_with_fit, format_str="{:0.2f}",
                            editable=False)
