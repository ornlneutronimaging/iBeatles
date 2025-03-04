import numpy as np

from src.ibeatles.fitting.kropff import FittingRegions
import ibeatles.utilities.error as fitting_error
from src.ibeatles.fitting.kropff import SessionSubKeys
from src.ibeatles.utilities.table_handler import TableHandler
from src.ibeatles.fitting import KropffTabSelected
from src.ibeatles import DataType
from src.ibeatles.fitting import FittingKeys


class Get:
    image_size = {"height": None, "width": None}

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def a0(self):
        a0 = self.parent.ui.kropff_high_lda_a0_init.text()
        try:
            a0 = float(a0)
        except ValueError:
            raise fitting_error.HighLambdaFittingError(
                fitting_region=FittingRegions.high_lambda,
                message="Wrong a\u2080 format!",
            )
        return a0

    def b0(self):
        b0 = self.parent.ui.kropff_high_lda_b0_init.text()
        try:
            b0 = float(b0)
        except ValueError:
            raise fitting_error.HighLambdaFittingError(
                fitting_region=FittingRegions.high_lambda,
                message="Wrong b\u2080 format!",
            )
        return b0

    def ahkl(self):
        ahkl = self.parent.ui.kropff_low_lda_ahkl_init.text()
        try:
            ahkl = float(ahkl)
        except ValueError:
            raise fitting_error.LowLambdaFittingError(
                fitting_region=FittingRegions.low_lambda,
                message="Wrong a\u2095\u2096\u2097 format!",
            )
        return ahkl

    def bhkl(self):
        bhkl = self.parent.ui.kropff_low_lda_bhkl_init.text()
        try:
            bhkl = float(bhkl)
        except ValueError:
            raise fitting_error.LowLambdaFittingError(
                fitting_region=FittingRegions.low_lambda,
                message="Wrong b\u2095\u2096\u2097 format!",
            )
        return bhkl

    def lambda_hkl(self):
        lambda_hkl = self.parent.kropff_lambda_settings["fix"]
        try:
            lambda_hkl = float(lambda_hkl)
        except ValueError:
            raise fitting_error.BraggPeakFittingError(
                fitting_region=FittingRegions.bragg_peak,
                message="Wrong \u03bb\u2095\u2096\u2097 format!",
            )
        return lambda_hkl

    def tau(self):
        tau = self.parent.ui.kropff_bragg_peak_tau_init.text()
        try:
            tau = float(tau)
        except ValueError:
            raise fitting_error.BraggPeakFittingError(
                fitting_region=FittingRegions.bragg_peak, message="Wrong \u03c4 format!"
            )
        return tau

    def sigma(self):
        sigma = self.parent.ui.kropff_bragg_peak_sigma_comboBox.currentText()
        try:
            sigma = float(sigma)
        except ValueError:
            raise fitting_error.BraggPeakFittingError(
                fitting_region=FittingRegions.bragg_peak, message="Wrong sigma format!"
            )
        return sigma

    def variable_selected(self):
        """get the variable selected in the Check/Set Variables table"""
        if self.parent.ui.lambda_hkl_button.isChecked():
            return SessionSubKeys.lambda_hkl
        elif self.parent.ui.sigma_button.isChecked():
            return SessionSubKeys.sigma
        elif self.parent.ui.tau_button.isChecked():
            return SessionSubKeys.tau
        else:
            raise NotImplementedError("variable requested not supported!")

    def list_lambda_hkl_initial_guess(self):
        return self._list_parameter_initial_guess(
            parameter=SessionSubKeys.lambda_hkl,
            error_message="Wrong \u03bb\u2095\u2096\u2097 format!",
        )

    def list_sigma_initial_guess(self):
        return self._list_parameter_initial_guess(
            parameter=SessionSubKeys.sigma, error_message="Wrong sigma format!"
        )

    def list_tau_initial_guess(self):
        return self._list_parameter_initial_guess(
            parameter=SessionSubKeys.tau, error_message="Wrong tau format!"
        )

    def _list_parameter_initial_guess(
        self,
        parameter=SessionSubKeys.lambda_hkl,
        error_message="Wrong \u03bb\u2095\u2096\u2097 format!",
    ):
        list_ui = {
            "fix_value": {
                SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_fix_lineEdit,
                SessionSubKeys.sigma: self.parent.ui.sigma_fix_lineEdit,
                SessionSubKeys.tau: self.parent.ui.tau_fix_lineEdit,
            },
            "fix_radio": {
                SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_fix_radioButton,
                SessionSubKeys.sigma: self.parent.ui.sigma_fix_radioButton,
                SessionSubKeys.tau: self.parent.ui.tau_fix_radioButton,
            },
            "from": {
                SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_from_lineEdit,
                SessionSubKeys.sigma: self.parent.ui.sigma_from_lineEdit,
                SessionSubKeys.tau: self.parent.ui.tau_from_lineEdit,
            },
            "to": {
                SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_to_lineEdit,
                SessionSubKeys.sigma: self.parent.ui.sigma_to_lineEdit,
                SessionSubKeys.tau: self.parent.ui.tau_to_lineEdit,
            },
            "step": {
                SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_step_lineEdit,
                SessionSubKeys.sigma: self.parent.ui.sigma_step_lineEdit,
                SessionSubKeys.tau: self.parent.ui.tau_step_lineEdit,
            },
        }

        try:
            if list_ui["fix_radio"][parameter].isChecked():
                list_value = [float(list_ui["fix_value"][parameter].text())]
            else:
                _from = float(list_ui["from"][parameter].text())
                _to = float(list_ui["to"][parameter].text())
                _step = float(list_ui["step"][parameter].text())

                value = _from
                list_value = []
                while value <= _to:
                    list_value.append(value)
                    value += _step

        except ValueError:
            raise fitting_error.BraggPeakFittingError(
                fitting_region=FittingRegions.bragg_peak, message=error_message
            )

        return list_value

    def kropff_row_selected(self):
        kropff_tab_ui_selected = self.kropff_table_ui_selected()
        o_table = TableHandler(table_ui=kropff_tab_ui_selected)
        row_selected = o_table.get_rows_of_table_selected()
        return row_selected

    def kropff_table_ui_selected(self):
        tab_selected = self.kropff_tab_selected()
        if tab_selected == KropffTabSelected.high_tof:
            return self.parent.ui.high_lda_tableWidget
        elif tab_selected == KropffTabSelected.low_tof:
            return self.parent.ui.low_lda_tableWidget
        elif tab_selected == KropffTabSelected.bragg_peak:
            return self.parent.ui.bragg_edge_tableWidget
        elif tab_selected == KropffTabSelected.summary:
            return None
        elif tab_selected == KropffTabSelected.settings:
            return None

    def kropff_tab_selected(self):
        tab_selected_index = self.parent.ui.kropff_tabWidget.currentIndex()
        if tab_selected_index == 1:
            return KropffTabSelected.low_tof
        elif tab_selected_index == 2:
            return KropffTabSelected.high_tof
        elif tab_selected_index == 3:
            return KropffTabSelected.bragg_peak
        elif tab_selected_index == 0:
            return KropffTabSelected.settings
        elif tab_selected_index == 4:
            return KropffTabSelected.summary

    def kropff_matplotlib_ui_selected(self):
        tab_selected = self.kropff_tab_selected()
        if tab_selected == KropffTabSelected.high_tof:
            return self.parent.kropff_high_plot
        elif tab_selected == KropffTabSelected.low_tof:
            return self.parent.kropff_low_plot
        elif tab_selected == KropffTabSelected.bragg_peak:
            return self.parent.kropff_bragg_peak_plot
        elif tab_selected == KropffTabSelected.settings:
            return None
        elif tab_selected == KropffTabSelected.summary:
            return None
        else:
            raise ValueError("Tab selected is invalid!")

    def kropff_fitting_parameters_radioButton_selected(self):
        tab_selected = self.kropff_tab_selected()
        if tab_selected == KropffTabSelected.high_tof:
            if self.parent.ui.kropff_a0_radioButton.isChecked():
                return "a0"
            elif self.parent.ui.kropff_b0_radioButton.isChecked():
                return "b0"
            else:
                raise ValueError("fitting parameters is invalid!")
        elif tab_selected == KropffTabSelected.low_tof:
            if self.parent.ui.kropff_ahkl_radioButton.isChecked():
                return "ahkl"
            elif self.parent.ui.kropff_bhkl_radioButton.isChecked():
                return "bhkl"
            else:
                raise ValueError("fitting parameters is invalid!")
        elif tab_selected == KropffTabSelected.bragg_peak:
            if self.parent.ui.kropff_lda_hkl_radioButton.isChecked():
                return "lambda_hkl"
            elif self.parent.ui.kropff_tau_radioButton.isChecked():
                return "tau"
            elif self.parent.ui.kropff_sigma_radioButton.isChecked():
                return "sigma"
            else:
                raise ValueError("fitting parameters is invalid!")
        elif tab_selected == KropffTabSelected.settings:
            return None
        elif tab_selected == KropffTabSelected.summary:
            return None
        else:
            raise ValueError("Tab selected is invalid!")

    def active_d0(self):
        lambda0 = float(self.parent.ui.bragg_edge_calculated.text())
        return lambda0 / 2.0

    def calculate_image_size(self):
        live_data = self.grand_parent.data_metadata[DataType.normalized]["data"]
        integrated_image = np.mean(live_data, 0)
        self.parent.integrated_image = np.transpose(integrated_image)
        [self.image_size["height"], self.image_size["width"]] = np.shape(
            integrated_image
        )

    def calculate_d_array(self):
        self.calculate_image_size()
        width = self.image_size["width"]
        height = self.image_size["height"]

        d_array = np.zeros((height, width))
        # d_array[:] = np.nan
        d_dict = {}

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        for _row_index in kropff_table_dictionary.keys():
            _row_entry = kropff_table_dictionary[_row_index]

            bin_coordinates = _row_entry["bin_coordinates"]

            x0 = bin_coordinates["x0"]
            x1 = bin_coordinates["x1"]
            y0 = bin_coordinates["y0"]
            y1 = bin_coordinates["y1"]

            lambda_hkl = _row_entry["lambda_hkl"]["val"]
            lambda_hkl_err = _row_entry["lambda_hkl"]["err"]
            if lambda_hkl_err is None:
                lambda_hkl_err = np.sqrt(lambda_hkl)

            d_array[y0:y1, x0:x1] = float(lambda_hkl) / 2.0
            d_dict[_row_index] = {
                "val": float(lambda_hkl) / 2.0,
                "err": float(lambda_hkl_err) / 2.0,
            }

        # self.parent.d_array = d_array
        self.parent.d_dict = d_dict

    def strain_mapping_dictionary(self):
        self.calculate_d_array()
        d_dict = self.parent.d_dict
        strain_mapping_dict = {}
        for _row in d_dict.keys():
            d0 = self.active_d0()
            d = d_dict[_row]["val"]
            d_error = d_dict[_row]["err"]
            strain_mapping = (d - d0) / d0
            strain_mapping_err = d_error + np.sqrt(d0)

            strain_mapping_dict[_row] = {
                "val": strain_mapping,
                "err": strain_mapping_err,
            }

        return strain_mapping_dict

    def nbr_row(self):
        list_row = []
        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        for _row_index in kropff_table_dictionary.keys():
            _row = kropff_table_dictionary[_row_index][FittingKeys.row_index]
            list_row.append(_row)
        set_list_row = set(list(list_row))
        return len(set_list_row)

    def nbr_column(self):
        list_column = []
        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        for _row_index in kropff_table_dictionary.keys():
            _row = kropff_table_dictionary[_row_index][FittingKeys.column_index]
            list_column.append(_row)
        set_list_column = set(list(list_column))
        return len(set_list_column)
