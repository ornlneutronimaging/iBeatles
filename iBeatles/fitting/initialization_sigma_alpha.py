from qtpy.QtWidgets import QMainWindow
import numpy as np

from .. import load_ui


class InitializationSigmaAlpha(object):

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

        init_sigma_alpha_window = InitializeWindow(parent=parent, grand_parent=grand_parent)
        init_sigma_alpha_window.show()


class InitializeWindow(QMainWindow):

    def __init__(self, parent=None, grand_parent=None):

        self.parent = parent
        self.grand_parent = grand_parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_initSigmaAlpha.ui', baseinstance=self)
        self.init_widgets()

    def init_widgets(self):
        self.ui.alpha_error.setVisible(False)
        self.ui.sigma_error.setVisible(False)

    def ok_button_clicked(self):
        if self.variable_correctly_initialized():
            self.parent.sigma_alpha_initialized = True
            self.parent.initialize_all_parameters_step2()
            self.parent.is_ready_to_fit = True
            self.parent.check_state_of_step4_button()
            self.close()

    def cancel_button_clicked(self):
        self.parent.sigma_alpha_initialized = False
        self.close()

    def variable_correctly_initialized(self):
        _alpha = str(self.ui.alpha_lineEdit.text())
        _sigma = str(self.ui.sigma_lineEdit.text())

        _sigma_status = True
        try:
            _sigma = np.float(_sigma)
        except ValueError:
            _sigma = np.NaN
            _sigma_status = False

        _alpha_status = True
        try:
            _alpha = np.float(_alpha)
        except ValueError:
            _alpha = np.NaN
            _alpha_status = False

        initialization_table = self.parent.initialization_table
        initialization_table['sigma'] = _sigma
        initialization_table['alpha'] = _alpha
        self.grand_parent.initialization_table = initialization_table

        self.ui.sigma_error.setVisible(not _sigma_status)
        self.ui.alpha_error.setVisible(not _alpha_status)

        if _sigma_status and _alpha_status:
            return True
        else:
            return False
