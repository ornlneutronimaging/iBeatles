import os
import glob
from pathlib import PurePath
import numpy as np
from qtpy.QtWidgets import QListWidgetItem, QFileDialog
import logging
import copy

from ..utilities.load_files import LoadFiles
from ..utilities.status_message_config import StatusMessageStatus, show_status_message
from ..utilities.file_handler import FileHandler
from ..step1.time_spectra_handler import TimeSpectraHandler
from .. import DataType

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
                                                       directory=os.path.dirname(self.parent.default_path[
                                                           self.data_type]),
                                                       options=QFileDialog.ShowDirsOnly))
        return _folder

    def import_files_from_folder(self, folder='', extension=".fits"):
        logging.info(f"importing files from folder with extension: {extension}")
        if folder == '':
            self.user_canceled = True
            return False

        if type(extension) is list:
            for _ext in extension:
                list_of_files = self.get_list_of_files(folder=folder, file_ext=_ext)
                if list_of_files:
                    break
        else:
            list_of_files = self.get_list_of_files(folder=folder, file_ext=extension)

        if not list_of_files:
            logging.info(f"Folder {folder} is empty or does not contain the right file format!")
            show_status_message(parent=self.parent,
                                message=f"Folder selected is empty or contains the wrong file formats!",
                                status=StatusMessageStatus.error,
                                duration_s=5)
            return False

        logging.info(f" len(list_of_files) = {len(list_of_files)}")
        if len(list_of_files) > 2:
            logging.info(f"  list_of_files[0] = {list_of_files[0]}")
            logging.info("    ...")
            logging.info(f"  list_of_files[-1] = {list_of_files[-1]}")
        else:
            logging.info(f"  list_of_files = {list_of_files}")
        self.load_files(list_of_files)
        return True

    def import_time_spectra(self):
        if not (self.parent.data_metadata[self.data_type]['data'] is None):
            if (self.data_type == DataType.sample) or (self.data_type == DataType.normalized):
                self.load_time_spectra()

    def get_list_of_files(self, folder='', file_ext='.fits'):
        """list of files in that folder with that extension"""
        file_regular_expression = os.path.join(folder, '*' + file_ext)
        list_of_files = glob.glob(file_regular_expression)
        list_of_files.sort()
        return list_of_files

    def load_files(self, list_of_files):
        logging.info("Loading files")
        image_type = DataHandler.get_image_type(list_of_files)
        logging.info(f" image type: {image_type}")
        o_load_image = LoadFiles(parent=self.parent,
                                 image_ext=image_type,
                                 list_of_files=list_of_files)
        self.populate_list_widget(o_load_image)
        self.record_data(o_load_image)

    def record_data(self, o_load_image):
        self.parent.list_files[self.data_type] = o_load_image.list_of_files
        self.parent.data_metadata[self.data_type]['folder'] = o_load_image.folder
        self.parent.data_metadata[self.data_type]['data'] = np.array(o_load_image.image_array)

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

    def load_time_spectra(self, time_spectra_file=None):
        if time_spectra_file is None:
            time_spectra_file = self.get_time_spectra_file()
            if not time_spectra_file:
                time_spectra_file = self.browse_file_name()

            if time_spectra_file is None:
                logging.info("User cancel browsing for time_spectra_file manually but time spectra is Mandatory!")
                time_spectra_file = self.browse_file_name()

        logging.info(f"User manually selected time spectra file {time_spectra_file}")

        self.parent.data_metadata[self.data_type]['time_spectra']['filename'] = time_spectra_file

        o_time_handler = TimeSpectraHandler(parent=self.parent,
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
        elif self.data_type == 'normalized':
            tof_key = 'normalized_data'
            lambda_key = 'normalized_lambda'

        self.parent.data_metadata['time_spectra'][tof_key] = tof_array
        self.parent.data_metadata['time_spectra'][lambda_key] = lambda_array

    def print_time_spectra_filename(self, time_spectra_filename):
        """display the folder and filename in the corresponding widgets"""
        time_spectra_filename = PurePath(time_spectra_filename)
        base_time_spectra = str(time_spectra_filename.name)
        folder_name = str(time_spectra_filename.parent)
        self.list_ui[self.data_type]['time_spectra']['filename'].setText(base_time_spectra)
        self.list_ui[self.data_type]['time_spectra']['folder'].setText(folder_name)
        self.parent.data_metadata[self.data_type]['time_spectra']['folder'] = folder_name

    def retrieve_files(self, data_type='sample'):
        """
        type = ['sample', 'ob', 'normalized', 'time_spectra']
        """
        self.data_type = data_type

        # folder_selected = self._select_folder()

        mydialog = FileDialog()
        mydialog.setDirectory(self.parent.default_path[data_type])
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

    def retrieve_time_spectra(self):
        folder = self.parent.default_path[self.data_type]
        time_spectra_name_format = '*_Spectra.txt'
        [file_name, _] = QFileDialog.getOpenFileName(caption="Select the Time Spectra File",
                                                     directory=folder,
                                                     filter="Txt ({});;All (*.*)".format(time_spectra_name_format))

        if file_name:
            folder_name = str(FileHandler.get_parent_path(file_name))
            base_file_name = str(FileHandler.get_base_filename(file_name))
            self.parent.time_spectra_folder = str(FileHandler.get_parent_folder(file_name))

            self.list_ui[self.data_type]['time_spectra']['filename'].setText(base_file_name)
            self.list_ui[self.data_type]['time_spectra']['folder'].setText(folder_name)
            self.parent.data_metadata[self.data_type]['time_spectra']['folder'] = folder_name
            self.parent.data_metadata[self.data_type]['time_spectra']['filename'] = file_name
            return True

        return False

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
        self.parent.sample_folder = os.path.dirname(o_load_image.folder)
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

    @staticmethod
    def get_image_type(list_of_files):
        image_type = FileHandler.get_file_extension(list_of_files[0])
        return image_type


class FileDialog(QFileDialog):
    selected_files = []

    def __init__(self, *args):
        QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, False)
        self.setFileMode(self.ExistingFiles)

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
            return f"{time_spectra[0]}"

        else:
            return ""
