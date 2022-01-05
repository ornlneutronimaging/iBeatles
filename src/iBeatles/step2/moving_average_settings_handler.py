from qtpy.QtWidgets import QDialog
import os

from .. import load_ui


class MovingAverageSettingsHandler(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'moving_average_settings.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Load previous session?")
        self.ui.pushButton.setFocus(True)

    def ok_clicked(self):
        self.close()
