import os

import PyQt4
import PyQt4.QtGui as QtGui

from neutronbraggedge.experiment_handler.tof import TOF

from ibeatles.interfaces.ui_time_spectra_preview import Ui_MainWindow as UiMainWindow


class TimeSpectraHandler(object):
    
    tof_array = []
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
    
    def display(self):
        self.load()
        if not self.tof_array == []:
            _time_spectra_window = TimeSpectraDisplay(parent = self.parent, 
                                                      filename = self.short_file_name)
            _time_spectra_window.show()
        
    
    
    
class TimeSpectraDisplay(QtGui.QMainWindow):
    
    def __init__(self, parent=None, filename=''):
        
        self.parent = parent
        
        QtGui.QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        
        self.setWindowTitle(filename)
        