from qtpy import QtCore
from qtpy.QtWidgets import QDialog
import numpy as np
from collections import OrderedDict

from ibeatles import Material
from ibeatles.utilities.gui_handler import GuiHandler
from ibeatles import load_ui


class ListHKLLambdaD0Handler:

    def __init__(self, parent=None):
        if parent.list_hkl_lambda_d0_ui is None:
            list_dialog = ListHKLLambdaD0(parent=parent)
            list_dialog.show()
            parent.list_hkl_lambda_d0_ui = list_dialog
        else:
            parent.list_hkl_lambda_d0_ui.setFocus()
            parent.list_hkl_lambda_d0_ui.activateWindow()


class ListHKLLambdaD0(QDialog):
    new_element = {}

    def __init__(self, parent=None):
        self.parent = parent

        QDialog.__init__(self, parent=parent)
        self.ui = load_ui('ui_list_hkl.ui', baseinstance=self)
        self.setWindowTitle("List of h, k, l, lambda and d0")

    def closeEvent(self, ev):
        self.parent.list_hkl_lambda_d0_ui = None

    def close_clicked(self):
        self.parent.list_hkl_lambda_d0_ui = None
        self.close()
        