from qtpy.QtWidgets import QDialog
import os

from src.ibeatles import load_ui
from src.ibeatles.utilities.get import Get

from src.ibeatles.session.load_previous_session_launcher_multiple_choice import LoadPreviousSessionLauncherMultipleChoice
from src.ibeatles.session.session_handler import SessionHandler
from src.ibeatles.session import SessionSubKeys


class LoadPreviousSessionLauncher(QDialog):

    def __init__(self, parent=None, config=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'ui_load_previous_session.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Load previous session?")
        self.ui.pushButton.setFocus(True)

    def yes_clicked(self):
        self.close()
        o_session = SessionHandler(parent=self.parent)
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.get_automatic_config_file_name()
        o_session.load_from_file(config_file_name=full_config_file_name)

        if not o_session.load_successful:
            self.no_clicked()
            return

        list_tabs_to_load = o_session.get_tabs_to_load()
        if len(list_tabs_to_load) < 2:
            o_session.load_to_ui(tabs_to_load=list_tabs_to_load)
            self.parent.loading_from_config = False
        else:
            load_session_ui = LoadPreviousSessionLauncherMultipleChoice(parent=self.parent,
                                                                        list_tabs_to_load=list_tabs_to_load)
            load_session_ui.show()
        self.parent.check_log_file_size()

    def no_clicked(self):
        self.parent.session_dict = SessionHandler.session_dict
        self.close()
        self.parent.check_log_file_size()

    def reject(self):
        self.no_clicked()

    def closeEvent(self, event):
        self.close()
