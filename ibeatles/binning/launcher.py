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
    
from ibeatles.interfaces.ui_binningWindow import Ui_MainWindow as UiMainWindow
from ibeatles.utilities.colors import pen_color

from ibeatles.binning.binning_handler import BinningHandler


class BinningLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.binning_ui == None:
            binning_window = BinningWindow(parent=parent)
            binning_window.show()
            self.parent.binning_ui = binning_window
            o_binning = BinningHandler(parent=self.parent)
            o_binning.display_image()
        else:
            self.parent.binning_ui.setFocus()
            self.parent.binning_ui.activateWindow()

class BinningWindow(QMainWindow):        
    
    image_view = None
    data = []
    widgets_ui = {'x_value': None,
                  'y_value': None,
                  'intensity_value': None,
                  'roi': None}

    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("4. Binning")
        
        self.init_pyqtgraph()        
                
    def roi_changed(self):
        roi = self.widgets_ui['roi']
        region = roi.getArraySlice(self.data, self.image_view.imageItem)
        
        x0 = region[0][0].start
        x1 = region[0][0].stop-1
        y0 = region[0][1].start
        y1 = region[0][1].stop-1
        
        width = np.abs(x0-x1)
        height = np.abs(y0-y1)
        
        self.ui.selection_x0.setText("{}".format(x0))
        self.ui.selection_y0.setText("{}".format(y0))
        self.ui.selection_width.setText("{}".format(width))
        self.ui.selection_height.setText("{}".format(height))
        
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
        self.widgets_ui['roi'] = roi

        # bottom x, y and counts labels
        hori_layout = QtGui.QHBoxLayout()
        spacer1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        x_label = QtGui.QLabel("X:")
        x_value = QtGui.QLabel("N/A")
        x_value.setFixedWidth(50)
        self.widgets_ui['x_value'] = x_value
        spacer2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        y_label = QtGui.QLabel("Y:")
        y_value = QtGui.QLabel("N/A")
        y_value.setFixedWidth(50)
        self.widgets_ui['y_value'] = y_value
        spacer3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        intensity_label = QtGui.QLabel("Counts:")
        intensity_value = QtGui.QLabel("N/A")
        self.widgets_ui['intensity_value'] = intensity_value
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
        image_view.scene.sigMouseMoved.connect(self.mouse_moved_in_image)

        self.image_view = image_view
        
    def closeEvent(self, event=None):
        self.parent.binning_ui = None

    def mouse_moved_in_image(self, event):
        pass
    
        if self.data == []:
            return

        x = np.int(event.x())
        y = np.int(event.y())
        
        self.widgets_ui['x_value'].setText("{}".format(x))
        self.widgets_ui['y_value'].setText("{}".format(y))
        
