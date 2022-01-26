import numpy as np
from lmfit import Model, Parameter

from src.iBeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
import src.iBeatles.utilities.error as fitting_error
from src.iBeatles.fitting.kropff.get import Get
from src.iBeatles.fitting.kropff.fitting_functions import kropff_high_lambda, kropff_bragg_peak_tof, kropff_low_lambda
from src.iBeatles.fitting import KropffTabSelected
from src.iBeatles.utilities.array_utilities import find_nearest_index


class FitRegions:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        self.o_get = Get(parent=parent)
        self.table_dictionary = self.grand_parent.kropff_table_dictionary

    def all_regions(self):
        type_error = ""

        # o_event = KropffBraggPeakThresholdCalculator(parent=self.parent,
        #                                              grand_parent=self.grand_parent)
        # o_event.save_all_profiles()

        # o_display = Display(parent=self.parent,
        #                     grand_parent=self.grand_parent)
        # o_display.display_bragg_peak_threshold()

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

        if type_error:
            show_status_message(parent=self.parent,
                                message=f"Error fitting {type_error}",
                                status=StatusMessageStatus.error,
                                duration_s=5)

    def high_lambda(self):
        gmodel = Model(kropff_high_lambda, missing='drop', independent_vars=['lda'])

        a0 = self.o_get.a0()
        b0 = self.o_get.b0()

        table_dictionary = self.table_dictionary
        for _key in table_dictionary.keys():
            xaxis = table_dictionary[_key]['xaxis']
            yaxis = table_dictionary[_key]['yaxis']

            right = table_dictionary[_key]['bragg peak threshold']['right']

            nearest_index = find_nearest_index(xaxis, right)

            yaxis = yaxis[nearest_index:-1]
            xaxis = xaxis[nearest_index:-1]

            yaxis = -np.log(yaxis)
            _result = gmodel.fit(yaxis, lda=xaxis, a0=a0, b0=b0)
            a0 = _result.params['a0'].value
            a0_error = _result.params['a0'].stderr
            b0 = _result.params['b0'].value
            b0_error = _result.params['b0'].stderr
            yaxis_fitted = kropff_high_lambda(xaxis, a0, b0)

            table_dictionary[_key]['a0'] = {'val': a0,
                                            'err': a0_error}
            table_dictionary[_key]['b0'] = {'val': b0,
                                            'err': b0_error}
            table_dictionary[_key]['fitted'][KropffTabSelected.high_tof] = {'xaxis': xaxis,
                                                                            'yaxis': yaxis_fitted}

            # import pprint
            # pprint.pprint(table_dictionary[_key])


    def low_lambda(self):
        ahkl = self.o_get.ahkl()
        bhkl = self.o_get.bhkl()

    def bragg_peak(self):
        lambda_hkl = self.o_get.lambda_hkl()
        tau = self.o_get.tau()
