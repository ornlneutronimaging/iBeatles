import numpy as np
import pyqtgraph as pg


class FittingHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        self.fitting_ui = self.parent.fitting_ui
        
    def display_image(self, data=[]):
        if not(data == []):
            self.fitting_ui.data = data
            self.fitting_ui.image_view.setImage(data)
        else:
            if not self.parent.data_metadata['normalized']['data_live_selection'] == []:
                data = np.array(self.parent.data_metadata['normalized']['data_live_selection'])
                if not(data == np.array([])):
                    self.fitting_ui.image_view.setImage(data)
                    self.fitting_ui.data = data
                
    def display_roi(self):
        plot_roi = False
        if self.parent.binning_ui: #retrieve info from binning ui
            pos = self.parent.binning_ui.pos
            adj = self.parent.binning_ui.adj
            lines = self.parent.binning_ui.lines
            plot_roi = True
        elif self.parent.binning_line_view['ui']: #retrieve info from main ui
            pos = self.parent.binning_line_view['pos']
            adj = self.parent.binning_line_view['adj']
            lines = self.parent.binning_line_view['pen']
            plot_roi = True
            
        if plot_roi:
            line_view_fitting = pg.GraphItem()
            self.parent.fitting_ui.image_view.addItem(line_view_fitting)
            self.parent.fitting_ui.line_view = line_view_fitting
            self.parent.fitting_ui.line_view.setData(pos=pos, 
                                                     adj=adj,
                                                     pen=lines,
                                                     symbol=None,
                                                     pxMode=False)

      