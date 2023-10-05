import numpy as np
import copy
from qtpy.QtWidgets import QMenu
from qtpy import QtGui
from qtpy.QtWidgets import QApplication
import logging
from pathlib import PurePath
import json

from ibeatles.fitting.get import Get
from ibeatles.fitting.kropff.kropff_bragg_peak_threshold_calculator import KropffBraggPeakThresholdCalculator
from ibeatles import DataType, interact_me_style, normal_style
from ibeatles.fitting.kropff.fit_regions import FitRegions
from ibeatles.fitting.kropff.display import Display
from ibeatles.fitting.fitting_handler import FittingHandler
from ibeatles.utilities.table_handler import TableHandler
from ibeatles.fitting.kropff.get import Get as KropffGet
from ibeatles.fitting import KropffTabSelected
from ibeatles.utilities.file_handler import select_folder
from ibeatles.utilities.array_utilities import from_nparray_to_list
from ibeatles.utilities.check import is_float, is_nan

from ibeatles.fitting import FittingTabSelected, FittingKeys
from ibeatles.fitting.kropff import UNLOCK_ROW_BACKGROUND
from ibeatles.fitting.kropff import SessionSubKeys as KropffSessionSubKeys
from ibeatles.session import SessionSubKeys
from ibeatles.fitting.kropff import FittingKropffBraggPeakColumns, FittingKropffHighLambdaColumns, \
    FittingKropffLowLambdaColumns, BraggPeakInitParameters
