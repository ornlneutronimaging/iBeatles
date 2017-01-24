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
    
        #add file_index, TOF, Lambda x-axis buttons
        hori_layout = QtGui.QHBoxLayout()
        button_widgets = QtGui.QWidget()
        button_widgets.setLayout(hori_layout)
    
        #file index
        file_index_button = QtGui.QRadioButton()
        file_index_button.setText("File Index")
        file_index_button.setChecked(True)
        self.parent.connect(file_index_button, QtCore.SIGNAL("clicked()"), 
                            self.parent.step2_file_index_radio_button_clicked)
    
        #tof
        tof_button = QtGui.QRadioButton()
        tof_button.setText("TOF")
        self.parent.connect(tof_button, QtCore.SIGNAL("clicked()"), 
                            self.parent.step2_tof_radio_button_clicked)
    
        #lambda
        lambda_button = QtGui.QRadioButton()
        lambda_button.setText(u"\u03BB")
        self.parent.connect(lambda_button, QtCore.SIGNAL("clicked()"), 
                            self.parent.step2_lambda_radio_button_clicked)
        
        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        hori_layout.addItem(spacer)
        hori_layout.addWidget(file_index_button)
        hori_layout.addWidget(tof_button)
        hori_layout.addWidget(lambda_button)
        hori_layout.addItem(spacer)
    
        d2.addWidget(bragg_edge_plot)
        d2.addWidget(button_widgets)
    
        vertical_layout.addWidget(area)
        self.parent.ui.normalization_left_widget.setLayout(vertical_layout)

        self.parent.step2_ui['area'] = area
        self.parent.step2_ui['image_view'] = image_view
        self.parent.list_roi_id['normalization'] = [roi]
        self.parent.step2_ui['bragg_edge_plot'] = bragg_edge_plot
        #self.parent.step2_ui['normalized_profile_plot'] = normalized_profile_plot
        self.parent.step2_ui['caxis'] = caxis
        self.parent.step2_ui['xaxis_file_index'] = file_index_button
        self.parent.step2_ui['xaxis_lambda'] = lambda_button
        self.parent.step2_ui['xaxis_tof'] = tof_button

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
        
        
        