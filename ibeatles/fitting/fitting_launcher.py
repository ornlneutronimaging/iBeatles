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

from ibeatles.fitting.fitting_handler import FittingHandler


class FittingLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.fitting_ui == None:
            fitting_window = FittingWindow(parent=parent)
            fitting_window.show()
            self.parent.fitting_ui = fitting_window
            o_fitting = FittingHandler(parent=self.parent)
            o_fitting.display_image()
            o_fitting.display_roi()
        else:
            self.parent.fitting_ui.setFocus()
            self.parent.fitting_ui.activateWindow()
            
class FittingWindow(QMainWindow):        
    
    data = []
    
    image_view = None
    bragg_edge_plot = None
    line_view = None

    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("5. Fitting")

        self.init_pyqtgraph()
        
    def init_pyqtgraph(self):

        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Image Preview", size=(200, 300))
        d2 = Dock("Bragg Edge", size=(200, 100))
    
        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')
    
        preview_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True) # this improve display
    
        vertical_layout = QtGui.QVBoxLayout()
        preview_widget.setLayout(vertical_layout)
    
        # image view (top plot)
        image_view = pg.ImageView()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        self.image_view = image_view
       
        top_widget = QtGui.QWidget()
        vertical = QtGui.QVBoxLayout()
        vertical.addWidget(image_view)
        top_widget.setLayout(vertical)
        d1.addWidget(top_widget)
    
        # bragg edge plot (bottom plot)
        bragg_edge_plot = pg.PlotWidget(title='')
        bragg_edge_plot.plot()
        self.bragg_edge_plot = bragg_edge_plot
    
        d2.addWidget(bragg_edge_plot)
    
        vertical_layout.addWidget(area)
        self.ui.widget.setLayout(vertical_layout)        
        
    def closeEvent(self, event=None):
        self.parent.fitting_ui = None
    