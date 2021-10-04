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

            formatted_table_dictionary[_row] = {'active': active_flag,
                                                'lock': lock_flag}

        self.session_dict["fitting"]["table dictionary"] = formatted_table_dictionary
