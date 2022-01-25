import logging

from src.iBeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
import src.iBeatles.utilities.error as fitting_error
from src.iBeatles.fitting.kropff import FittingRegions


class FitRegions:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def all_regions(self):
        try:
            self.high_lambda()
            self.low_lambda()
            self.bragg_peak()
        except fitting_error.HighLambdaFittingError as err:
            type_error = err
        except fitting_error.LowLambdaFittingError as err:
            type_error = err
        except fitting_error.BraggPeakFittingError as err:
            type_error = err

        show_status_message(parent=self.parent,
                            message=f"Error fitting {type_error}",
                            status=StatusMessageStatus.error,
                            duration_s=5)

    def high_lambda(self):
        a0 = self.parent.ui.kropff_high_lda_a0_init.text()
        raise fitting_error.HighLambdaFittingError(fitting_region=FittingRegions.high_lambda,
                                                   message="Wrong a0 format!")

    def low_lambda(self):
        pass

    def bragg_peak(self):
        pass
