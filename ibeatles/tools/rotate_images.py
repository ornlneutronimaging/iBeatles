try:
    import PyQt4
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QMainWindow
    from PyQt4.QtGui import QApplication         
except:
    import PyQt5
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QApplication
    
from pyqtgraph.dockarea import *
import pyqtgraph as pg
import numpy as np

from ibeatles.interfaces.ui_rotateImages import Ui_MainWindow as UiMainWindow
    
    
class RotateImages(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.rotate_ui == None:
            rotate_ui = RotateImagesWindow(parent=parent)
            rotate_ui.show()
            self.parent.rotate_ui = rotate_ui
        else:
            self.parent.rotate_ui.setFocus()
            self.parent.rotate_ui.activateWindow()
        
        
class RotateImagesWindow(QMainWindow):
    
    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        
        self.init_pyqtgraph()
        
    def init_pyqtgraph(self):

        self.ui.image_view = pg.ImageView()
        self.ui.image_view.ui.roiBtn.hide()
        self.ui.image_view.ui.menuBtn.hide()
        
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(self.ui.image_view)
        self.ui.widget.setLayout(vertical_layout)
        
        
        
        
        
        
        
        
    
    def cancel_clicked(self):
        self.closeEvent(self)
        
    def closeEvent(self, event=None):
        self.parent.rotate_ui.close()
        self.parent.rotate_ui = None
        