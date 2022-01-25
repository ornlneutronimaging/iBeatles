import numpy as np

from src.iBeatles.fitting.kropff import FittingRegions
import src.iBeatles.utilities.error as fitting_error


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def a0(self):
        a0 = self.parent.ui.kropff_high_lda_a0_init.text()
        try:
            a0 = np.float(a0)
        except ValueError:
            raise fitting_error.HighLambdaFittingError(fitting_region=FittingRegions.high_lambda,
                                                       message=u"Wrong a\u2080 format!")
        return a0

    def b0(self):
        b0 = self.parent.ui.kropff_high_lda_b0_init.text()
        try:
            b0 = np.float(b0)
        except ValueError:
            raise fitting_error.HighLambdaFittingError(fitting_region=FittingRegions.high_lambda,
                                                       message=u"Wrong b\u2080 format!")
        return b0

    def ahkl(self):
        ahkl = self.parent.ui.kropff_low_lda_ahkl_init.text()
        try:
            ahkl = np.float(ahkl)
        except ValueError:
            raise fitting_error.LowLambdaFittingError(fitting_region=FittingRegions.low_lambda,
                                                      message=u"Wrong a\u2095\u2096\u2097 format!")
        return ahkl

    def bhkl(self):
        bhkl = self.parent.ui.kropff_low_lda_bhkl_init.text()
        try:
            bhkl = np.float(bhkl)
        except ValueError:
            raise fitting_error.LowLambdaFittingError(fitting_region=FittingRegions.low_lambda,
                                                      message="Wrong b\u2095\u2096\u2097 format!")
        return bhkl

    def lambda_hkl(self):
        lambda_hkl = self.parent.ui.kropff_bragg_peak_ldahkl_init.text()
        try:
            lambda_hkl = np.float(lambda_hkl)
        except ValueError:
            raise fitting_error.BraggPeakFittingError(fitting_region=FittingRegions.bragg_peak,
                                                      message=u"Wrong \u03BB\u2095\u2096\u2097 format!")
        return lambda_hkl

    def tau(self):
        tau = self.parent.ui.kropff_bragg_peak_tau_init.text()
        try:
            tau = np.float(tau)
        except ValueError:
            raise fitting_error.BraggPeakFittingError(fitting_region=FittingRegions.bragg_peak,
                                                      message=u"Wrong \u03c4 format!")
        return tau
