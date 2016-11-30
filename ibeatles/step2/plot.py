import numpy as np
import pyqtgraph as pg

from neutronbraggedge.experiment_handler.experiment import Experiment
from ibeatles.utilities.colors import pen_color
from ibeatles.utilities.roi_handler import RoiHandler


class CustomAxis(pg.AxisItem):
    
    def __init__(self, gui_parent, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.parent = gui_parent
        
    def tickStrings(self, values, scale, spacing):
        strings = []

        _distance_source_detector = float(str(self.parent.ui.distance_source_detector.text()))
        _detector_offset_micros = float(str(self.parent.ui.detector_offset.text()))

        tof_s = [float(time)*1e-6 for time in values]

        _exp = Experiment(tof = tof_s,
                          distance_source_detector_m = _distance_source_detector,
                          detector_offset_micros = _detector_offset_micros)
        lambda_array = _exp.lambda_array

        for _lambda in lambda_array:
            strings.append("{:.4f}".format(_lambda*1e10))

        return strings
    
class Step2Plot(object):
    
    data = []

    def __init__(self, parent=None, data=[]):
        self.parent = parent
        data = self.parent.data_metadata['normalization']['data']
        self.data = data
        
    def display_image(self):
        _data = self.data
        
        if _data == []:
            self.clear_plots()
            self.parent.step2_ui['area'].setVisible(False)
        else:
            _data = np.array(_data)
            self.parent.step2_ui['area'].setVisible(True)
            self.parent.step2_ui['image_view'].setImage(_data)
        
    def clear_plots(self):
        self.parent.step2_ui['image_view'].clear()
        self.parent.step2_ui['bragg_edge_plot'].clear()
        