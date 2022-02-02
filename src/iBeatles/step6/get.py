import numpy as np


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def active_d0(self):
        if self.parent.ui.d0_value.isChecked():
            return np.float(self.parent.ui.d0_value.text())
        else:
            return np.float(self.parent.ui.d0_user_value.text())
