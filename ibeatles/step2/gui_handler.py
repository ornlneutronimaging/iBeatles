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
        o_step2_plot.display_counts_vs_file()
        o_step2_plot.init_roi_table()
        
    def init_table(self):
        for _index, _width in enumerate(self.col_width):
            self.parent.ui.normalization_tableWidget.setColumnWidth(_index, _width)

    def init_pyqtgraph(self):
        area = DockArea()
        area.setVisible(False)
        d1 = Dock("Sample", size=(200, 300))
        d2 = Dock("Profile", size=(200, 100))
        
        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')
        
        preview_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)
        
        vertical_layout = QtGui.QVBoxLayout()
        #preview_widget.setLayout(vertical_layout)        
        
        # image view
        image_view = pg.ImageView()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        roi = pg.ROI([0,0],[1,1], pen=pen_color['0'])
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
    
        vertical_layout.addWidget(area)
        self.parent.ui.normalization_left_widget.setLayout(vertical_layout)

        self.parent.step2_ui['area'] = area
        self.parent.step2_ui['image_view'] = image_view
        self.parent.list_roi_id['normalization'] = [roi]
        self.parent.step2_ui['bragg_edge_plot'] = bragg_edge_plot
        self.parent.step2_ui['caxis'] = caxis

    def check_add_remove_roi_buttons(self):
        nbr_row = self.parent.ui.normalization_tableWidget.rowCount()
        if nbr_row == 0:
            _status_remove = False
        else:
            _status_remove = True
            
        self.parent.ui.normalization_remove_roi_button.setEnabled(_status_remove)