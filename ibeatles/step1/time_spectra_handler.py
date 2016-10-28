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

from ibeatles.interfaces.ui_time_spectra_preview import Ui_MainWindow as UiMainWindow
from ibeatles.utilities.file_handler import FileHandler


class TimeSpectraHandler(object):
    
    tof_array = []
    counts_array  = []
    full_file_name = ''
    
    def __init__(self, parent=None):
        self.tof_array = []
        self.parent = parent
        self.short_file_name = str(self.parent.ui.time_spectra.text())
        self.full_file_name = os.path.join(self.parent.time_spectra_folder,
                                           str(self.parent.ui.time_spectra_folder.text()),
                                           str(self.parent.ui.time_spectra.text()))
        
        
    def load(self):
        if os.path.isfile(self.full_file_name):
            _tof_handler = TOF(filename = self.full_file_name)
            self.tof_array = _tof_handler.tof_array
            self.counts_array = _tof_handler.counts_array
    
    def display(self):
        self.load()
        if not self.tof_array == []:
            _time_spectra_window = TimeSpectraDisplay(parent = self.parent, 
                                                      short_filename = self.short_file_name,
                                                      full_filename = self.full_file_name,
                                                      x_axis = self.tof_array,
                                                      y_axis = self.counts_array)
            _time_spectra_window.show()
        
    
    
    
class TimeSpectraDisplay(QMainWindow):
    
    def __init__(self, parent=None, short_filename='', full_filename='', x_axis=[], y_axis=[]):
        
        self.parent = parent
        self.x_axis = x_axis
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
        self.ui.time_spectra_plot.set_xlabel("TOF (micros)")
        self.ui.time_spectra_plot.set_ylabel("Counts")
        self.ui.time_spectra_plot.draw()
        
        