import os
import numpy as np

try:
    import PyQt4
    import PyQt4.QtGui as QtGui
    from PyQt4.QtGui import QMainWindow
except:
    import PyQt5
    import PyQt5.QtGui as QtGui
    from PyQt5.QtWidgets import QMainWindow

from neutronbraggedge.experiment_handler.tof import TOF
from neutronbraggedge.experiment_handler.experiment import Experiment

from ibeatles.interfaces.ui_time_spectra_preview import Ui_MainWindow as UiMainWindow
from ibeatles.utilities.file_handler import FileHandler
import ibeatles.utilities.math_tools as math_tools


class TimeSpectraHandler(object):
    
    tof_array = []
    lambda_array = []
    counts_array  = []
    full_file_name = ''
    
    def __init__(self, parent=None, normalized_tab=False):
        self.tof_array = []
        self.parent = parent

        if normalized_tab:
            self.short_file_name = str(self.parent.ui.time_spectra_2.text())
            self.full_file_name = os.path.join(self.parent.time_spectra_normalized_folder ,
                                               self.short_file_name)
        else:
            self.short_file_name = str(self.parent.ui.time_spectra.text())
            self.full_file_name = os.path.join(self.parent.time_spectra_folder,
                                               str(self.parent.ui.time_spectra.text()))
        
    def load(self):
        if os.path.isfile(self.full_file_name):
            _tof_handler = TOF(filename = self.full_file_name)
            _tof_array_s = _tof_handler.tof_array
            #self.tof_array = _tof_array_s * 1e6
            self.tof_array = _tof_array_s
            self.counts_array = _tof_handler.counts_array
            
    def calculate_lambda_scale(self):
        distance_source_detector = str(self.parent.ui.distance_source_detector.text())
        detector_offset = str(self.parent.ui.detector_offset.text())
                             
        if (math_tools.is_float(distance_source_detector)) and \
           (math_tools.is_float(detector_offset)):
            distance_source_detector = float(distance_source_detector)
            detector_offset = float(detector_offset)

            _exp = Experiment(tof=self.tof_array,
                              distance_source_detector_m=distance_source_detector,
                              detector_offset_micros=detector_offset)
            self.lambda_array = _exp.lambda_array
            
        else:
            self.lambda_array = []
    
    def display(self):
        self.load()
        self.calculate_lambda_scale()
        if not self.tof_array == []:
            _time_spectra_window = TimeSpectraDisplay(parent = self.parent, 
                                                      short_filename = self.short_file_name,
                                                      full_filename = self.full_file_name,
                                                      x_axis = self.tof_array,
                                                      y_axis = self.counts_array,
                                                      x2_axis = self.lambda_array)
            _time_spectra_window.show()
        
    
    
    
class TimeSpectraDisplay(QMainWindow):
    
    def __init__(self, parent=None, short_filename='', full_filename='', 
                 x_axis=[], y_axis=[], x2_axis=[]):
        
        self.parent = parent
        self.x_axis = x_axis
        self.x2_axis = x2_axis
        self.y_axis = y_axis
        self.full_filename = full_filename
        
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle(short_filename)
        
        self.populate_text()
        self.plot_data()
        
    def populate_text(self):
        _file_contain = FileHandler.retrieve_ascii_contain(self.full_filename)
        self.ui.time_spectra_text.setText(_file_contain)
    
    def plot_data(self):
        self.ui.time_spectra_plot.plot(self.x_axis, self.y_axis)

        if not self.x2_axis == []:
            ax2 = self.ui.time_spectra_plot.canvas.ax.twiny()
            ax2.plot(self.x2_axis, np.ones(len(self.x2_axis)))
            ax2.cla()
            ax2.set_xlabel(r"$Lambda  (\AA)$")
        
        self.ui.time_spectra_plot.set_xlabel(r"$TOF  (\mu s)$")
        self.ui.time_spectra_plot.set_ylabel("Counts")
        self.ui.time_spectra_plot.canvas.figure.subplots_adjust(top=0.9,
                                                                left=0.1)

        self.ui.time_spectra_plot.draw()
        
        