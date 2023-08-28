from qtpy.QtWidgets import QDialog

from ibeatles import load_ui


class KropffLambdaHKLSettings(QDialog):
    ### REMOVE_ME

    fit_conditions = {}

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        super(QDialog, self).__init__(parent)
        self.ui = load_ui('ui_kropff_lambda_hkl_settings.ui', baseinstance=self)
        self.init_widgets()

    def init_widgets(self):
        self.ui.fix_lineEdit.setText(str(self.parent.kropff_lambda_settings['fix']))
        from_value, to_value, step_value = self.parent.kropff_lambda_settings['range']
        self.ui.from_lineEdit.setText(str(from_value))
        self.ui.to_lineEdit.setText(str(to_value))
        self.ui.step_lineEdit.setText(str(step_value))
        if self.parent.kropff_lambda_settings['state'] == 'fix':
            self.ui.fix_radioButton.setChecked(True)
        else:
            self.ui.range_radioButton.setChecked(True)
        self.radio_button_changed()

    def done(self, value):
        self.ok_clicked()
        QDialog.done(self, value)

    def ok_clicked(self):
        if self.ui.fix_radioButton.isChecked():
            self.parent.kropff_lambda_settings['state'] = 'fix'
        else:
            self.parent.kropff_lambda_settings['state'] = 'range'

        try:
            fix_value = float(str(self.ui.fix_lineEdit.text()))
            from_value = float(str(self.ui.from_lineEdit.text()))
            to_value = float(str(self.ui.to_lineEdit.text()))
            step_value = float(str(self.ui.step_lineEdit.text()))
        except ValueError:
            self.init_widgets()
            return

        self.parent.kropff_lambda_settings['fix'] = fix_value
        self.parent.kropff_lambda_settings['range'] = [from_value, to_value, step_value]
        self.close()

    def radio_button_changed(self):
        fix_state = self.ui.fix_radioButton.isChecked()
        self.ui.fix_lineEdit.setEnabled(fix_state)
        self.ui.from_lineEdit.setEnabled(not fix_state)
        self.ui.to_label.setEnabled(not fix_state)
        self.ui.to_lineEdit.setEnabled(not fix_state)
        self.ui.step_label.setEnabled(not fix_state)
        self.ui.step_lineEdit.setEnabled(not fix_state)

    def check_ok_button(self):
        state1 = self.ui.lambda_hkl_checkBox.isChecked()
        state2 = self.ui.tau_checkBox.isChecked()
        state3 = self.ui.sigma_checkBox.isChecked()

        if (not state1) and (not state2) and (not state3):
            button_state = False
        else:
            button_state = True

        self.ui.ok_pushButton.setEnabled(button_state)
