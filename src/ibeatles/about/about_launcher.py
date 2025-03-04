from qtpy.QtWidgets import QDialog

from src.ibeatles import load_ui
from src.ibeatles._version import __version__


class AboutLauncher(QDialog):
    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)

        self.ui = load_ui("about.ui", baseinstance=self)
        self.setWindowTitle("About")
        self.ui.application_version_label.setText(f"iBeatles: {__version__}")

        list_version = []
        try:
            import numpy
        except ImportError:
            list_version.append("numpy: unknown")
        else:
            list_version.append(f"numpy: {numpy.__version__}")

        try:
            import matplotlib
        except ImportError:
            list_version.append("matplotlib: unknown")
        else:
            list_version.append(f"matplotlib: {matplotlib.__version__}")

        try:
            import pyqtgraph
        except ImportError:
            list_version.append("pyqtgraph: unknown")
        else:
            list_version.append(f"pyqtgraph: {pyqtgraph.__version__}")

        try:
            import pandas
        except ImportError:
            list_version.append("pandas: unknown")
        else:
            list_version.append(f"pandas: {pandas.__version__}")

        try:
            import NeuNorm
        except ImportError:
            list_version.append("NeuNorm: unknown")
        else:
            list_version.append(f"NeuNorm: {NeuNorm.__version__}")

        try:
            import qtpy
        except ImportError:
            list_version.append("qtpy: unknown")
        else:
            list_version.append(f"qtpy: {qtpy.__version__}")

        try:
            import NeuNorm
        except ImportError:
            list_version.append("NeuNorm: unknown")
        else:
            list_version.append(f"NeuNorm: {NeuNorm.__version__}")

        try:
            import qtpy
        except ImportError:
            list_version.append("qtpy: unknown")
        else:
            list_version.append(f"qtpy: {qtpy.__version__}")

        formatted_list_version = "\n".join(list_version)
        self.ui.librairies_versions_textEdit.setText(formatted_list_version)
