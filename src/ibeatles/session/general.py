from src.ibeatles.session import SessionSubKeys


class General:
    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def settings(self):
        if self.session_dict.get("log buffer size", None):
            pass
        else:
            self.session_dict[SessionSubKeys.log_buffer_size] = (
                self.parent.default_session_dict[SessionSubKeys.log_buffer_size]
            )
