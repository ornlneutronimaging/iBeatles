from qtpy.QtGui import QGuiApplication
from qtpy.QtWidgets import QApplication


class StatusMessageStatus:
    ready = "QStatusBar{padding-left:8px;color:green;font-weight:normal;}"
    working = "QStatusBar{padding-left:8px;color:blue;font-weight:normal;}"
    error = "QStatusBar{padding-left:8px;;color:red;font-weight:bold;}"
    warning = "QStatusBar{padding-left:8px;color:purple;font-weight:normal;}"


def show_status_message(
    parent=None, message="", status=StatusMessageStatus.ready, duration_s=None
):
    parent.ui.statusbar.setStyleSheet(status)
    if duration_s:
        parent.ui.statusbar.showMessage(message, duration_s * 1000)
    else:
        parent.ui.statusbar.showMessage(message)
    QGuiApplication.processEvents()
    parent.ui.repaint()
    QApplication.processEvents()
