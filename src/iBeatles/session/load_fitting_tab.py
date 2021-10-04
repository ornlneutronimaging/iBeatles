from .. import DataType


class LoadFitting:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def table_dictionary(self):
        formatted_table_dictionary = self.session_dict["fitting"]["table dictionary"]

        self.parent.table_dictionary_from_session = formatted_table_dictionary
