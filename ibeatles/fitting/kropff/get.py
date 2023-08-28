import numpy as np

from ibeatles.fitting.kropff import FittingRegions
import ibeatles.utilities.error as fitting_error
from ibeatles.fitting.kropff import SessionSubKeys


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def a0(self):
        a0 = self.parent.ui.kropff_high_lda_a0_init.text()
        try:
            a0 = float(a0)
        except ValueError:
            raise fitting_error.HighLambdaFittingError(fitting_region=FittingRegions.high_lambda,
                                                       message=u"Wrong a\u2080 format!")
        return a0

    def b0(self):
        b0 = self.parent.ui.kropff_high_lda_b0_init.text()
        try:
            b0 = float(b0)
        except ValueError:
            raise fitting_error.HighLambdaFittingError(fitting_region=FittingRegions.high_lambda,
                                                       message=u"Wrong b\u2080 format!")
        return b0

    def ahkl(self):
        ahkl = self.parent.ui.kropff_low_lda_ahkl_init.text()
        try:
            ahkl = float(ahkl)
        except ValueError:
            raise fitting_error.LowLambdaFittingError(fitting_region=FittingRegions.low_lambda,
                                                      message=u"Wrong a\u2095\u2096\u2097 format!")
        return ahkl

    def bhkl(self):
        bhkl = self.parent.ui.kropff_low_lda_bhkl_init.text()
        try:
            bhkl = float(bhkl)
        except ValueError:
            raise fitting_error.LowLambdaFittingError(fitting_region=FittingRegions.low_lambda,
                                                      message="Wrong b\u2095\u2096\u2097 format!")
        return bhkl

    def lambda_hkl(self):
        lambda_hkl = self.parent.kropff_lambda_settings['fix']
        try:
            lambda_hkl = float(lambda_hkl)
        except ValueError:
            raise fitting_error.BraggPeakFittingError(fitting_region=FittingRegions.bragg_peak,
                                                      message=u"Wrong \u03BB\u2095\u2096\u2097 format!")
        return lambda_hkl

    def tau(self):
        tau = self.parent.ui.kropff_bragg_peak_tau_init.text()
        try:
            tau = float(tau)
        except ValueError:
            raise fitting_error.BraggPeakFittingError(fitting_region=FittingRegions.bragg_peak,
                                                      message=u"Wrong \u03c4 format!")
        return tau

    def sigma(self):
        sigma = self.parent.ui.kropff_bragg_peak_sigma_comboBox.currentText()
        try:
            sigma = float(sigma)
        except ValueError:
            raise fitting_error.BraggPeakFittingError(fitting_region=FittingRegions.bragg_peak,
                                                      message=u"Wrong sigma format!")
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
        return self._list_parameter_initial_guess(parameter=SessionSubKeys.lambda_hkl,
                                                  error_message=u"Wrong \u03BB\u2095\u2096\u2097 format!")

    def list_sigma_initial_guess(self):
        return self._list_parameter_initial_guess(parameter=SessionSubKeys.sigma,
                                                  error_message=u"Wrong sigma format!")

    def list_tau_initial_guess(self):
        return self._list_parameter_initial_guess(parameter=SessionSubKeys.sigma,
                                                  error_message=u"Wrong tau format!")

    def _list_parameter_initial_guess(self, parameter=SessionSubKeys.lambda_hkl,
                                      error_message=u"Wrong \u03BB\u2095\u2096\u2097 format!"):

        list_ui = {'fix_value': {SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_fix_lineEdit,
                                 SessionSubKeys.sigma: self.parent.ui.sigma_fix_lineEdit,
                                 SessionSubKeys.tau: self.parent.ui.tau_fix_lineEdit,
                                 },
                   'fix_radio': {SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_fix_radioButton,
                                 SessionSubKeys.sigma: self.parent.ui.sigma_fix_radioButton,
                                 SessionSubKeys.tau: self.parent.ui.tau_fix_radioButton,
                                 },
                   'from': {SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_from_lineEdit,
                            SessionSubKeys.sigma: self.parent.ui.sigma_from_lineEdit,
                            SessionSubKeys.tau: self.parent.ui.tau_from_lineEdit,
                            },
                   'to': {SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_to_lineEdit,
                          SessionSubKeys.sigma: self.parent.ui.sigma_to_lineEdit,
                          SessionSubKeys.tau: self.parent.ui.tau_to_lineEdit,
                          },
                   'step': {SessionSubKeys.lambda_hkl: self.parent.ui.lambda_hkl_step_lineEdit,
                            SessionSubKeys.sigma: self.parent.ui.sigma_step_lineEdit,
                            SessionSubKeys.tau: self.parent.ui.tau_step_lineEdit,
                            },
                   }

        try:
            if list_ui['fix_radio'][parameter].isChecked():
                list_value = [float(list_ui['fix_value'][parameter].text())]
            else:
                _from = float(list_ui['from'][parameter].text())
                _to = float(list_ui['to'][parameter].text())
                _step = float(list_ui['step'][parameter].text())

                value = _from
                list_value = []
                while (value <= _to):
                    list_value.append(value)
                    value += _step

        except ValueError:
            raise fitting_error.BraggPeakFittingError(fitting_region=FittingRegions.bragg_peak,
                                                      message=error_message)

        return list_value
