import sys
import os
import glob
import pprint
import numpy as np
from qtpy.QtWidgets import QListWidgetItem, QFileDialog, QPushButton, QTreeView

from ibeatles.utilities.load_files import LoadFiles, LoadTimeSpectra
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.step1.time_spectra_handler import TimeSpectraHandler


class DataHandler(object):
    user_canceled = False

    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type

        self.list_ui = {'sample': {'list': self.parent.ui.list_sample,
                                   'folder': self.parent.ui.sample_folder},
                        'ob': {'list': self.parent.ui.list_open_beam,
                               'folder': self.parent.ui.open_beam_folder},
                        'normalized': {'list': self.parent.ui.list_normalized,
                                       'folder': self.parent.ui.normalized_folder},
                        'time_spectra': {'text': self.parent.ui.time_spectra,
                                         'text2': self.parent.ui.time_spectra_2,
                                         'folder': self.parent.ui.time_spectra_folder,
                                         'folder2': self.parent.ui.time_spectra_folder_2}}

    def retrieve_files(self, data_type='sample'):
        """
        type = ['sample', 'ob', 'normalized', 'time_spectra']
        """

        self.data_type = data_type

        mydialog = FileDialog()
        mydialog.setDirectory(self.parent.sample_folder)
        mydialog.exec_()

        try:
            selectedFiles = mydialog.filesSelected()
            if selectedFiles:
                if len(selectedFiles) == 1:
                    if os.path.isdir(selectedFiles[0]):
                        self.load_directory(selectedFiles[0])
                    else:
                        self.load_files(selectedFiles[0])
                else:
                    self.load_files(selectedFiles)

                if (data_type == 'sample') or (data_type == 'normalized'):
                    self.retrieve_time_spectra()
                    self.load_time_spectra()

            else:
                self.user_canceled = True

        except TypeError:
            self.user_canceled = True
            # inform user here that the folder is empty !
            # FIXME

            return

        # calculate mean data array for normalization tab
        if data_type == 'sample':
            _data = self.parent.data_metadata['sample']['data']
            normalization_mean_data = np.mean(_data, axis=0)
            self.parent.data_metadata['normalization']['data'] = normalization_mean_data

    def load_time_spectra(self):
        if self.data_type == 'normalized':
            o_time_handler = TimeSpectraHandler(parent=self.parent, normalized_tab=True)
        else:
            o_time_handler = TimeSpectraHandler(parent=self.parent)
        o_time_handler.load()
        o_time_handler.calculate_lambda_scale()
        tof_array = o_time_handler.tof_array
        lambda_array = o_time_handler.lambda_array
        if self.data_type == 'sample':
            self.parent.data_metadata['time_spectra']['data'] = tof_array
            self.parent.data_metadata['time_spectra']['lambda'] = lambda_array
        else:  # normalized
            self.parent.data_metadata['time_spectra']['normalized_data'] = tof_array
            self.parent.data_metadata['time_spectra']['normalized_lambda'] = lambda_array

    def retrieve_time_spectra(self, auto_load=True):
        if auto_load:
            if self.data_type == 'sample':
                folder = self.parent.data_metadata['sample']['folder']
            else:
                folder = self.parent.data_metadata['normalized']['folder']
            o_time_spectra = LoadTimeSpectra(folder=folder, auto_load=auto_load)

            if o_time_spectra.file_found:
                time_spectra = o_time_spectra.time_spectra
                base_time_spectra = FileHandler.get_base_filename(time_spectra)
                folder_name = FileHandler.get_parent_folder(time_spectra)
                self.parent.time_spectra_folder = os.path.dirname(time_spectra)

                if self.data_type == 'sample':
                    self.list_ui['time_spectra']['text'].setText(base_time_spectra)
                    self.list_ui['time_spectra']['folder'].setText(folder_name)
                elif self.data_type == 'normalized':
                    self.parent.data_metadata['time_spectra']['full_file_name'] = time_spectra
                    self.list_ui['time_spectra']['text2'].setText(base_time_spectra)
                    self.list_ui['time_spectra']['folder2'].setText(folder_name)
                    self.parent.data_metadata['time_spectra']['normalized_folder'] = folder_name
                    self.parent.time_spectra_normalized_folder = os.path.dirname(time_spectra)

        else:
            if self.data_type == 'sample':
                folder = self.parent.data_metadata['time_spectra']['folder']
            else:
                folder = self.parent.data_metadata['time_spectra']['normalized_folder']
            time_spectra_name_format = '*_Spectra.txt'
            file_name = str(QFileDialog.getOpenFileName(caption="Select the Time Spectra File",
                                                        directory=folder,
                                                        filter="Txt ({});;All (*.*)".format(time_spectra_name_format)))

            if file_name:
                folder_name = FileHandler.get_parent_folder(file_name)
                base_file_name = FileHandler.get_base_filename(file_name)
                self.parent.time_spectra_folder = os.path.dirname(file_name)

                if self.data_type == 'sample':
                    self.list_ui['time_spectra']['text'].setText(base_file_name)
                    self.list_ui['time_spectra']['folder'].setText(folder_name)
                    self.parent.data_metadata['time_spectra']['folder'] = folder_name
                elif self.data_type == 'normalized':
                    self.parent.data_metadata['time_spectra']['full_file_name'] = file_name
                    self.list_ui['time_spectra']['text2'].setText(base_file_name)
                    self.list_ui['time_spectra']['folder2'].setText(folder_name)
                    self.parent.data_metadata['time_spectra']['normalized_folder'] = folder_name
                    self.parent.time_spectra_normalized_folder = os.path.dirname(file_name)

    def load_directory(self, folder):
        list_files = glob.glob(folder + '/*.*')
        if len(list_files) == 0:
            raise TypeError
        image_type = self.get_image_type(list_files)
        o_load_image = LoadFiles(parent=self.parent,
                                 image_ext=image_type,
                                 folder=folder)
        self.populate_list_widget(o_load_image)
        self.parent.data_files[self.data_type] = o_load_image.list_of_files
        self.parent.data_metadata[self.data_type]['folder'] = o_load_image.folder
        self.parent.sample_folder = os.path.dirname(os.path.dirname(o_load_image.folder))
        self.parent.data_metadata[self.data_type]['data'] = o_load_image.image_array

    def populate_list_widget(self, o_loader):
        list_of_files = o_loader.list_of_files

        _list_ui = self.list_ui[self.data_type]['list']
        _list_ui.clear()
        for _row, _file in enumerate(list_of_files):
            _item = QListWidgetItem(_file)
            _list_ui.insertItem(_row, _item)

        _folder = o_loader.folder
        self.folder = _folder

        _parent_folder = FileHandler.get_parent_folder(_folder)
        self.list_ui[self.data_type]['folder'].setText(_parent_folder)

    def load_files(self, list_of_files):
        image_type = self.get_image_type(list_of_files)
        o_load_image = LoadFiles(parent=self.parent,
                                 image_ext=image_type,
                                 list_of_files=list_of_files)
        self.populate_list_widget(o_load_image)
        self.parent.data_files[self.data_type] = o_load_image.list_of_files
        self.parent.data_metadata[self.data_type]['folder'] = o_load_image.folder
        # self.parent.data_metadata[self.data_type]['data'] = o_load_image.data
        self.parent.data_metadata[self.data_type]['data'] = o_load_image.image_array

    def get_image_type(self, list_of_files):
        raw_file, ext = os.path.splitext(list_of_files[1])
        return ext


class FileDialog(QFileDialog):
    selectedFiles = []

    def __init__(self, *args):
        QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, False)
        self.setFileMode(self.ExistingFiles)
        btns = self.findChildren(QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QTreeView)

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                #        files.append(os.path.join(str(self.directory().absolutePath()),str(i.data().toString())))
                files.append(os.path.join(str(self.directory().absolutePath()), str(i.data())))
        self.selectedFiles = files
        self.close()

    def filesSelected(self):
        return self.selectedFiles