from ibeatles.fitting.kropff.checking_fitting_conditions import CheckingFittingConditions
from ibeatles.utilities.status_message_config import show_status_message, StatusMessageStatus
from ibeatles.fitting.kropff.fitting_parameters_viewer_editor_launcher import FittingParametersViewerEditorLauncher
from ibeatles.fitting.kropff import RightClickTableMenu


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
                table_dictionary[_row][_template_key] = \
                    copy.deepcopy(kropff_table_dictionary_template[_template_key])

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

    def update_fitting_plots(self):
        self.update_bottom_right_plot()

    def update_bottom_right_plot(self):
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

        o_display = Display(parent=self.parent,
                            grand_parent=self.grand_parent)
        o_display.display_bragg_peak_threshold()

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

        # high TOF
        a0 = self.parent.ui.kropff_high_lda_a0_init.text()
        b0 = self.parent.ui.kropff_high_lda_b0_init.text()
        high_tof_graph = 'a0' if self.parent.ui.kropff_a0_radioButton.isChecked() else 'b0'
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.high_tof][
            KropffSessionSubKeys.a0] = a0
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.high_tof][
            KropffSessionSubKeys.b0] = b0
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.high_tof][
            KropffSessionSubKeys.graph] = high_tof_graph

        # low TOF
        ahkl = self.parent.ui.kropff_low_lda_ahkl_init.text()
        bhkl = self.parent.ui.kropff_low_lda_bhkl_init.text()
        low_tof_graph = 'ahkl' if self.parent.ui.kropff_ahkl_radioButton.isChecked() else 'bhkl'
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.low_tof][
            KropffSessionSubKeys.ahkl] = ahkl
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.low_tof][
            KropffSessionSubKeys.bhkl] = bhkl
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.low_tof][
            KropffSessionSubKeys.graph] = low_tof_graph

        # bragg peak
        lambda_hkl_fix_flag = self.parent.ui.lambda_hkl_fix_radioButton.isChecked()
        lambda_hkl_fix_value = self.parent.ui.lambda_hkl_fix_lineEdit.text()
        lambda_hkl_range_from = self.parent.ui.lambda_hkl_from_lineEdit.text()
        lambda_hkl_range_to = self.parent.ui.lambda_hkl_to_lineEdit.text()
        lambda_hkl_range_step = self.parent.ui.lambda_hkl_step_lineEdit.text()

        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.lambda_hkl][BraggPeakInitParameters.fix_value] = lambda_hkl_fix_value
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.lambda_hkl][BraggPeakInitParameters.fix_flag] = lambda_hkl_fix_flag
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.lambda_hkl][BraggPeakInitParameters.range_from] = lambda_hkl_range_from
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.lambda_hkl][BraggPeakInitParameters.range_to] = lambda_hkl_range_to
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.lambda_hkl][BraggPeakInitParameters.range_step] = lambda_hkl_range_step

        tau_fix_flag = self.parent.ui.tau_fix_radioButton.isChecked()
        tau_fix_value = self.parent.ui.tau_fix_lineEdit.text()
        tau_range_from = self.parent.ui.tau_from_lineEdit.text()
        tau_range_to = self.parent.ui.tau_to_lineEdit.text()
        tau_range_step = self.parent.ui.tau_step_lineEdit.text()
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.tau][BraggPeakInitParameters.fix_value] = tau_fix_value
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.tau][BraggPeakInitParameters.fix_flag] = tau_fix_flag
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.tau][BraggPeakInitParameters.range_from] = tau_range_from
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.tau][BraggPeakInitParameters.range_to] = tau_range_to
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.tau][BraggPeakInitParameters.range_step] = tau_range_step

        sigma_fix_flag = self.parent.ui.sigma_fix_radioButton.isChecked()
        sigma_fix_value = self.parent.ui.sigma_fix_lineEdit.text()
        sigma_range_from = self.parent.ui.sigma_from_lineEdit.text()
        sigma_range_to = self.parent.ui.sigma_to_lineEdit.text()
        sigma_range_step = self.parent.ui.sigma_step_lineEdit.text()
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.sigma][BraggPeakInitParameters.fix_value] = sigma_fix_value
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.sigma][BraggPeakInitParameters.fix_flag] = sigma_fix_flag
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.sigma][BraggPeakInitParameters.range_from] = sigma_range_from
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.sigma][BraggPeakInitParameters.range_to] = sigma_range_to
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.sigma][BraggPeakInitParameters.range_step] = sigma_range_step

        # lambda_hkl = self.parent.kropff_lambda_settings['fix']
        # tau = self.parent.ui.kropff_bragg_peak_tau_init.text()
        # sigma = self.parent.ui.kropff_bragg_peak_sigma_comboBox.currentText()
        if self.parent.ui.kropff_lda_hkl_radioButton.isChecked():
            bragg_peak_graph = 'lambda_hkl'
        elif self.parent.ui.kropff_tau_radioButton.isChecked():
            bragg_peak_graph = 'tau'
        else:
            bragg_peak_graph = 'sigma'

        # self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
        #     KropffSessionSubKeys.lambda_hkl] = lambda_hkl
        # self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
        #     KropffSessionSubKeys.tau] = tau
        # self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
        #     KropffSessionSubKeys.sigma] = sigma
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][KropffSessionSubKeys.bragg_peak][
            KropffSessionSubKeys.graph] = bragg_peak_graph

        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][
            KropffSessionSubKeys.kropff_bragg_peak_good_fit_conditions] = \
            self.parent.kropff_bragg_peak_good_fit_conditions

        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][
            KropffSessionSubKeys.kropff_lambda_settings] = \
            self.parent.kropff_lambda_settings

        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][
            KropffSessionSubKeys.bragg_peak_row_rejections_conditions] = \
            self.parent.kropff_bragg_peak_row_rejections_conditions

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

        # lock_all_good_cells = None
        # unlock_all_rows = None
        replace_row = None
        # export_bin = None

        export_bin = menu.addAction("Export bin signal ...")

        # replace_row = menu.addAction("Replace value by median of surrounding pixels")
        # button_state = self.parent.kropff_bragg_table_right_click_menu[RightClickTableMenu.replace_values]['state']
        # replace_row.setEnabled(button_state)

        menu.addSeparator()

        display_fitting_parameters = menu.addAction("Fitting parameters viewer ...")
        # button_state = self.parent.kropff_bragg_table_right_click_menu[RightClickTableMenu.display_fitting_parameters]['state']

        button_state = self.did_we_perform_the_fitting()

        display_fitting_parameters.setEnabled(button_state)
        # unlock_all_rows = menu.addAction("Un-lock/Un-reject all rows")

        # self.parent.kropff_bragg_table_right_click_menu[RightClickTableMenu.replace_values]['ui'] = replace_row
        # self.parent.kropff_bragg_table_right_click_menu[RightClickTableMenu.display_fitting_parameters]['ui'] = \
        #     display_fitting_parameters

        action = menu.exec_(QtGui.QCursor.pos())

        # if action == unlock_all_rows:
        #     self.unlock_all_bragg_peak_rows()
        # if action == replace_row:
        #     self.replace_bragg_peak_row_values()
        if action == display_fitting_parameters:
            self.display_fitting_parameters()
        elif action == export_bin:
            self.export_bin()

    def did_we_perform_the_fitting(self) -> bool:
        """
        do we have the fitting table filled with values
         if at least one lambda_hkl value is found, return True, otherwise return False

        Returns
            bool
        """
        table = self.grand_parent.kropff_table_dictionary
        for _row in table.keys():
            lambda_hkl_value = table[_row][KropffSessionSubKeys.lambda_hkl]['val']
            if is_nan(lambda_hkl_value):
                continue

            if is_float(lambda_hkl_value):
                return True
        return False

    def export_bin(self):
        logging.info(f"Exporting bin:")
        o_table = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)
        row_selected = str(o_table.get_row_selected())

        # create base output file name using bin# row# col#
        table_dictionary = self.grand_parent.kropff_table_dictionary
        metadata_for_this_row = table_dictionary[row_selected]

        logging.info(f" - row_selected: {row_selected}")
        # logging.info(f" - metadata: {metadata_for_this_row}")

        bin_number = row_selected
        row_index = metadata_for_this_row[FittingKeys.row_index]
        column_index = metadata_for_this_row[FittingKeys.column_index]

        logging.info(f" - bin_number: {bin_number}")
        logging.info(f" - bin row: {row_index}")
        logging.info(f" - bin column: {column_index}")

        # {'high_tof': {'xaxis': None, 'yaxis': None},
        #  'low_tof': {'xaxis': None, 'yaxis': None},
        #  'bragg_peak': {'xaxis': None, 'yaxis': None},
        fitted_dict = metadata_for_this_row[KropffSessionSubKeys.fitted]

        parent_folder = PurePath(self.grand_parent.default_path[DataType.normalized]).parent
        base_parent_folder = PurePath(self.grand_parent.default_path[DataType.normalized]).name
        output_folder = select_folder(start_folder=str(parent_folder))

        full_output_filename = PurePath(output_folder) / f"{str(base_parent_folder)}_bin#{bin_number}.json"
        logging.info(f" - output file name: {full_output_filename}")

        # cleanup data
        cleaned_dict = {}

        cleaned_dict[FittingKeys.x_axis] = from_nparray_to_list(metadata_for_this_row[FittingKeys.x_axis])
        cleaned_dict[FittingKeys.y_axis] = from_nparray_to_list(metadata_for_this_row[FittingKeys.y_axis])

        # fitted
        cleaned_dict[KropffSessionSubKeys.fitted] = {}

        # high tof
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.high_tof] = {}
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.high_tof][FittingKeys.x_axis] = \
            from_nparray_to_list(fitted_dict
                                              [KropffSessionSubKeys.high_tof][FittingKeys.x_axis])
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.high_tof][FittingKeys.y_axis] = \
            from_nparray_to_list(fitted_dict
                                              [KropffSessionSubKeys.high_tof][FittingKeys.y_axis])

        # low tof
        cleaned_dict[KropffSessionSubKeys.fitted][KropffTabSelected.low_tof] = {}
        cleaned_dict[KropffSessionSubKeys.fitted][KropffTabSelected.low_tof][FittingKeys.x_axis] = \
            from_nparray_to_list(fitted_dict
                                              [KropffTabSelected.low_tof][FittingKeys.x_axis])
        cleaned_dict[KropffSessionSubKeys.fitted][KropffTabSelected.low_tof][FittingKeys.y_axis] = \
            from_nparray_to_list(fitted_dict
                                              [KropffTabSelected.low_tof][FittingKeys.y_axis])

        # bragg peak
        cleaned_dict[KropffSessionSubKeys.fitted][KropffTabSelected.bragg_peak] = {}
        cleaned_dict[KropffSessionSubKeys.fitted][KropffTabSelected.bragg_peak][FittingKeys.x_axis] = \
            from_nparray_to_list(fitted_dict
                                              [KropffTabSelected.bragg_peak][FittingKeys.x_axis])
        cleaned_dict[KropffSessionSubKeys.fitted][KropffTabSelected.bragg_peak][FittingKeys.y_axis] = \
            from_nparray_to_list(fitted_dict
                                              [KropffTabSelected.bragg_peak][FittingKeys.y_axis])

        # fitting parameters
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.a0] = \
            metadata_for_this_row[KropffSessionSubKeys.a0]
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.b0] = \
            metadata_for_this_row[KropffSessionSubKeys.b0]
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.ahkl] = \
            metadata_for_this_row[KropffSessionSubKeys.ahkl]
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.bhkl] = \
            metadata_for_this_row[KropffSessionSubKeys.bhkl]
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.lambda_hkl] = \
            metadata_for_this_row[KropffSessionSubKeys.lambda_hkl]
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.tau] = \
            metadata_for_this_row[KropffSessionSubKeys.tau]
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.sigma] =\
            metadata_for_this_row[KropffSessionSubKeys.sigma]
        cleaned_dict[KropffSessionSubKeys.fitted][KropffSessionSubKeys.bhkl] =\
            metadata_for_this_row[KropffSessionSubKeys.bhkl]
        cleaned_dict[KropffSessionSubKeys.fitted][SessionSubKeys.bin_coordinates] = {'x0': int(metadata_for_this_row[SessionSubKeys.bin_coordinates]['x0']),
                                                                                     'y0': int(metadata_for_this_row[SessionSubKeys.bin_coordinates]['y0']),
                                                                                     'x1': int(metadata_for_this_row[SessionSubKeys.bin_coordinates]['x1']),
                                                                                     'y1': int(metadata_for_this_row[SessionSubKeys.bin_coordinates]['y1'])}
        cleaned_dict[KropffSessionSubKeys.fitted][SessionSubKeys.bragg_peak_threshold] =\
            metadata_for_this_row[SessionSubKeys.bragg_peak_threshold]

        with open(full_output_filename, 'w') as json_file:
            json.dump(cleaned_dict, json_file)

    def replace_bragg_peak_row_values(self):
        """replace by median of surrounding pixels"""
        pass

    def display_fitting_parameters(self):
        FittingParametersViewerEditorLauncher(parent=self.parent,
                                              grand_parent=self.grand_parent)

    def unlock_all_bragg_peak_rows(self):
        background_color = UNLOCK_ROW_BACKGROUND

        o_table = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)
        nbr_row = o_table.row_count()
        for _row in np.arange(nbr_row):
            o_table.set_background_color_of_row(row=_row,
                                                qcolor=background_color)

        o_table_high = TableHandler(table_ui=self.parent.ui.high_lda_tableWidget)
        for _row in np.arange(nbr_row):
            o_table_high.set_background_color_of_row(row=_row,
                                                     qcolor=background_color)

        o_table_low = TableHandler(table_ui=self.parent.ui.low_lda_tableWidget)
        for _row in np.arange(nbr_row):
            o_table_low.set_background_color_of_row(row=_row,
                                                    qcolor=background_color)

    def unlock_all_rows_in_table_dictionary(self):
        table_dictionary = self.grand_parent.kropff_table_dictionary
        for _key in table_dictionary.keys():
            table_dictionary[_key]['lock'] = False
        self.grand_parent.kropff_table_dictionary = table_dictionary

    # def bragg_peak_auto_lock_clicked(self):
    #     """if the condition found in the Bragg Edge table are met, the row of all the table will be locked"""
    #
    #     o_table_bragg_peak = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)
    #     o_table_high_tof = TableHandler(table_ui=self.parent.ui.high_lda_tableWidget)
    #     o_table_low_tof = TableHandler(table_ui=self.parent.ui.low_lda_tableWidget)
    #     nbr_row = o_table_bragg_peak.row_count()
    #
    #     table_dictionary = self.grand_parent.kropff_table_dictionary
    #     if self.parent.ui.checkBox.isChecked():
    #
    #         for _row in np.arange(nbr_row):
    #
    #             if self._lets_reject_this_row(row=_row):
    #                 background_color = REJECTED_ROW_BACKGROUND
    #                 table_dictionary[str(_row)]['rejected'] = True
    #
    #             elif self._lets_lock_this_row(row=_row):
    #                 table_dictionary[str(_row)]['rejected'] = False
    #                 background_color = LOCK_ROW_BACKGROUND
    #                 table_dictionary[str(_row)]['lock'] = True
    #
    #             else:
    #                 table_dictionary[str(_row)]['rejected'] = False
    #                 background_color = UNLOCK_ROW_BACKGROUND
    #                 table_dictionary[str(_row)]['lock'] = False
    #
    #             o_table_bragg_peak.set_background_color_of_row(row=_row,
    #                                                            qcolor=background_color)
    #             o_table_high_tof.set_background_color_of_row(row=_row,
    #                                                          qcolor=background_color)
    #             o_table_low_tof.set_background_color_of_row(row=_row,
    #                                                         qcolor=background_color)
    #
    #     else:
    #         for _row in np.arange(nbr_row):
    #
    #             # if table_dictionary[str(_row)]['rejected']:
    #             #     background_color = REJECTED_ROW_BACKGROUND
    #             # else:
    #             background_color = UNLOCK_ROW_BACKGROUND
    #
    #             o_table_bragg_peak.set_background_color_of_row(row=_row,
    #                                                            qcolor=background_color)
    #             o_table_high_tof.set_background_color_of_row(row=_row,
    #                                                          qcolor=background_color)
    #             o_table_low_tof.set_background_color_of_row(row=_row,
    #                                                         qcolor=background_color)
    #
    #         self.unlock_all_rows_in_table_dictionary()

    def _lets_reject_this_row(self, row=0):
        o_table = TableHandler(table_ui=self.parent.ui.high_lda_tableWidget)

        # high lambda
        # if a0 or b0 are nan -> yes, reject this row
        a0_value = o_table.get_item_float_from_cell(row=row, column=FittingKropffHighLambdaColumns.a0)
        if not np.isfinite(a0_value):
            return True

        b0_value = o_table.get_item_float_from_cell(row=row, column=FittingKropffHighLambdaColumns.b0)
        if not np.isfinite(b0_value):
            return True

        # low lambda
        # if ahkl, bhkl are nan -> yes, reject this row
        ahkl_value = o_table.get_item_float_from_cell(row=row, column=FittingKropffLowLambdaColumns.ahkl)
        if not np.isfinite(ahkl_value):
            return True

        bhkl_value = o_table.get_item_float_from_cell(row=row, column=FittingKropffLowLambdaColumns.bhkl)
        if not np.isfinite(bhkl_value):
            return True

        # bragg peak
        # if l_hkl is nan -> yes, reject this row
        l_hkl_value = o_table.get_item_float_from_cell(row=row, column=FittingKropffBraggPeakColumns.l_hkl_value)
        if not np.isfinite(l_hkl_value):
            return True

        # if l_hkl is outside of range defined in settings -> reject this row
        less_than_state = self.parent.kropff_bragg_peak_row_rejections_conditions['l_hkl']['less_than']['state']
        if less_than_state:
            less_than_value = self.parent.kropff_bragg_peak_row_rejections_conditions['l_hkl']['less_than']['value']
            if l_hkl_value < less_than_value:
                return True

        more_than_state = self.parent.kropff_bragg_peak_row_rejections_conditions['l_hkl']['more_than']['state']
        if more_than_state:
            more_than_value = self.parent.kropff_bragg_peak_row_rejections_conditions['l_hkl']['more_than']['value']
            if l_hkl_value > more_than_value:
                return True

        return False

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
        QApplication.processEvents()

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

    # top left view mouse events
    def mouse_clicked_in_top_left_image_view(self, mouse_click_event):
        image_pos = self.parent.image_view_item.mapFromScene(mouse_click_event.scenePos())

        # if user click within a BIN, select that bin in all the tables (this will automatically highlight it
        [_, top_left_x, top_left_y, _, _,  binning_size] = self.grand_parent.session_dict[DataType.bin][
            SessionSubKeys.roi]

        # top_left_corner_coordinates = self.grand_parent.binning_line_view['pos'][0]
        # top_left_x = top_left_corner_coordinates[0]
        # top_left_y = top_left_corner_coordinates[1]
        #
        # binning_size = self.grand_parent.binning_roi[-1]
        x = int(image_pos.x())
        y = int(image_pos.y())

        if x < top_left_x:
            return

        if y < top_left_y:
            return

        o_get = KropffGet(parent=self.parent)
        tab_selected = o_get.kropff_tab_selected()

        if not tab_selected in [KropffTabSelected.low_tof,
                                KropffTabSelected.high_tof,
                                KropffTabSelected.bragg_peak]:
            # no need to update table as we are showing a tab without tables
            return

        table_ui = o_get.kropff_table_ui_selected()
        nbr_bin_y_direction = self.grand_parent.fitting_selection['nbr_row']
        nbr_bin_x_direction = self.grand_parent.fitting_selection["nbr_column"]

        if x > (top_left_x + (nbr_bin_x_direction + 1) * binning_size):
            return

        if y > (top_left_y + (nbr_bin_y_direction) * binning_size):
            return

        bin_x_index = int((x - top_left_x) / binning_size) + 1
        bin_y_index = int((y - top_left_y) / binning_size) + 1

        row_to_select = int(bin_y_index + (bin_x_index - 1) * nbr_bin_y_direction - 1)
        o_table = TableHandler(table_ui=table_ui)
        o_table.select_row(row_to_select)

    def mouse_moved_in_top_left_image_view(self, evt):
        pos = evt[0]

        width = self.grand_parent.data_metadata[DataType.normalized]['size']['width']
        height = self.grand_parent.data_metadata[DataType.normalized]['size']['height']

        if self.parent.image_view_item.sceneBoundingRect().contains(pos):
            image_pos = self.parent.image_view_item.mapFromScene(pos)
            x = int(image_pos.x())
            y = int(image_pos.y())
            binning_size = self.grand_parent.session_dict[DataType.bin][SessionSubKeys.roi][-1]
            top_left_corner_coordinates = self.grand_parent.binning_line_view['pos'][0]
            top_left_x = top_left_corner_coordinates[0]
            top_left_y = top_left_corner_coordinates[1]
            bin_x_index = int((x - top_left_x) / binning_size) + 1
            bin_y_index = int((y - top_left_y) / binning_size) + 1
            nbr_bin_y_direction = self.grand_parent.fitting_selection['nbr_row']
            row_to_select = int(bin_y_index + (bin_x_index - 1) * nbr_bin_y_direction - 1) + 1

            if (x >= 0) and (x < width) and (y >= 0) and (y < height):
                self.parent.image_view_vline.setPos(x)
                self.parent.image_view_hline.setPos(y)

                self.parent.ui.kropff_pos_x_value.setText(f"{x}")
                self.parent.ui.kropff_pos_y_value.setText(f"{y}")

                # only if we are inside the bin selection
                bin_list = self.grand_parent.session_dict[DataType.bin][SessionSubKeys.roi]
                left = bin_list[1]
                top = bin_list[2]
                roi_width = bin_list[3]
                roi_height = bin_list[4]
                bin_size = bin_list[5]

                if (x >= left) and (x <= (left + roi_width - bin_size)) and \
                        (y >= top) and (y <= (top + roi_height - bin_size)):
                    # inside the ROI region
                    self.parent.ui.kropff_bin_x_value.setText(f"{bin_x_index}")
                    self.parent.ui.kropff_bin_y_value.setText(f"{bin_y_index}")
                    self.parent.ui.kropff_bin_nbr_value.setText(f"{row_to_select}")
                else:
                    # outside the ROI region
                    self.parent.ui.kropff_bin_x_value.setText("N/A")
                    self.parent.ui.kropff_bin_y_value.setText("N/A")
                    self.parent.ui.kropff_bin_nbr_value.setText("N/A")

            else:
                self.parent.ui.kropff_pos_x_value.setText("N/A")
                self.parent.ui.kropff_pos_y_value.setText("N/A")
                self.parent.ui.kropff_bin_x_value.setText(f"N/A")
                self.parent.ui.kropff_bin_y_value.setText(f"N/A")
                self.parent.ui.kropff_bin_nbr_value.setText(f"N/A")

        else:
            self.parent.ui.kropff_pos_x_value.setText("N/A")
            self.parent.ui.kropff_pos_y_value.setText("N/A")
            self.parent.ui.kropff_bin_x_value.setText("N/A")
            self.parent.ui.kropff_bin_y_value.setText("N/A")
            self.parent.ui.kropff_bin_nbr_value.setText("N/A")

    def change_initial_guess_lambda_hkl_widgets(self):
        state_fix = self.parent.ui.lambda_hkl_fix_radioButton.isChecked()

        self.parent.ui.lambda_hkl_fix_lineEdit.setEnabled(state_fix)
        self.parent.ui.lambda_hkl_from_lineEdit.setEnabled(not state_fix)
        self.parent.ui.to_label.setEnabled(not state_fix)
        self.parent.ui.lambda_hkl_to_lineEdit.setEnabled(not state_fix)
        self.parent.ui.step_label.setEnabled(not state_fix)
        self.parent.ui.lambda_hkl_step_lineEdit.setEnabled(not state_fix)

    def change_initial_guess_tau_widgets(self):
        state_fix = self.parent.ui.tau_fix_radioButton.isChecked()

        self.parent.ui.tau_fix_lineEdit.setEnabled(state_fix)
        self.parent.ui.tau_from_lineEdit.setEnabled(not state_fix)
        self.parent.ui.to_label_1.setEnabled(not state_fix)
        self.parent.ui.tau_to_lineEdit.setEnabled(not state_fix)
        self.parent.ui.step_label_1.setEnabled(not state_fix)
        self.parent.ui.tau_step_lineEdit.setEnabled(not state_fix)

    def change_initial_guess_sigma_widgets(self):
        state_fix = self.parent.ui.sigma_fix_radioButton.isChecked()

        self.parent.ui.sigma_fix_lineEdit.setEnabled(state_fix)
        self.parent.ui.sigma_from_lineEdit.setEnabled(not state_fix)
        self.parent.ui.to_label_2.setEnabled(not state_fix)
        self.parent.ui.sigma_to_lineEdit.setEnabled(not state_fix)
        self.parent.ui.step_label_2.setEnabled(not state_fix)
        self.parent.ui.sigma_step_lineEdit.setEnabled(not state_fix)
