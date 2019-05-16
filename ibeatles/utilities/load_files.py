from qtpy.QtWidgets import QApplication, QFileDialog
import glob
import os

from ibeatles.utilities.file_handler import FileHandler
from ibeatles.utilities.image_handler import ImageHandler


class LoadFiles(object):

    # class variables
    image_array = []
    list_of_files = []
    data = []

    def __init__(self, parent=None, image_ext='.tiff', folder=None, list_of_files=None):
        self.parent = parent
        self.image_ext = image_ext
        self.folder = folder
        self.retrieve_list_of_files(list_of_files=list_of_files)
        self.retrieve_data()

    def retrieve_list_of_files(self, list_of_files=None):
        _folder = self.folder
        _image_ext = self.image_ext

        if list_of_files is None:
            _list_of_files = glob.glob(_folder + '/*' + _image_ext)
        else:
            _list_of_files = list_of_files

        self.list_of_files_full_name = _list_of_files
        short_list_of_files = []
        self.folder = os.path.dirname(_list_of_files[0]) + '/'
        for _file in _list_of_files:
            _short_file = os.path.basename(_file)
            short_list_of_files.append(_short_file)

        short_list_of_files = FileHandler.cleanup_list_of_files(short_list_of_files)
        self.list_of_files = short_list_of_files

    def retrieve_data(self):

        self.image_array = []

        self.parent.eventProgress.setMinimum(0)
        self.parent.eventProgress.setMaximum(len(self.list_of_files))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        for _index, _file in enumerate(self.list_of_files):
            full_file_name = os.path.join(self.folder, _file)
            o_handler = ImageHandler(parent=self.parent, filename=full_file_name)
            _data = o_handler.get_data()
            self.image_array.append(_data)
            self.parent.eventProgress.setValue(_index + 1)
            QApplication.processEvents()

        self.parent.eventProgress.setVisible(False)


class LoadTimeSpectra(object):
    __slots__ = ['file_found', 'time_spectra', 'time_spectra_name_format', 'folder']

    def __init__(self, folder=None, auto_load=True):
        self.file_found = False
        self.time_spectra = ''
        self.time_spectra_name_format = '*_Spectra.txt'
        self.folder = folder

        if auto_load:
            self.retrieve_file_name()
        else:
            self.browse_file_name()

    def browse_file_name(self):
        file_name = QFileDialog.getOpenFileName(caption="Select the Time Spectra File",
                                                directory=self.folder,
                                                filter="Txt ({});;All (*.*)".format(self.time_spectra_name_format))
        if file_name:
            self.parent.ui.time_spectra.setText(file_name)

    def retrieve_file_name(self):
        time_spectra = glob.glob(self.folder + '/' + self.time_spectra_name_format)
        if time_spectra:
            self.file_found = True
            self.time_spectra = time_spectra[0]

