from qtpy.QtWidgets import QApplication
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
