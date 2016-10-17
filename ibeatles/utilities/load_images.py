import glob
import os
import matplotlib.image as mpimg

from PyQt4 import QtGui



class LoadImages(object):
    
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
        
        self.list_of_files = short_list_of_files


    def load(self):
        if (self.image_ext == '.tiff') or (self.image_ext == '.tif'):
            self.load_tiff()
        elif (self.image_ext == '.fits'):
            self.load_fits()
        else:
            raise TypeError("Image Type not supported")
    
    def load_tiff(self):
        _list_of_files = self.list_of_files
        _data = []
        for _file in _list_of_files:
            _image = mpimg.imread(_file)
            _data.append(_image)

        self.image_array = _data
    
    def load_fits(self):
        print("loading fits")
        print(self.list_of_files)
        
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
        file_name = QtGui.QFileDialog.getOpenFileName(caption = "Select the Time Spectra File",
                                                     directory = self.folder,
                                                     filter = "Txt ({});;All (*.*)".format(self.time_spectra_name_format))
        if file_name:
            self.parent.ui.time_spectra.setText(file_name)
        
        
    def retrieve_file_name(self):
        print(type(self.folder))
        print(type(self.time_spectra_name_format))
        time_spectra = glob.glob(self.folder + '/' + self.time_spectra_name_format)
        if time_spectra:
            self.file_found = True
            self.time_spectra = time_spectra[0]
        