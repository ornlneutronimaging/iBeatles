from qtpy.QtWidgets import QApplication

from ibeatles.tof_combine.utilities.image_handler import ImageHandler


class LoadFiles:

    def __init__(self, parent=None, folder=None):
        self.parent = parent
        self.folder = folder

    def retrieve_data(self):
        list_of_files = self.parent.raw_data_folders[self.folder]['list_files']

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

