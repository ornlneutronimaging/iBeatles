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
import scipy

from ibeatles.interfaces.ui_rotateImages import Ui_MainWindow as UiMainWindow
    
    
class RotateImages(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.rotate_ui == None:
            rotate_ui = RotateImagesWindow(parent=parent)
            rotate_ui.show()
            rotate_ui.display_rotated_images()
            self.parent.rotate_ui = rotate_ui
        else:
            self.parent.rotate_ui.setFocus()
            self.parent.rotate_ui.activateWindow()
        
        
class RotateImagesWindow(QMainWindow):
    
    grid_size = 100 # pixels
    
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
        
        self.ui.line_view = None

    def display_rotated_images(self):
        data = np.array(self.parent.data_metadata['normalized']['data_live_selection'])
        rotation_value = np.float(str(self.ui.rotation_value.text()))
        
        rotated_data = scipy.ndimage.interpolation.rotate(data, rotation_value)
        self.ui.image_view.setImage(rotated_data)
        
        self.display_grid(data = rotated_data)
        
    def display_grid(self, data=None):
        [height, width] = np.shape(data)
        
        pos = []
        adj = []
        
        # vertical lines
        x = self.grid_size
        index = 0
        while (x <= width):
            one_edge = [x, 0]
            other_edge = [x, height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index+1])
            x += self.grid_size
            index += 2
            
        # horizontal lines
        y = self.grid_size
        while(y <= height):
            one_edge = [0, y]
            other_edge = [width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index+1])
            y += self.grid_size
            index += 2
            
        pos = np.array(pos)
        adj = np.array(adj)
        
        line_color = (0, 255, 0, 255, 0.5)
        lines = np.array([line_color for n in np.arange(len(pos))],
                             dtype=[('red',np.ubyte),('green',np.ubyte),
                                        ('blue',np.ubyte),('alpha',np.ubyte),
                                       ('width',float)]) 

        # remove old line_view
        if self.ui.line_view:
            self.ui.image_view.removeItem(self.ui.line_view)
        line_view = pg.GraphItem()
        self.ui.image_view.addItem(line_view)
        line_view.setData(pos=pos, 
                          adj=adj,
                          pen=lines,
                          symbol=None,
                          pxMode=False) 
        self.ui.line_view = line_view

        

    def save_and_use_clicked(self):
        pass
        
    
    def cancel_clicked(self):
        self.closeEvent(self)
        
    def closeEvent(self, event=None):
        self.parent.rotate_ui.close()
        self.parent.rotate_ui = None
        