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
    line_view = None
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

    def roi_changed_finished(self):
        self.roi_selection_widgets_modified()        
        
    def roi_changed(self):

        if self.line_view:
            self.image_view.removeItem(self.line_view)
            self.line_view = None
        
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
        roi.sigRegionChangeFinished.connect(self.roi_changed_finished)
        self.widgets_ui['roi'] = roi
        
        line_view = pg.GraphItem()
        image_view.addItem(line_view)
        self.line_view = line_view

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

    def roi_selection_widgets_modified(self):
        
        if self.line_view:
            self.image_view.removeItem(self.line_view)
            self.line_view = None
            
        if self.parent.fitting_ui:
            if self.parent.fitting_ui.line_view:
                self.parent.fitting_ui.image_view.removeItem(self.parent.fitting_ui.line_view)
                self.parent.fitting_ui.line_view = None
                    
        x0 = np.int(str(self.ui.selection_x0.text()))
        y0 = np.int(str(self.ui.selection_y0.text()))
        width = np.int(str(self.ui.selection_width.text()))
        height = np.int(str(self.ui.selection_height.text()))
        bin_size = np.int(str(self.ui.pixel_bin_size.text()))
        
        self.widgets_ui['roi'].setPos([x0, y0], update=False, finish=False)
        self.widgets_ui['roi'].setSize([width, height], update=False, finish=False)
        
        pos_adj_dict = self.calculate_matrix_of_pixel_bins(bin_size=bin_size,
                                                           x0=x0,
                                                           y0=y0,
                                                           width=width,
                                                           height=height)
        
        pos = pos_adj_dict['pos']
        adj = pos_adj_dict['adj']
        
        line_color = (255,0,0,255,1)
        lines = np.array([line_color for n in np.arange(len(pos))],
                        dtype=[('red',np.ubyte),('green',np.ubyte),
                               ('blue',np.ubyte),('alpha',np.ubyte),
                               ('width',float)]) 

        line_view_binning = pg.GraphItem()
        self.image_view.addItem(line_view_binning)
        self.line_view = line_view_binning
        self.line_view.setData(pos=pos, 
                               adj=adj,
                               pen=lines,
                               symbol=None,
                               pxMode=False)
        
        if self.parent.fitting_ui:
            
            line_view_fitting = pg.GraphItem()
            self.parent.fitting_ui.image_view.addItem(line_view_fitting)
            self.parent.fitting_ui.line_view = line_view_fitting
            self.parent.fitting_ui.line_view.setData(pos=pos, 
                                                     adj=adj,
                                                     pen=lines,
                                                     symbol=None,
                                                     pxMode=False)
            
                
    def  calculate_matrix_of_pixel_bins(self, bin_size=2,
                                            x0=0,
                                            y0=0,
                                            width=20,
                                            height=20):
        
        pos_adj_dict = {}

        nbr_height_bins = np.float(height) / np.float(bin_size)
        real_height = y0 + np.int(nbr_height_bins) * np.int(bin_size)
        
        nbr_width_bins = np.float(width) / np.float(bin_size)
        read_width = x0 + np.int(nbr_width_bins) * np.int(bin_size)
        
        # pos (each matrix is one side of the lines)
        pos = []
        adj = []

        # vertical lines
        x = x0
        index = 0
        while (x <= x0 + width):
            one_edge = [x, y0]
            other_edge = [x, real_height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index+1])
            x += bin_size
            index += 2
            
        # horizontal lines
        y = y0
        while (y <= y0 + height):
            one_edge = [x0, y]
            other_edge = [read_width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index+1])
            y += bin_size
            index += 2

        pos_adj_dict['pos'] = np.array(pos)
        pos_adj_dict['adj'] = np.array(adj)
        
        return pos_adj_dict
       
    def mouse_moved_in_image(self, event):
        pass
    
        if self.data == []:
            return

        x = np.int(event.x())
        y = np.int(event.y())
        
        self.widgets_ui['x_value'].setText("{}".format(x))
        self.widgets_ui['y_value'].setText("{}".format(y))
        
    def closeEvent(self, event=None):
        self.parent.binning_ui = None
