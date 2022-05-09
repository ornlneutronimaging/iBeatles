from qtpy.QtWidgets import QDialog

from ibeatles import load_ui


class KropffGoodFitSettingsLauncher(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        super(QDialog, self).__init__(parent)
        self.ui = load_ui('ui_kropff_good_fit_settings.ui', baseinstance=self)
        self.init_widgets()

    def init_widgets(self):
        self.ui.l_hkl_error_label.setText(u"\u03BB<sub>hkl</sub>")
        self.ui.t_error_label.setText(u"\u03c4")
        self.ui.sigma_error_label.setText(u"\u03c3")

    def ok_clicked(self):
        pass

    def lambda_hkl_clicked(self):
        state = self.ui.lambda_hkl_checkBox.isChecked()
        self.ui.l_hkl_label.setEnabled(state)
        self.ui.lambda_hkl_doubleSpinBox.setEnabled(state)

    def tau_clicked(self):
        state = self.ui.tau_checkBox.isChecked()
        self.ui.t_label.setEnabled(state)
        self.ui.tau_doubleSpinBox.setEnabled(state)

    def sigma_clicked(self):
        state = self.ui.sigma_checkBox.isChecked()
        self.ui.sigma_label.setEnabled(state)
        self.ui.sigma_doubleSpinBox.setEnabled(state)
