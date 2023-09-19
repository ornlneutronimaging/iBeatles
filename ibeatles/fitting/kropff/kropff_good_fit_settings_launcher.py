from qtpy.QtWidgets import QDialog

from ibeatles import load_ui


class KropffGoodFitSettingsLauncher(QDialog):

    fit_conditions = {}

    def __init__(self, parent=None):
        self.parent = parent
        super(QDialog, self).__init__(parent)
        self.ui = load_ui('ui_kropff_good_fit_settings.ui', baseinstance=self)
        self.fit_conditions = self.parent.kropff_bragg_peak_good_fit_conditions
        self.rejection_conditions = self.parent.kropff_bragg_peak_row_rejections_conditions
        self.init_widgets()

    def init_widgets(self):
        self.ui.l_hkl_error_label.setText(u"\u03BB<sub>hkl</sub>")
        self.ui.t_error_label.setText(u"\u03c4")
        self.ui.sigma_error_label.setText(u"\u03c3")

        self.ui.l_hkl_less_than_label.setText(u"\u03BB<sub>hkl</sub>")
        self.ui.l_hkl_more_than_label.setText(u"\u03BB<sub>hkl</sub>")

        fit_conditions = self.fit_conditions
        self.ui.lambda_hkl_checkBox.setChecked(fit_conditions['l_hkl_error']['state'])
        self.ui.lambda_hkl_doubleSpinBox.setValue(fit_conditions['l_hkl_error']['value'])
        self.ui.tau_checkBox.setChecked(fit_conditions['t_error']['state'])
        self.ui.tau_doubleSpinBox.setValue(fit_conditions['t_error']['value'])
        self.ui.sigma_checkBox.setChecked(fit_conditions['sigma_error']['state'])
        self.ui.sigma_doubleSpinBox.setValue(fit_conditions['sigma_error']['value'])

        rejection_conditions = self.rejection_conditions
        self.ui.l_hkl_less_than_checkBox.setChecked(rejection_conditions['l_hkl']['less_than']['state'])
        self.ui.l_hkl_less_than_doubleSpinBox.setValue(rejection_conditions['l_hkl']['less_than']['value'])
        self.ui.l_hkl_more_than_checkBox.setChecked(rejection_conditions['l_hkl']['more_than']['state'])
        self.ui.l_hkl_more_than_doubleSpinBox.setValue(rejection_conditions['l_hkl']['more_than']['value'])

        self.lambda_hkl_clicked()
        self.tau_clicked()
        self.sigma_clicked()
        self.l_hkl_less_than_clicked()
        self.l_hkl_more_than_clicked()

    def ok_clicked(self):
        l_hkl_error = {'state': self.ui.lambda_hkl_checkBox.isChecked(),
                       'value': self.ui.lambda_hkl_doubleSpinBox.value()}
        t_error = {'state': self.ui.tau_checkBox.isChecked(),
                   'value': self.ui.tau_doubleSpinBox.value()}
        sigma_error = {'state': self.ui.sigma_checkBox.isChecked(),
                       'value': self.ui.sigma_doubleSpinBox.value()}

        self.parent.kropff_bragg_peak_good_fit_conditions['l_hkl_error'] = l_hkl_error
        self.parent.kropff_bragg_peak_good_fit_conditions['t_error'] = t_error
        self.parent.kropff_bragg_peak_good_fit_conditions['sigma_error'] = sigma_error

        l_hkl_less_than = {'state': self.ui.l_hkl_less_than_checkBox.isChecked(),
                           'value': self.ui.l_hkl_less_than_doubleSpinBox.value()}
        l_hkl_more_than = {'state': self.ui.l_hkl_more_than_checkBox.isChecked(),
                           'value': self.ui.l_hkl_more_than_doubleSpinBox.value()}
        self.parent.kropff_bragg_peak_row_rejections_conditions = {'l_hkl': {'less_than': l_hkl_less_than,
                                                                             'more_than': l_hkl_more_than,
                                                                             },
                                                                   }

        self.parent.update_locked_and_rejected_rows_in_bragg_peak_table()
        self.close()

    def lambda_hkl_clicked(self):
        state = self.ui.lambda_hkl_checkBox.isChecked()
        self.ui.l_hkl_label.setEnabled(state)
        self.ui.lambda_hkl_doubleSpinBox.setEnabled(state)
        self.check_ok_button()

    def tau_clicked(self):
        state = self.ui.tau_checkBox.isChecked()
        self.ui.t_label.setEnabled(state)
        self.ui.tau_doubleSpinBox.setEnabled(state)
        self.check_ok_button()

    def sigma_clicked(self):
        state = self.ui.sigma_checkBox.isChecked()
        self.ui.sigma_label.setEnabled(state)
        self.ui.sigma_doubleSpinBox.setEnabled(state)
        self.check_ok_button()

    def l_hkl_less_than_clicked(self):
        state = self.ui.l_hkl_less_than_checkBox.isChecked()
        self.ui.l_hkl_less_than_label.setEnabled(state)
        self.ui.l_hkl_label_2.setEnabled(state)
        self.ui.l_hkl_less_than_doubleSpinBox.setEnabled(state)

    def l_hkl_more_than_clicked(self):
        state = self.ui.l_hkl_more_than_checkBox.isChecked()
        self.ui.l_hkl_more_than_label.setEnabled(state)
        self.ui.l_hkl_label_3.setEnabled(state)
        self.ui.l_hkl_more_than_doubleSpinBox.setEnabled(state)

    def check_ok_button(self):
        state1 = self.ui.lambda_hkl_checkBox.isChecked()
        state2 = self.ui.tau_checkBox.isChecked()
        state3 = self.ui.sigma_checkBox.isChecked()

        if (not state1) and (not state2) and (not state3):
            button_state = False
        else:
            button_state = True

        self.ui.ok_pushButton.setEnabled(button_state)
