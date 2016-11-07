import numpy as np


class Step1Plot(object):
    
    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type
        
    def display_bragg_edge(self):
        roi = self.parent.ui.image_view_roi
        region = roi.getArraySlice(self.parent.live_data, 
                                   self.parent.ui.image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop
        y0 = region[0][1].start
        y1 = region[0][1].stop

        data = self.parent.data_metadata['sample']['data']
        bragg_edge = []
        for _data in data:
            _sum_data = np.sum(_data[y0:y1, x0:x1])
            bragg_edge.append(_sum_data)
            
        self.parent.ui.bragg_edge_plot.clear()
        self.parent.ui.bragg_edge_plot.plot(bragg_edge)
