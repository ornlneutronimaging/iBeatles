try:
    import PyQt4
    import PyQt4.QtGui as QtGui
    from PyQt4.QtGui import QMainWindow
except:
    import PyQt5
    import PyQt5.QtGui as QtGui
    from PyQt5.QtWidgets import QMainWindow

from pyqtgraph.dockarea import *
import pyqtgraph as pg
import numpy as np
    
from ibeatles.interfaces.ui_fittingWindow import Ui_MainWindow as UiMainWindow
from ibeatles.utilities.colors import pen_color


class FittingLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.binning_ui == None:
            fitting_window = FittingWindow(parent=parent)
            fitting_window.show()
            self.parent.fitting_ui = fitting_window
        else:
            self.parent.fitting_ui.setFocus()
            self.parent.fitting_ui.activateWindow()
            
class FittingWindow(QMainWindow):        
    
    data = []

    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("5. Fitting")
