from qtpy.QtWidgets import QDialog
import os

from ibeatles import load_ui, DataType
from ibeatles.utilities.gui_handler import GuiHandler


class InfosLauncher:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.infos_id is None:
            infos_id = Infos(parent=self.parent)
            infos_id.show()
            self.parent.infos_id = infos_id
        else:
            self.parent.infos_id.activateWindow()
            self.parent.infos_id.setFocus()


class Infos(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'ui_infos.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Folders Infos")

        self.ui.sample_textEdit.setReadOnly(True)
        self.ui.ob_textEdit.setReadOnly(True)
        self.ui.normalized_textEdit.setReadOnly(True)
        self.update()

    def ok_clicked(self):
        self.close()

    def closeEvent(self, a0):
        self.parent.infos_id = None

    def update(self):
        # get current main tab activated (sample, ob or normalized)
        o_gui = GuiHandler(parent=self.parent)
        data_type = o_gui.get_active_tab()

        # jump to tab that corresponds to current main tab activated
        if data_type == DataType.sample:
            tab_index = 0
        elif data_type == DataType.ob:
            tab_index = 1
        else:
            tab_index = 2
        self.ui.toolBox.setCurrentIndex(tab_index)

        # disable or not tabs
        infos_dict = self.parent.infos_dict
        if infos_dict[DataType.sample] is None:
            self.ui.toolBox.setItemEnabled(0, False)
        if infos_dict[DataType.ob] is None:
            self.ui.toolBox.setItemEnabled(1, False)
        if infos_dict[DataType.normalized] is None:
            self.ui.toolBox.setItemEnabled(2, False)
