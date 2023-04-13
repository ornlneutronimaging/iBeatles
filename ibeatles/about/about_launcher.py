from qtpy.QtWidgets import QDialog
import os
import re

from ibeatles import load_ui


class AboutLauncher(QDialog):

    def __init__(self, parent=None):

        self.parent = parent
        QDialog.__init__(self, parent=parent)

        self.ui = load_ui('about.ui', baseinstance=self)
        self.setWindowTitle("About")

        root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        setup_py_file = os.path.join(root, "setup.py")
        with open(setup_py_file, 'r') as setup_file_handler:
            content = setup_file_handler.read()
        content_formatted = content.split("\n")

        _version = "unknown"
        for _line in content_formatted:
            if _line.strip().startswith("version"):
                _tag, _version = _line.strip().split("=")
                m = re.match('"(\d*.\d*.\d*)",', _version)
                if m:
                    _version = m.group(1)
                break
        self.ui.application_version_label.setText(f"iBeatles: {_version}")

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