try:
    import PyQt4
    import PyQt4.QtCore as QtCore
    import PyQt4.QtGui as QtGui
except:
    import PyQt5
    import PyQt5.QtCore as QtCore
    import PyQt5.QtGui as QtGui

import numpy as np
import pyqtgraph as pg
from pyqtgraph.dockarea import *

from ibeatles.utilities.colors import pen_color
from ibeatles.step2.plot import Step2Plot
from ibeatles.step2.normalization import Normalization


class CustomAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return ['{:.4f}'.format(1./i) for i in values]
                
                
class Step2GuiHandler(object):
    
    col_width = [70, 50, 50, 50, 50]
    
    def __init__(self, parent=None):
        self.parent = parent

    def update_widgets(self):
        o_step2_plot = Step2Plot(parent = self.parent)
        o_step2_plot.display_image()
        #o_step2_plot.display_counts_vs_file()
        o_normalization = Normalization(parent=self.parent)
        o_normalization.run()
        o_step2_plot.init_roi_table()
        self.check_run_normalization_button()
        
    def init_table(self):
        for _index, _width in enumerate(self.col_width):
            self.parent.ui.normalization_tableWidget.setColumnWidth(_index, _width)

    def init_pyqtgraph(self):
        area = DockArea()
        area.setVisible(True)
        d1 = Dock("Sample", size=(200, 300))
        d2 = Dock("STEP1: Background normalization", size=(200, 100))
        #d3 = Dock("STEP2: Working Range Selection", size=(200, 100))
        
        area.addDock(d1, 'top')
        #area.addDock(d3, 'bottom')
        area.addDock(d2, 'bottom')
        #area.moveDock(d2, 'above', d3)
        
        preview_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)
        
        vertical_layout = QtGui.QVBoxLayout()
        #preview_widget.setLayout(vertical_layout)        
        
        # image view
        image_view = pg.ImageView()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        roi = pg.ROI([0,0],[20,20], pen=pen_color['0'])
        roi.addScaleHandle([1,1],[0,0])
        image_view.addItem(roi)
        roi.sigRegionChangeFinished.connect(self.parent.normalization_manual_roi_changed)

        #vertical_layout.addWidget(image_view)
        #top_right_widget = QtGui.QWidget()
        d1.addWidget(image_view)

        # bragg edge plot
        bragg_edge_plot = pg.PlotWidget()
        bragg_edge_plot.plot()

        # bragg_edge_plot.setLabel("top", "")
        p1 = bragg_edge_plot.plotItem
        p1.layout.removeItem(p1.getAxis('top'))
        caxis = CustomAxis(orientation='top', parent=p1)
        caxis.setLabel('')
        caxis.linkToView(p1.vb)
        p1.layout.addItem(caxis, 1, 1)
    
        d2.addWidget(bragg_edge_plot)
    
        #button = QtGui.QPushButton()
        #button.setText("Run OB Normalization")
        #self.parent.connect(button, QtCore.SIGNAL("clicked()"), self.parent.run_ob_normalization)
        ##space
        #spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        
        #hori_layout = QtGui.QHBoxLayout()
        #hori_layout.addItem(spacerItem1)
        #hori_layout.addWidget(button)
        
        #bottom_widget = QtGui.QWidget()
        #bottom_widget.setLayout(hori_layout)
        #d2.addWidget(bottom_widget)
    
        ## normalization profile
        #normalized_profile_plot = pg.PlotWidget()
        #normalized_profile_plot.plot()

        #p1 = normalized_profile_plot.plotItem
        #p1.layout.removeItem(p1.getAxis('top'))
        #caxis = CustomAxis(orientation='top', parent=p1)
        #caxis.setLabel('')
        #caxis.linkToView(p1.vb)
        #p1.layout.addItem(caxis, 1, 1)
    
        #d3.addWidget(normalized_profile_plot)        

        ##space
        #spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        
        #label = QtGui.QLabel()
        #label.setText("Scaling Coefficient:")
        
        #text_field = QtGui.QLineEdit()
        #self.parent.connect(text_field, QtCore.SIGNAL("returnPressed()"), self.parent.scaling_coefficient_validated)
        #text_field.setMaximumSize(QtCore.QSize(50, 50))

        #hori_layout = QtGui.QHBoxLayout()
        #hori_layout.addItem(spacerItem1)
        #hori_layout.addWidget(label)
        #hori_layout.addWidget(text_field)
        #bottom_widget = QtGui.QWidget()
        #bottom_widget.setLayout(hori_layout)
        
        #d3.addWidget(bottom_widget)
    
        vertical_layout.addWidget(area)
        self.parent.ui.normalization_left_widget.setLayout(vertical_layout)

        self.parent.step2_ui['area'] = area
        self.parent.step2_ui['image_view'] = image_view
        self.parent.list_roi_id['normalization'] = [roi]
        self.parent.step2_ui['bragg_edge_plot'] = bragg_edge_plot
        #self.parent.step2_ui['normalized_profile_plot'] = normalized_profile_plot
        self.parent.step2_ui['caxis'] = caxis

    def check_add_remove_roi_buttons(self):
        nbr_row = self.parent.ui.normalization_tableWidget.rowCount()
        if nbr_row == 0:
            _status_remove = False
        else:
            _status_remove = True
            
        self.parent.ui.normalization_remove_roi_button.setEnabled(_status_remove)
        
    def check_run_normalization_button(self):
        nbr_row = self.parent.ui.normalization_tableWidget.rowCount()
        ob = self.parent.data_files['ob']
        data = self.parent.data_files['sample']
        if data == []:
            _status = False
        else:
            if (nbr_row == 0) and (ob == []):
                _status = False
            else:
                _status = True
        self.parent.ui.normalization_button.setChecked(_status)
        
        
        