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
    
    line_view_fitting = None #roi selected in binning window
    all_bins_button = None
    indi_bins_button = None

    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("5. Fitting")

        self.init_pyqtgraph()
        self.init_labels()
        self.init_widgets()
        
    def init_widgets(self):
        '''
        such as material h,k,l list according to material selected in normalized tab
        '''
        hkl_list = self.parent.selected_element_hkl_array
        str_hkl_list = ["{},{},{}".format(_hkl[0], _hkl[1], _hkl[2]) for _hkl in hkl_list]
        self.ui.hkl_list_ui.addItems(str_hkl_list)
        
    def init_labels(self):
        self.ui.lambda_min_label.setText(u"\u03BB<sub>min</sub>")
        self.ui.lambda_max_label.setText(u"\u03BB<sub>max</sub>")
        self.ui.lambda_min_units.setText(u"\u212B")
        self.ui.lambda_max_units.setText(u"\u212B")
        self.ui.bragg_edge_units.setText(u"\u212B")
        
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

        # bin transparency
        transparency_layout = QtGui.QHBoxLayout()
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        transparency_layout.addItem(spacer)        
        label = QtGui.QLabel("Bin Transparency")
        transparency_layout.addWidget(label)
        slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        slider.setMaximum(100)
        slider.setMinimum(0)
        slider.setValue(50)
        slider.valueChanged.connect(self.slider_changed)
        self.slider = slider
        transparency_layout.addWidget(slider)
        bottom_widget = QtGui.QWidget()
        bottom_widget.setLayout(transparency_layout)

        top_widget.setLayout(vertical)
        d1.addWidget(top_widget)
        d1.addWidget(bottom_widget)
    
        # bragg edge plot (bottom plot)
        bragg_edge_plot = pg.PlotWidget(title='')
        bragg_edge_plot.plot()
        self.bragg_edge_plot = bragg_edge_plot
    
        # plot all or individual bins
        buttons_layout = QtGui.QHBoxLayout()
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        buttons_layout.addItem(spacer)
        label = QtGui.QLabel("Plots Bins")
        buttons_layout.addWidget(label)
        
        # all bins button
        all_button = QtGui.QRadioButton()
        all_button.setText("All")
        all_button.setChecked(True)
        all_button.pressed.connect(self.plots_bins_all_pressed)
        self.all_bins_button = all_button
        
        # indi bin button
        buttons_layout.addWidget(all_button)
        indi_button = QtGui.QRadioButton()
        indi_button.setText("Individual")
        indi_button.setChecked(False)
        indi_button.pressed.connect(self.plots_bins_individual_pressed)
        self.indi_bins_button = indi_button

        buttons_layout.addWidget(indi_button)
        bottom_widget = QtGui.QWidget()
        bottom_widget.setLayout(buttons_layout)
    
        d2.addWidget(bragg_edge_plot)
        d2.addWidget(bottom_widget)
    
        vertical_layout.addWidget(area)
        self.ui.widget.setLayout(vertical_layout)        
        
    def plots_bins_all_pressed(self):
        print("all pressed")
        
    def plots_bins_individual_pressed(self):
        print("indi pressed")
        
    def slider_changed(self):
        o_fitting_handler = FittingHandler(parent=self.parent)
        o_fitting_handler.display_roi()
        
    def closeEvent(self, event=None):
        self.parent.fitting_ui = None
    