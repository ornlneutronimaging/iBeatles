import glob
import os
import matplotlib.image as mpimg

try:
    from PyQt4 import QtGui
    from PyQt4.QtGui import QFileDialog
except:
    from PyQt5 import QtGui
    from PyQt5.QtWidgets import QFileDialog
    
from ibeatles.utilities.file_handler import FileHandler


class LoadFiles(object):
    
    image_array = []
    list_of_files = []

    def __init__(self, image_ext = '.tiff', folder = None, list_of_files=None):
        self.image_ext = image_ext
        self.folder = folder
        self.retrieve_list_of_files(list_of_files = list_of_files)
        
        
    def retrieve_list_of_files(self, list_of_files=None):
        _folder = self.folder
        _image_ext = self.image_ext
        
        if list_of_files is None:
            _list_of_files = glob.glob(_folder + '/*' + _image_ext)
        else:
            _list_of_files = list_of_files
        
        short_list_of_files = []
        self.folder = os.path.dirname(_list_of_files[0]) + '/'
        for _file in _list_of_files:
            _short_file = os.path.basename(_file)
            short_list_of_files.append(_short_file)
        
        
        short_list_of_files = FileHandler.cleanup_list_of_files(short_list_of_files)
        self.list_of_files = short_list_of_files


class LoadTimeSpectra(object):
    
    file_found = False
    time_spectra_name_format = '*_Spectra.txt'
    
    def __init__(self, folder=None, auto_load=True):
        self.folder = folder
        if auto_load:
            self.retrieve_file_name()
        else:
            self.browse_file_name()

    def browse_file_name(self):
        file_name = QFileDialog.getOpenFileName(caption = "Select the Time Spectra File",
                                                     directory = self.folder,
                                                     filter = "Txt ({});;All (*.*)".format(self.time_spectra_name_format))
        if file_name:
            self.parent.ui.time_spectra.setText(file_name)
        
        
    def retrieve_file_name(self):
        time_spectra = glob.glob(self.folder + '/' + self.time_spectra_name_format)
        if time_spectra:
            self.file_found = True
            self.time_spectra = time_spectra[0]
        