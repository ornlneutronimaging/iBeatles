import logging

from .save_tab import SaveTab
from .. import DataType
from ..utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities


class SaveFittingTab(SaveTab):

    def fitting(self):

        if not self.parent.data_metadata[DataType.fitting]['ui_accessed']:
            return

        self.general_infos()
        self.march_dollase()
        self.kropff()

    def general_infos(self):
        logging.info("Recording general fitting parameters")

        if self.parent.fitting_image_view:
            o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                        image_view=self.parent.fitting_image_view,
                                        data_type=DataType.fitting)
            state = o_pyqt.get_state()
            o_pyqt.save_histogram_level(data_type_of_data=DataType.normalized)
            histogram = self.parent.image_view_settings[DataType.fitting]['histogram']
        else:
            state = None
            histogram = None

        fitting_bragg_edge_linear_selection = self.parent.fitting_bragg_edge_linear_selection
        if fitting_bragg_edge_linear_selection:
            min_lambda_index = int(fitting_bragg_edge_linear_selection[0])
            max_lambda_index = int(fitting_bragg_edge_linear_selection[1])
            self.session_dict[DataType.fitting]['lambda range index'] = [min_lambda_index, max_lambda_index]

        logging.info(f" state: {state}")
        logging.info(f" histogram: {histogram}")

        self.session_dict[DataType.fitting]['x_axis'] = [float(x) for x in
                                                         self.parent.normalized_lambda_bragg_edge_x_axis]
        self.session_dict[DataType.fitting]['transparency'] = self.parent.fitting_transparency_slider_value
        self.session_dict[DataType.fitting]['image view state'] = state
        self.session_dict[DataType.fitting]['image view histogram'] = histogram
        self.session_dict[DataType.fitting]['ui accessed'] = self.parent.data_metadata[DataType.bin]['ui_accessed']
        self.session_dict[DataType.fitting]['ui'] = self.parent.session_dict[DataType.fitting]['ui']

    def march_dollase(self):
        logging.info("Recording March-Dollase fitting parameters")

        if self.parent.fitting_ui:
            self.parent.fitting_ui.save_all_parameters()

        table_dictionary = self.parent.march_table_dictionary

        formatted_table_dictionary = {}

        for _row in table_dictionary.keys():
            _entry = table_dictionary[_row]

            active_flag = _entry['active']
            lock_flag = _entry['lock']
            fitting_confidence = _entry['fitting_confidence']
            d_spacing = _entry['d_spacing']
            sigma = _entry['sigma']
            alpha = _entry['alpha']
            a1 = _entry['a1']
            a2 = _entry['a2']
            a5 = _entry['a5']
            a6 = _entry['a6']

            formatted_table_dictionary[_row] = {'active'            : active_flag,
                                                'lock'              : lock_flag,
                                                'fitting_confidence': fitting_confidence,
                                                'd_spacing'         : d_spacing,
                                                'sigma'             : sigma,
                                                'alpha'             : alpha,
                                                'a1'                : a1,
                                                'a2'                : a2,
                                                'a5'                : a5,
                                                'a6'                : a6}
        self.session_dict[DataType.fitting]['march dollase']["table dictionary"] = formatted_table_dictionary
        self.session_dict[DataType.fitting]['march dollase']['plot active row flag'] = \
            self.parent.display_active_row_flag

        logging.info(f" x_axis: {self.session_dict[DataType.fitting]['x_axis']}")
        logging.info(f" lambda range index: {self.session_dict['fitting']['lambda range index']}")

    def kropff(self):
        logging.info("Recording Kropff fitting parameters")
        table_dictionary = self.parent.kropff_table_dictionary

        formatted_table_dictionary = {}

        for _row in table_dictionary.keys():
            _entry = table_dictionary[_row]

            a0 = _entry['a0']
            b0 = _entry['b0']
            ahkl = _entry['ahkl']
            bhkl = _entry['bhkl']
            lambda_hkl = _entry['lambda_hkl']
            tau = _entry['tau']
            sigma = _entry['sigma']
            bragg_peak_threshold = _entry['bragg peak threshold']

            formatted_table_dictionary[_row] = {'a0': a0,
                                                'b0': b0,
                                                'ahkl': ahkl,
                                                'bhkl': bhkl,
                                                'lambda_hkl': lambda_hkl,
                                                'tau': tau,
                                                'sigma': sigma,
                                                'bragg_peak_threshold': bragg_peak_threshold}
        self.session_dict[DataType.fitting]['kropff']["table dictionary"] = formatted_table_dictionary
        self.session_dict[DataType.fitting]['kropff']["automatic bragg peak threshold finder"] = \
            self.parent.session_dict['fitting']['kropff']["automatic bragg peak threshold finder"]

        # self.session_dict[DataType.fitting]['kropff'] = self.parent.session_dict[DataType.fitting]['kropff']
