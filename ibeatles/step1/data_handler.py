# import sys
import os
import glob
# import pprint
import numpy as np
from qtpy.QtWidgets import QListWidgetItem, QFileDialog

from ibeatles.utilities.load_files import LoadFiles
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.step1.time_spectra_handler import TimeSpectraHandler

TIME_SPECTRA_NAME_FORMAT = '*_Spectra.txt'


class DataHandler:
    user_canceled = False

    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type

        self.list_ui = {'sample': {'list': self.parent.ui.list_sample,
                                   'folder': self.parent.ui.sample_folder,
                                   'time_spectra': {'filename': self.parent.ui.time_spectra,
                                                    'folder': self.parent.ui.time_spectra_folder,
                                                   },
                                   },
                        'ob': {'list': self.parent.ui.list_open_beam,
                               'folder': self.parent.ui.open_beam_folder},
                        'normalized': {'list': self.parent.ui.list_normalized,
                                       'folder': self.parent.ui.normalized_folder,
                                       'time_spectra': {'filename': self.parent.ui.time_spectra_2,
                                                        'folder': self.parent.ui.time_spectra_folder_2,
                                                        },
                                       },
                        'time_spectra': {'text': self.parent.ui.time_spectra,
                                         'text2': self.parent.ui.time_spectra_2,
                                         'folder': self.parent.ui.time_spectra_folder,
                                         'folder2': self.parent.ui.time_spectra_folder_2}}

    def raises_error(self):
        raise ValueError

    def select_folder(self):
        _folder = str(QFileDialog.getExistingDirectory(caption="Select {} folder".format(self.data_type),
                                                       directory=self.parent.default_path[self.data_type],
                                                       options=QFileDialog.ShowDirsOnly))
        return _folder

    def import_files_from_folder(self, folder=''):
        if folder == '':
            self.user_canceled = True
            return ''

        list_of_files = self.get_list_of_files(folder=folder)
        if not list_of_files:
            return

        self.load_files(list_of_files)

    def import_time_spectra(self):
        self.load_time_spectra()

    def get_list_of_files(self, folder='', file_ext='.fits'):
        """list of files in that folder with that extension"""
        file_regular_expression = os.path.join(folder, '*' + file_ext)
        list_of_files = glob.glob(file_regular_expression)
        return list_of_files

    def load_files(self, list_of_files):
        image_type = self.get_image_type(list_of_files)
        o_load_image = LoadFiles(parent=self.parent,
                                 image_ext=image_type,
                                 list_of_files=list_of_files)
        self.populate_list_widget(o_load_image)
        self.record_data(o_load_image)

    def record_data(self, o_load_image):
        self.parent.list_files[self.data_type] = o_load_image.list_of_files
        self.parent.data_metadata[self.data_type]['folder'] = o_load_image.folder
        self.parent.data_metadata[self.data_type]['data'] = o_load_image.image_array

    def get_image_type(self, list_of_files):
        image_type = FileHandler.get_file_extension(list_of_files[0])
        return image_type

    def get_time_spectra_file(self):
        o_time_spectra = GetTimeSpectraFilename(parent=self.parent,
                                                data_type=self.data_type)
        return o_time_spectra.retrieve_file_name()

    def browse_file_name(self):
        [file_name, _] = QFileDialog.getOpenFileName(caption="Select the Time Spectra File",
                                                     directory=self.parent.default_path[self.data_type],
                                                     filter="Txt ({});;All (*.*)".format(TIME_SPECTRA_NAME_FORMAT))
        if file_name:
            return file_name

    def load_time_spectra(self):
        time_spectra_file = self.get_time_spectra_file()
        if not time_spectra_file:
            time_spectra_file = self.browse_file_name()

        o_time_handler = TimeSpectraHandler(parent=self.parent,
                                            filename=time_spectra_file,
                                            data_type=self.data_type)
        o_time_handler.load()
        o_time_handler.calculate_lambda_scale()
        self.save_tof_and_lambda_array(o_time_handler)
        self.print_time_spectra_filename(time_spectra_file)

    def save_tof_and_lambda_array(self, o_time_handler):
        tof_array = o_time_handler.tof_array
        lambda_array = o_time_handler.lambda_array
        if self.data_type == 'sample':
            tof_key = 'data'
            lambda_key = 'lambda'
        else:
            tof_key = 'normalized_data'
            lambda_key = 'normalized_lambda'

        self.parent.data_metadata['time_spectra'][tof_key] = tof_array
        self.parent.data_metadata['time_spectra'][lambda_key] = lambda_array

    def print_time_spectra_filename(self, time_spectra_filename):
        """display the folder and filename in the corresponding widgets"""
        base_time_spectra = os.path.basename(time_spectra_filename)
        folder_name = os.path.dirname(time_spectra_filename)
        self.list_ui[self.data_type]['time_spectra']['filename'].setText(base_time_spectra)
        self.list_ui[self.data_type]['time_spectra']['folder'].setText(folder_name)

    def retrieve_files(self, data_type='sample'):
        """
        type = ['sample', 'ob', 'normalized', 'time_spectra']
        """
        self.data_type = data_type

        # folder_selected = self._select_folder()

        mydialog = FileDialog()
        mydialog.setDirectory(self.parent.sample_folder)
        mydialog.exec_()

        # try:
        selected_files = mydialog.filesSelected()

        if selected_files:
            if len(selected_files) == 1:
                if os.path.isdir(selected_files[0]):
                    self.load_directory(selected_files[0])
                else:
                    self.load_files(selected_files[0])
            else:
                self.load_files(selected_files)

            if (data_type == 'sample') or (data_type == 'normalized'):
                self.retrieve_time_spectra()
                self.load_time_spectra()

        else:
            self.user_canceled = True

        # except TypeError:
        #     self.user_canceled = True
        #     # inform user here that the folder is empty !
        #     # FIXME
        #
        #     return

        # calculate mean data array for normalization tab
        if data_type == 'sample':
            _data = self.parent.data_metadata['sample']['data']
            normalization_mean_data = np.mean(_data, axis=0)
            self.parent.data_metadata['normalization']['data'] = normalization_mean_data

    def retrieve_time_spectra(self, auto_load=True):
        pass

        # if auto_load:
        #     if self.data_type == 'sample':
        #         folder = self.parent.data_metadata['sample']['folder']
        #     else:
        #         folder = self.parent.data_metadata['normalized']['folder']
        #     o_time_spectra = LoadTimeSpectra(folder=folder, auto_load=auto_load)
        #
        #     if o_time_spectra.file_found:
        #         time_spectra = o_time_spectra.time_spectra
        #         base_time_spectra = FileHandler.get_base_filename(time_spectra)
        #         folder_name = FileHandler.get_parent_folder(time_spectra)
        #         self.parent.time_spectra_folder = os.path.dirname(time_spectra)
        #
        #         if self.data_type == 'sample':
        #             self.list_ui['time_spectra']['text'].setText(base_time_spectra)
        #             self.list_ui['time_spectra']['folder'].setText(folder_name)
        #         elif self.data_type == 'normalized':
        #             self.parent.data_metadata['time_spectra']['full_file_name'] = time_spectra
        #             self.list_ui['time_spectra']['text2'].setText(base_time_spectra)
        #             self.list_ui['time_spectra']['folder2'].setText(folder_name)
        #             self.parent.data_metadata['time_spectra']['normalized_folder'] = folder_name
        #             self.parent.time_spectra_normalized_folder = os.path.dirname(time_spectra)
        #
        # else:
        #     if self.data_type == 'sample':
        #         folder = self.parent.data_metadata['time_spectra']['folder']
        #     else:
        #         folder = self.parent.data_metadata['time_spectra']['normalized_folder']
        #     time_spectra_name_format = '*_Spectra.txt'
        #     file_name = str(QFileDialog.getOpenFileName(caption="Select the Time Spectra File",
        #                                                 directory=folder,
        #                                                 filter="Txt ({});;All (*.*)".format(time_spectra_name_format)))
        #
        #     if file_name:
        #         folder_name = FileHandler.get_parent_folder(file_name)
        #         base_file_name = FileHandler.get_base_filename(file_name)
        #         self.parent.time_spectra_folder = os.path.dirname(file_name)
        #
        #         if self.data_type == 'sample':
        #             self.list_ui['time_spectra']['text'].setText(base_file_name)
        #             self.list_ui['time_spectra']['folder'].setText(folder_name)
        #             self.parent.data_metadata['time_spectra']['folder'] = folder_name
        #         elif self.data_type == 'normalized':
        #             self.parent.data_metadata['time_spectra']['full_file_name'] = file_name
        #             self.list_ui['time_spectra']['text2'].setText(base_file_name)
        #             self.list_ui['time_spectra']['folder2'].setText(folder_name)
        #             self.parent.data_metadata['time_spectra']['normalized_folder'] = folder_name
        #             self.parent.time_spectra_normalized_folder = os.path.dirname(file_name)

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
        self.parent.default_path[self.data_type] = _folder

        _parent_folder = FileHandler.get_parent_folder(_folder)
        self.list_ui[self.data_type]['folder'].setText(_parent_folder)

    # def load_files(self, list_of_files):
    #     image_type = self.get_image_type(list_of_files)
    #     o_load_image = LoadFiles(parent=self.parent,
    #                              image_ext=image_type,
    #                              list_of_files=list_of_files)
    #     self.populate_list_widget(o_load_image)
    #     self.parent.data_files[self.data_type] = o_load_image.list_of_files
    #     self.parent.data_metadata[self.data_type]['folder'] = o_load_image.folder
    #     # self.parent.data_metadata[self.data_type]['data'] = o_load_image.data
    #     self.parent.data_metadata[self.data_type]['data'] = o_load_image.image_array


