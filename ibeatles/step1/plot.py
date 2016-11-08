import numpy as np
import pyqtgraph as pg

import ibeatles.step1.utilities as utilities
from ibeatles.step1.time_spectra_handler import TimeSpectraHandler


class CustomAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return ['{:.4f}'.format(1./i) for i in values]
                

class Step1Plot(object):
    
    data = []
    
    def __init__(self, parent=None, data_type='sample', data=[]):
        self.parent = parent
        self.data_type = data_type
        if data == []:
            data = self.parent.data_metadata[data_type]['data']
        self.data = data
        
    def all_plots(self):
        self.display_image()
        self.display_bragg_edge()

    def display_image(self):
        _data = self.data
        self.parent.live_data = _data
    
        if _data == []:
            self.clear_plots(data_type = self.data_type)
        else:
            if self.data_type == 'sample':
                self.parent.ui.image_view.setImage(_data)       
            elif self.data_type == 'ob':
                self.parent.ui.ob_image_view.setImage(_data)
            elif self.data_type == 'normalized':
                self.parent.ui.normalized_image_view.setImage(_data)

    def clear_plots(self, data_type = 'sample'):
        if data_type == 'sample':
            self.parent.ui.image_view.clear()
            self.parent.ui.bragg_edge_plot.clear()
        elif data_type == 'ob':
            self.parent.ui.ob_image_view.clear()
            self.parent.ui.ob_bragg_edge_plot.clear()
        elif data_type == 'normalized':
            self.parent.ui.normalized_image_view.clear()
            self.parent.ui.normalized_bragg_edge_plot.clear()
        
    def display_general_bragg_edge(self):
        data_type = utilities.get_tab_selected(parent=self.parent)
        self.data_type = data_type
        data = self.parent.data_metadata[data_type]['data']
        self.data = data
        self.display_bragg_edge()
        
    def display_bragg_edge(self):
        _data = self.data
        if _data == []:
            if self.data_type == 'sample':
                self.parent.ui.bragg_edge_plot.clear()
            elif self.data_type == 'ob':
                self.parent.ui.ob_bragg_edge_plot.clear()
            elif self.data_type == 'normalized':
                self.parent.ui.normalized_bragg_edge_plot.clear()
        else:
            if self.data_type == 'sample':
                roi = self.parent.ui.image_view_roi
                _image_view_item = self.parent.ui.image_view.imageItem
            elif self.data_type == 'ob':
                roi = self.parent.ui.ob_image_view_roi
                _image_view_item = self.parent.ui.ob_image_view.imageItem
            elif self.data_type == 'normalized':
                roi = self.parent.ui.normalized_image_view_roi
                _image_view_item = self.parent.ui.normalized_image_view.imageItem
                
            region = roi.getArraySlice(self.parent.live_data, 
                                       _image_view_item)
            x0 = region[0][0].start
            x1 = region[0][0].stop
            y0 = region[0][1].start
            y1 = region[0][1].stop
    
            data = self.parent.data_metadata[self.data_type]['data']
            bragg_edge = []
            for _data in data:
                _sum_data = np.sum(_data[y0:y1, x0:x1])
                bragg_edge.append(_sum_data)

            #check if xaxis can be in lambda, or tof
            o_time_handler = TimeSpectraHandler(parent = self.parent)
            o_time_handler.load()
            tof_array = o_time_handler.tof_array
            lambda_array = o_time_handler.lambda_array
                
            if self.data_type == 'sample':
                self.parent.ui.bragg_edge_plot.clear()
                if tof_array == []:
                    self.parent.ui.bragg_edge_plot.plot(bragg_edge)
                    self.parent.ui.bragg_edge_plot.setLabel('bottom', 'File Index')
                else:
                    self.parent.ui.bragg_edge_plot.plot(tof_array, bragg_edge)
                    self.parent.ui.bragg_edge_plot.setLabel('bottom', u'TOF (\u00B5s)')
#                    self.parent.ui.bragg_edge_plot.setLabel('top', u'\u03BB (\u212B)')
            elif self.data_type == 'ob':
                self.parent.ui.ob_bragg_edge_plot.clear()
                if tof_array == []:
                    self.parent.ui.ob_bragg_edge_plot.plot(bragg_edge)
                    self.parent.ui.ob_bragg_edge_plot.setLabel('bottom', 'File Index')
                else:
                    self.parent.ui.ob_bragg_edge_plot.plot(tof_array, bragg_edge)
                    self.parent.ui.ob_bragg_edge_plot.setLabel('bottom', u'TOF (\u00B5s)')
                    #lambda array

                    self.parent.ui.ob_bragg_edge_plot.setLabel('top', u'\u03BB (\u212B)')
            elif self.data_type == 'normalized':
                self.parent.ui.normalized_bragg_edge_plot.clear()
                if tof_array == []:
                    self.parent.ui.normalized_bragg_edge_plot.plot(bragg_edge)
                    self.parent.ui.normalized_bragg_edge_plot.setLabel('bottom', 'File Index')
                else:
                    self.parent.ui.normalized_bragg_edge_plot.plot(tof_array, bragg_edge)
                    self.parent.ui.normalized_bragg_edge_plot.setLabel('bottom', u'TOF (\u00B5s)')
                    #lambda array

                    self.parent.ui.normalized_bragg_edge_plot.setLabel('top', u'\u03BB (\u212B)')
                