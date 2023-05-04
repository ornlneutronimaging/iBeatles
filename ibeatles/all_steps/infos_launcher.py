from qtpy.QtWidgets import QDialog
import os

from ibeatles import load_ui


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

    def ok_clicked(self):
        self.close()

    def closeEvent(self, a0):
        self.parent.infos_id = None
