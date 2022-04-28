from .. import DataType


class LoadFitting:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def table_dictionary(self):
        self.parent.session_dict['fitting'] = self.session_dict["fitting"]
        self.parent.table_loaded_from_session = True

        self.parent.data_metadata[DataType.bin]['ui_accessed'] = self.parent.session_dict['fitting']['ui accessed']
        self.parent.image_view_settings[DataType.fitting]['state'] = \
            self.parent.session_dict[DataType.fitting]['image view state']
        self.parent.image_view_settings[DataType.fitting]['histogram'] = \
            self.parent.session_dict[DataType.fitting]['image view histogram']
