import logging

from .save_tab import SaveTab
from .. import DataType


class SaveFittingTab(SaveTab):

    def fitting(self):
        table_dictionary = self.parent.table_dictionary

        logging.info("Recording fitting table dictionary")
        logging.info(table_dictionary)

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

            formatted_table_dictionary[_row] = {'active': active_flag,
                                                'lock': lock_flag,
                                                'fitting_confidence': fitting_confidence,
                                                'd_spacing': d_spacing,
                                                'sigma': sigma,
                                                'alpha': alpha,
                                                'a1': a1,
                                                'a2': a2,
                                                'a5': a5,
                                                'a6': a6}

        self.session_dict["fitting"]["table dictionary"] = formatted_table_dictionary
