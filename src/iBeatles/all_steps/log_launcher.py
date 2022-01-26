from qtpy.QtWidgets import QMainWindow, QDialog
import os
from qtpy.QtGui import QIcon
from qtpy import QtGui
import logging

from .. import load_ui
from ..utilities.get import Get
from ..utilities.file_handler import read_ascii, write_ascii
from .. import refresh_image, settings_image


class LogLauncher:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.log_id is None:
            log_id = Log(parent=self.parent)
            log_id.show()
            self.parent.log_id = log_id
        else:
            self.parent.log_id.activateWindow()
            self.parent.log_id.setFocus()


class Log(QMainWindow):

    def __init__(self, parent=None):
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'log.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Log")
        self.ui.log_text.setReadOnly(True)

        refresh_icon = QIcon(refresh_image)
        self.ui.refresh_pushButton.setIcon(refresh_icon)

        settings_icon = QIcon(settings_image)
        self.ui.settings_pushButton.setIcon(settings_icon)

        o_get = Get(parent=self.parent)
        self.log_file_name = o_get.get_log_file_name()
        self.loading_logging_file()

        # jump to end of file
        self.ui.log_text.moveCursor(QtGui.QTextCursor.End)

    def closeEvent(self, c):
        self.parent.log_id = None

    def loading_logging_file(self):
        try:
            log_text = read_ascii(self.log_file_name)
            self.ui.log_text.setPlainText(log_text)
            self.ui.log_text.moveCursor(QtGui.QTextCursor.End)
        except FileNotFoundError:
            self.ui.log_text.setPlainText("")

    def clear_clicked(self):
        if os.path.exists(self.log_file_name):
            write_ascii(text="", filename=self.log_file_name)
            logging.info("log file has been cleared by user")
        self.loading_logging_file()

    def check_log_size(self):
        log_buffer_size = self.parent.session_dict['log buffer size']
        # FIXME

    def launch_settings(self):
        log_id = LogSettings(parent=self,
                             grand_parent=self.parent)
        log_id.show()


class LogSettings(QDialog):

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        QDialog.__init__(self, parent=self.parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'log_settings.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Log")
        self.init_widgets()

    def init_widgets(self):
        log_buffer_size = self.grand_parent.session_dict['log buffer size']
        self.ui.buffer_size_spinBox.setValue(log_buffer_size)

    def accept(self):
        self.grand_parent.session_dict['log buffer size'] = self.ui.buffer_size_spinBox.value()
        self.parent.check_log_size()
        self.close()
