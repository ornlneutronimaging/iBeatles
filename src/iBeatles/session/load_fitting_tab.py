from .. import DataType


class LoadFitting:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def table_dictionary(self):
        self.parent.session_dict['fitting'] = self.session_dict["fitting"]
        self.parent.table_loaded_from_session = True
        