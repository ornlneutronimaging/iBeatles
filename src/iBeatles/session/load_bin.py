class LoadBin:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def all(self):
        session_dict = self.session_dict
