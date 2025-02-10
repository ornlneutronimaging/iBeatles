from src.ibeatles import DataType
from src.ibeatles.session import SessionKeys, SessionSubKeys


class LoadFitting:
    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def table_dictionary(self):
        self.parent.session_dict[SessionKeys.fitting] = self.session_dict[
            SessionKeys.fitting
        ]
        self.parent.table_loaded_from_session = True

        self.parent.image_view_settings[DataType.fitting]["state"] = (
            self.parent.session_dict[DataType.fitting][SessionSubKeys.image_view_state]
        )
        self.parent.image_view_settings[DataType.fitting]["histogram"] = (
            self.parent.session_dict[DataType.fitting][
                SessionSubKeys.image_view_histogram
            ]
        )