class FileDialog(QFileDialog):
    selected_files = []

    def __init__(self, *args):
        QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, False)
        self.setFileMode(self.ExistingFiles)
        # buttons = self.findChildren(QPushButton)
        # self.openBtn = [x for x in buttons if 'open' in str(x.text()).lower()][0]
        # self.openBtn.clicked.disconnect()
        # self.openBtn.clicked.connect(self.openClicked)
        # self.tree = self.findChild(QTreeView)

    def openClicked(self):
        indexes = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in indexes:
            if i.column() == 0:
                #        files.append(os.path.join(str(self.directory().absolutePath()),str(i.data().toString())))
                files.append(os.path.join(str(self.directory().absolutePath()), str(i.data())))
        self.selected_files = files
        self.close()

    def filesSelected(self):
        print("in FileDialog, filesSelected")
        print("self.selected_files: {}".format(self.selected_files))
        return self.selected_files


class GetTimeSpectraFilename(object):
    __slots__ = ['parent', 'file_found', 'time_spectra', 'time_spectra_name_format', 'folder']

    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.file_found = False
        self.time_spectra = ''
        self.time_spectra_name_format = '*_Spectra.txt'
        self.folder = self.parent.default_path[data_type]

    def retrieve_file_name(self):
        time_spectra = glob.glob(self.folder + '/' + TIME_SPECTRA_NAME_FORMAT)
        if time_spectra and os.path.exists(time_spectra[0]):
            return time_spectra[0]

        else:
            return ''
