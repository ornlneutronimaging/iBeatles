from qtpy.QtWidgets import QDialog
import os

from src.ibeatles import load_ui, DataType
from src.ibeatles.utilities.gui_handler import GuiHandler


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
            self.parent.infos_id.update()


class Infos(QDialog):
    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(
            os.path.dirname(__file__), os.path.join("ui", "ui_infos.ui")
        )
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

        # disable or not tabs and add message if not
        infos_dict = self.parent.infos_dict
        if infos_dict[DataType.sample] is None:
            self.ui.toolBox.setItemEnabled(0, False)
        else:
            self.ui.toolBox.setItemEnabled(0, True)
            _entry = infos_dict[DataType.sample]
            text = ""
            for key in _entry:
                text += "<b>{}</b>: {}<br/>".format(
                    _entry[key]["name"], _entry[key]["value"]
                )

                self.ui.sample_textEdit.setHtml(text)

        if infos_dict[DataType.ob] is None:
            self.ui.toolBox.setItemEnabled(1, False)
        else:
            self.ui.toolBox.setItemEnabled(1, True)
            _entry = infos_dict[DataType.ob]
            text = ""
            for key in _entry:
                text += "<b>{}</b>: {}<br/>".format(
                    _entry[key]["name"], _entry[key]["value"]
                )

                self.ui.ob_textEdit.setHtml(text)

        if infos_dict[DataType.normalized] is None:
            self.ui.toolBox.setItemEnabled(2, False)
        else:
            self.ui.toolBox.setItemEnabled(2, True)
            _entry = infos_dict[DataType.normalized]
            text = ""
            for key in _entry:
                text += "<b>{}</b>: {}<br/>".format(
                    _entry[key]["name"], _entry[key]["value"]
                )

                self.ui.normalized_textEdit.setHtml(text)
