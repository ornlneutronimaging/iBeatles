from qtpy.QtWidgets import QApplication

from ibeatles.tof_combine.utilities.image_handler import ImageHandler
from ibeatles.tof_combine.utilities.get import Get
from ibeatles.tof_combine import SessionKeys as TofSessionKeys


class LoadFiles:

    def __init__(self, parent=None, folder=None):
        self.parent = parent
        self.folder = folder

    def retrieve_data(self):

        o_get = Get(parent=self.parent)
        _row = o_get.row_of_that_folder(folder=self.folder)
        list_of_files = self.parent.dict_data_folders[_row][TofSessionKeys.list_files]

        self.parent.eventProgress.setMinimum(0)
        self.parent.eventProgress.setMaximum(len(list_of_files))
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        image_array = []
        for _index, _file in enumerate(list_of_files):
            try:
                o_handler = ImageHandler(parent=self.parent, filename=_file)
                _data = o_handler.get_data()
                image_array.append(_data)
                self.parent.eventProgress.setValue(_index + 1)
                QApplication.processEvents()
            except ValueError:
                # skip this file, it's a .txt
                pass

        self.parent.eventProgress.setVisible(False)

        return image_array
