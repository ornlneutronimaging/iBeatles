from .. import DataType


class LoadNormalization:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def roi(self):

        session_dict = self.session_dict

        list_roi = session_dict[DataType.normalization]['roi']
        self.parent.list_roi[DataType.normalization] = list_roi
