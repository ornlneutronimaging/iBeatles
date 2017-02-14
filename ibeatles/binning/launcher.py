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
    
from ibeatles.interfaces.ui_binningWindow import Ui_MainWindow as UiMainWindow
from ibeatles.utilities.colors import pen_color


class BinningLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.binning_ui == None:
            binning_window = BinningWindow(parent=parent)
            binning_window.show()
            self.parent.binning_ui = binning_window
        else:
            self.parent.binning_ui.setFocus()
            self.parent.binning_ui.activateWindow()

class BinningWindow(QMainWindow):        
    
    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        
        self.init_pyqtgraph()
        
    def closeEvent(self, event=None):
        self.parent.binning_ui = None
        
    def normalized_file_selection_updated(self):
        print("normalized file selection changed")
        
    def roi_changed(self):
        print("roi changed")
    
    def init_pyqtgraph(self):

        pg.setConfigOptions(antialias=True)
        
        # image view that will display the image and the ROI on top of it + bin regions
        image_view = pg.ImageView()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        roi = pg.ROI([0,0], [20, 20], pen=pen_color['0'], scaleSnap=True)
        roi.addScaleHandle([1,1], [0,0])
        image_view.addItem(roi)
        roi.sigRegionChanged.connect(self.roi_changed)

        # bottom x, y and counts labels
        hori_layout = QtGui.QHBoxLayout()
        spacer1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        x_label = QtGui.QLabel("X:")
        x_value = QtGui.QLabel("N/A")
        x_value.setFixedWidth(50)
        spacer2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        y_label = QtGui.QLabel("Y:")
        y_value = QtGui.QLabel("N/A")
        y_value.setFixedWidth(50)
        spacer3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        intensity_label = QtGui.QLabel("Counts:")
        intensity_value = QtGui.QLabel("N/A")
        intensity_value.setFixedWidth(50)

        hori_layout.addItem(spacer1)
        hori_layout.addWidget(x_label)
        hori_layout.addWidget(x_value)
        hori_layout.addItem(spacer2)
        hori_layout.addWidget(y_label)
        hori_layout.addWidget(y_value)
        hori_layout.addItem(spacer3)
        hori_layout.addWidget(intensity_label)
        hori_layout.addWidget(intensity_value)
        hori_widget = QtGui.QWidget()
        hori_widget.setLayout(hori_layout)
        
        # put everything back into the main GUI
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(image_view)
        vertical_layout.addWidget(hori_widget)
        
        self.ui.left_widget.setLayout(vertical_layout)
