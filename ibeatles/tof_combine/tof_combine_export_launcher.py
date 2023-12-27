from qtpy.QtWidgets import QDialog

import warnings
warnings.filterwarnings("ignore")

from ibeatles import load_ui
from ibeatles.tof_combine.utilities.get import Get


class TofCombineExportLauncher(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        self.ui = load_ui('ui_tof_combine_export.ui', baseinstance=self)

    def ok_clicked(self):
        o_get = Get(parent=self)
        data_type_selected = o_get.combine_export_mode()
        self.close()
        self.parent.combine_run(data_type_selected=data_type_selected)
