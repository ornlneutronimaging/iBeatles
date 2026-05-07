import numpy as np


class CheckingFittingConditions:
    def __init__(self, fit_conditions=None):
        self.max_l_hkl_error_value = fit_conditions["l_hkl_error"]["value"]
        self.l_hkl_error_state = fit_conditions["l_hkl_error"]["state"]

        self.max_t_error_value = fit_conditions["t_error"]["value"]
        self.t_error_state = fit_conditions["t_error"]["state"]

        self.max_sigma_error_value = fit_conditions["sigma_error"]["value"]
        self.sigma_error_state = fit_conditions["sigma_error"]["state"]

    def is_fitting_ok(self, l_hkl_error=None, t_error=None, sigma_error=None):
        if self.l_hkl_error_state:
            if l_hkl_error is None:
                return False

            if not np.isfinite(l_hkl_error):
                return False

            if l_hkl_error > self.max_l_hkl_error_value:
                return False

        if self.t_error_state:
            if t_error is None:
                return False

            if not np.isfinite(t_error):
                return False

            if t_error > self.max_t_error_value:
                return False

        if self.sigma_error_state:
            if sigma_error is None:
                return False

            if not np.isfinite(sigma_error):
                return False

            if sigma_error > self.max_sigma_error_value:
                return False

        return True
