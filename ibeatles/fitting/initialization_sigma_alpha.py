try:
    import PyQt4
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QMainWindow
except:
    import PyQt5
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QMainWindow
import numpy as np

from ibeatles.interfaces.ui_initSigmaAlpha import Ui_MainWindow as UiMainWindow


class InitializationSigmaAlpha(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        init_sigma_alpha_window = InitializeWindow(parent=parent)
        init_sigma_alpha_window.show()
        
class InitializeWindow(QMainWindow):
    
    def __init__(self, parent=None):

        self.parent = parent
        QMainWindow.__init__(self, parent=parent.fitting_ui)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.init_widgets()
            
    def init_widgets(self):
        self.ui.alpha_error.setVisible(False)
        self.ui.sigma_error.setVisible(False)
             
    def ok_button_clicked(self):
        if self.variable_correctly_initialized():
            self.parent.fitting_ui.sigma_alpha_initialized = True
            self.parent.fitting_ui.initialize_all_parameters_step2()
            self.close()
    
    def cancel_button_clicked(self):
        self.parent.fitting_ui.sigma_alpha_initialized = False
        self.close()

    def variable_correctly_initialized(self):
        _alpha = str(self.ui.sigma_lineEdit.text())
        _sigma = str(self.ui.alpha_lineEdit.text())
        
        _sigma_status = True
        try:
            _float_alpha = np.float(_alpha)
        except:
            _sigma_status = False
            
        _alpha_status = True
        try:
            _float_sigma = np.float(_sigma)
        except:
            _alpha_status = False
        
        self.ui.sigma_error.setVisible(not _sigma_status)
        self.ui.alpha_error.setVisible(not _alpha_status)
        
        if _sigma_status and _alpha_status:
            return True
        else:
            return False