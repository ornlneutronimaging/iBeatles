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
        common_xaxis = None
        nearest_index = -1
        for _key in table_dictionary.keys():

            if nearest_index == -1:
                xaxis = table_dictionary[_key]['xaxis']

                right = table_dictionary[_key]['bragg peak threshold']['right']

                nearest_index = find_nearest_index(xaxis, right)
                xaxis = xaxis[nearest_index:-1]
                common_xaxis = xaxis

            yaxis = table_dictionary[_key]['yaxis']
            yaxis = yaxis[nearest_index:-1]
            yaxis = -np.log(yaxis)

            _result = gmodel.fit(yaxis, lda=common_xaxis, a0=a0, b0=b0)
            a0 = _result.params['a0'].value
            a0_error = _result.params['a0'].stderr
            b0 = _result.params['b0'].value
            b0_error = _result.params['b0'].stderr
            yaxis_fitted = kropff_high_lambda(common_xaxis, a0, b0)

            table_dictionary[_key]['a0'] = {'val': a0,
                                            'err': a0_error}
            table_dictionary[_key]['b0'] = {'val': b0,
                                            'err': b0_error}
            table_dictionary[_key]['fitted'][KropffTabSelected.high_tof] = {'xaxis': common_xaxis,
                                                                            'yaxis': yaxis_fitted}

    def low_lambda(self):
        gmodel = Model(kropff_low_lambda, missing='drop', independent_vars=['lda'])

        ahkl = self.o_get.ahkl()
        bhkl = self.o_get.bhkl()

        table_dictionary = self.table_dictionary
        common_xaxis = None
        nearest_index = -1
        for _key in table_dictionary.keys():

            table_entry = table_dictionary[_key]

            if nearest_index == -1:
                xaxis = table_entry['xaxis']
                a0 = table_entry['a0']['val']
                b0 = table_entry['b0']['val']

                left = table_entry['bragg peak threshold']['left']

                nearest_index = find_nearest_index(xaxis, left)
                xaxis = xaxis[: nearest_index+1]
                common_xaxis = xaxis

            yaxis = table_entry['yaxis']
            yaxis = yaxis[: nearest_index+1]
            yaxis = -np.log(yaxis)

            _result = gmodel.fit(yaxis,
                                 lda=common_xaxis,
                                 a0=Parameter('a0', value=a0, vary=False),
                                 b0=Parameter('b0', value=b0, vary=False),
                                 ahkl=ahkl,
                                 bhkl=bhkl)

            ahkl = _result.params['ahkl'].value
            ahkl_error = _result.params['ahkl'].stderr
            bhkl = _result.params['bhkl'].value
            bhkl_error = _result.params['bhkl'].stderr
            yaxis_fitted = kropff_low_lambda(common_xaxis, a0, b0, ahkl, bhkl)

            table_dictionary[_key]['ahkl'] = {'val': ahkl,
                                              'err': ahkl_error}
            table_dictionary[_key]['bhkl'] = {'val': bhkl,
                                              'err': bhkl_error}
            table_dictionary[_key]['fitted'][KropffTabSelected.low_tof] = {'xaxis': common_xaxis,
                                                                           'yaxis': yaxis_fitted}

    def bragg_peak(self):
        lambda_hkl = self.o_get.lambda_hkl()
        tau = self.o_get.tau()
