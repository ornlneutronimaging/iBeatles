import os
from qtpy.QtWidgets import QFileDialog, QCheckBox
import logging
import numpy as np
import copy

from ibeatles.session import SessionSubKeys
from ibeatles.tof_combine import SessionKeys as TofCombineSessionKeys
from ibeatles import DataType
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.tof_combine.utilities.table_handler import TableHandler
from ibeatles.tof_combine.utilities.time_spectra import GetTimeSpectraFilename, TimeSpectraHandler
from ibeatles.tof_combine.utilities.get import Get as TofCombineGet
from ibeatles.tof_combine.utilities import CombineAlgorithm, TimeSpectraKeys
from ibeatles.tof_combine.load.load_files import LoadFiles
from ibeatles.tof_combine.combine.combine import Combine
from ibeatles.tof_combine import LAMBDA, MICRO, ANGSTROMS


class EventHandler:

    no_data_loaded = False

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

        # o_get = TofCombineGet(parent=parent)
        # list_working_folders = o_get.list_of_folders_to_use()
        # if list_working_folders == [None]:
        #     self.no_data_loaded = True

    def visualize_flag_changed(self):
        self.parent.visualize_flag = self.parent.ui.visualize_checkBox.isChecked()
        if self.parent.visualize_flag:
            self.parent.ui.combine_horizontal_splitter.setSizes([20, 500])
        else:
            self.parent.ui.combine_horizontal_splitter.setSizes([100, 0])


    def select_top_folder(self):
        if self.no_data_loaded:
            return

        default_path = self.grand_parent.session_dict[DataType.sample][SessionSubKeys.current_folder]
        folder = str(QFileDialog.getExistingDirectory(caption="Select Top Working Folder",
                                                       directory=default_path,
                                                       options=QFileDialog.ShowDirsOnly))
        if folder == "":
            logging.info("User Canceled the selection of top folder dialog!")
            return

        logging.info(f"Users selected a new top folder: {folder}")

        # get list of folders in top folder
        list_folders = FileHandler.get_list_of_all_subfolders(folder)
        list_folders = self.keep_only_folders_with_tiff_files(list_folders)
        list_folders.sort()

        self.parent.session[TofCombineSessionKeys.list_folders] = list_folders
        self.parent.session[TofCombineSessionKeys.top_folder] = folder

        # initialize parameters when using new working folder
        self.reset_data()

        # display the full path of the top folder selected
        self.parent.ui.top_folder_label.setText(folder)

        # display list of folders in widget and column showing working folders used
        self.populate_list_of_folders_to_combine()

        # update ui
        self.check_widgets()

    def at_least_one_folder_selected(self):
        for key in self.parent.dict_data_folders.keys():
            if self.parent.dict_data_folders[key][TofCombineSessionKeys.use]:
                return True
        return False

    def at_least_two_folder_selected(self):
        """check if there are at least 2 folders selected"""
        nbr_folder_selected = 0
        for key in self.parent.dict_data_folders.keys():
            if self.parent.dict_data_folders[key][TofCombineSessionKeys.use]:
                nbr_folder_selected += 1

        if nbr_folder_selected >= 2:
            return True

        return False

    def check_widgets(self):
        if self.parent.session[TofCombineSessionKeys.top_folder]:
            self.parent.ui.combine_refresh_top_folder_pushButton.setEnabled(True)
        else:
            self.parent.ui.combine_refresh_top_folder_pushButton.setEnabled(False)

        if self.at_least_two_folder_selected():
            self.parent.ui.combine_widget.setEnabled(True)
        else:
            self.parent.ui.combine_widget.setEnabled(False)

    def refresh_table_clicked(self):
        self.parent.ui.combine_tableWidget.blockSignals(True)

        logging.info("User clicked the refresh table!")
        top_folder = self.parent.session[TofCombineSessionKeys.top_folder]
        list_folders = FileHandler.get_list_of_all_subfolders(top_folder)
        list_folders = self.keep_only_folders_with_tiff_files(list_folders=list_folders)

        # checking if there is any new folder
        current_list_of_folders = []
        for _row in self.parent.dict_data_folders.keys():
            current_list_of_folders.append(self.parent.dict_data_folders[_row][TofCombineSessionKeys.folder])

        row = len(current_list_of_folders)
        for _folder in list_folders:
            if not (_folder in current_list_of_folders):

                list_folders.append(_folder)
                list_files = FileHandler.get_list_of_tif(_folder)
                nbr_files = len(list_files)

                self.parent.dict_data_folders[row] = {TofCombineSessionKeys.folder: _folder,
                                                      TofCombineSessionKeys.data: None,
                                                      TofCombineSessionKeys.list_files: list_files,
                                                      TofCombineSessionKeys.nbr_files: nbr_files,
                                                      TofCombineSessionKeys.use: False,
                                                      }
                self.insert_row_entry(row)
                row += 1

        self.parent.session[TofCombineSessionKeys.list_folders] = list_folders
        self.parent.ui.combine_tableWidget.blockSignals(False)

    def keep_only_folders_with_tiff_files(self, list_folders):
        """will go over the list of folders and will only keep the one with tiff in it"""
        list_folders.sort()
        clean_list_folders = []
        for _folder in list_folders:
            list_files = FileHandler.get_list_of_tif(_folder)
            if len(list_files) > 0:
                clean_list_folders.append(_folder)

        return clean_list_folders

    def reset_data(self):
        """
        This re-initialize all the parameters when working with a new top folder
        """

        # reset master dictionary that contains the raw data
        list_folders = self.parent.session[TofCombineSessionKeys.list_folders]
        if list_folders is None:
            return

        _data_dict = {}
        for _row, _folder in enumerate(list_folders):
            list_files = FileHandler.get_list_of_tif(_folder)
            nbr_files = len(list_files)
            _data_dict[_row] = {TofCombineSessionKeys.folder: _folder,
                                TofCombineSessionKeys.data: None,
                                TofCombineSessionKeys.list_files: list_files,
                                TofCombineSessionKeys.nbr_files: nbr_files,
                                TofCombineSessionKeys.use: False,
                                }
        self.parent.dict_data_folders = _data_dict

        # reset time spectra
        self.parent.time_spectra = {TimeSpectraKeys.file_name: None,
                                    TimeSpectraKeys.tof_array: None,
                                    TimeSpectraKeys.lambda_array: None,
                                    TimeSpectraKeys.file_index_array: None}

        self._reset_time_spectra_tab()

    def _reset_time_spectra_tab(self):
        self.parent.ui.time_spectra_name_label.setText("N/A")
        self.parent.ui.time_spectra_preview_pushButton.setEnabled(False)

    def populate_list_of_folders_to_combine(self):
        list_of_folders = self.parent.session[TofCombineSessionKeys.list_folders]

        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        o_table.remove_all_rows()

        if list_of_folders is None:
            return

        for _row, _folder in enumerate(list_of_folders):
            self.insert_row_entry(_row)

    def insert_row_entry(self, row=0):

        folder_dict = self.parent.dict_data_folders[row]

        status_of_folder = folder_dict[TofCombineSessionKeys.use]
        nbr_files = folder_dict[TofCombineSessionKeys.nbr_files]
        folder_name = folder_dict[TofCombineSessionKeys.folder]

        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        row = o_table.row_count()
        o_table.insert_empty_row(row=row)

        # use or not that row
        check_box = QCheckBox()
        check_box.setChecked(status_of_folder)

        # check if this file has more than 1 file
        # if not disable radio button
        # number of images in that folder
        if nbr_files > 0:
            check_box.setEnabled(True)
        else:
            check_box.setEnabled(False)

        o_table.insert_widget(row=row,
                              column=0,
                              widget=check_box,
                              centered=True)
        check_box.clicked.connect(self.parent.radio_buttons_of_folder_changed)

        o_table.insert_item(row=row,
                            column=1,
                            value=nbr_files,
                            editable=False)

        # full path of the folder
        o_table.insert_item(row=row,
                            column=2,
                            value=folder_name,
                            editable=False)

    def update_list_of_folders_to_use(self, force_recalculation_of_time_spectra=False):
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        nbr_row = o_table.row_count()
        for _row_index in np.arange(nbr_row):
            _horizontal_widget = o_table.get_widget(row=_row_index,
                                                    column=0)
            radio_button = _horizontal_widget.layout().itemAt(1).widget()
            self.parent.dict_data_folders[_row_index][TofCombineSessionKeys.use] = radio_button.isChecked()

        for _row_index in np.arange(nbr_row):

            if self.parent.dict_data_folders[_row_index][TofCombineSessionKeys.use]:

                _folder_name = self.parent.dict_data_folders[_row_index][TofCombineSessionKeys.folder]

                if force_recalculation_of_time_spectra:
                    self.load_time_spectra_file(folder=_folder_name)
                    self.fix_linear_bin_radio_button_max_values()

                if self.parent.dict_data_folders[_row_index][TofCombineSessionKeys.data] is None:
                    loading_worked = self.load_that_folder(folder_name=_folder_name)

                    # load time spectra if not already there
                    if self.parent.time_spectra[TimeSpectraKeys.file_name] is None:
                        self.load_time_spectra_file(folder=_folder_name)
                        self.fix_linear_bin_radio_button_max_values()

    def load_time_spectra_file(self, folder=None):
        """
        load the time spectra file
        :param folder: location of the time spectra file
        :return:
        """
        o_time_spectra = GetTimeSpectraFilename(parent=self.parent,
                                                folder=folder)
        full_path_to_time_spectra = o_time_spectra.retrieve_file_name()

        o_time_handler = TimeSpectraHandler(parent=self.parent,
                                            time_spectra_file_name=full_path_to_time_spectra)
        o_time_handler.load()
        o_time_handler.calculate_lambda_scale()

        tof_array = o_time_handler.tof_array
        lambda_array = o_time_handler.lambda_array
        file_index_array = np.arange(len(tof_array))

        self.parent.time_spectra[TimeSpectraKeys.file_name] = full_path_to_time_spectra
        self.parent.time_spectra[TimeSpectraKeys.tof_array] = tof_array
        self.parent.time_spectra[TimeSpectraKeys.lambda_array] = lambda_array
        self.parent.time_spectra[TimeSpectraKeys.file_index_array] = file_index_array
        self.parent.time_spectra[TimeSpectraKeys.counts_array] = o_time_handler.counts_array

        # update time spectra tab
        self.parent.ui.time_spectra_name_label.setText(os.path.basename(full_path_to_time_spectra))
        self.parent.ui.time_spectra_preview_pushButton.setEnabled(True)

    def load_that_folder(self, folder_name=None):
        """
        this routine load all the images of the selected folder
        :param folder_name: full path of the folder containing the images to load
        :return: True if the loading worked, False otherwise
        """
        if not os.path.exists(folder_name):
            logging.info(f"Unable to load data from folder {folder_name}")
            return False

        # load the data
        o_load = LoadFiles(parent=self.parent,
                           folder=folder_name)
        data = o_load.retrieve_data()

        o_get = TofCombineGet(parent=self.parent)
        row = o_get.row_of_that_folder(folder=folder_name)
        self.parent.dict_data_folders[row][TofCombineSessionKeys.data] = data

        return True

    def combine_algorithm_changed(self):
        if self.no_data_loaded:
            return

        o_get = TofCombineGet(parent=self.parent)
        combine_algorithm = o_get.combine_algorithm()

        self.parent.session[TofCombineSessionKeys.combine_algorithm] = combine_algorithm
        logging.info(f"Algorithm to combine changed to: {combine_algorithm}")
        self.combine_folders()
        self.display_profile()

    def combine_folders(self):
        if self.no_data_loaded:
            return

        o_combine = Combine(parent=self.parent)
        o_combine.run()

    def combine_roi_changed(self):
        live_combine_image = self.parent.live_combine_image
        image_view = self.parent.combine_image_view
        roi_item = self.parent.combine_roi_item_id

        region = roi_item.getArraySlice(live_combine_image,
                                        image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop - 1
        y0 = region[0][1].start
        y1 = region[0][1].stop - 1

        width = x1 - x0
        height = y1 - y0

        self.parent.combine_roi = {'x0': x0,
                                   'y0': y0,
                                   'width': width,
                                   'height': height}

    def display_profile(self):
        if self.no_data_loaded:
            return

        combine_data = self.parent.combine_data

        if combine_data is None:
            self.parent.combine_profile_view.clear()
            return

        x0 = self.parent.combine_roi['x0']
        y0 = self.parent.combine_roi['y0']
        width = self.parent.combine_roi['width']
        height = self.parent.combine_roi['height']

        o_get = TofCombineGet(parent=self.parent)
        combine_algorithm = o_get.combine_algorithm()
        time_spectra_x_axis_name = o_get.combine_x_axis_selected()

        profile_signal = [np.mean(_data[y0:y0 + height, x0:x0 + width]) for _data in combine_data]
        # if combine_algorithm == CombineAlgorithm.mean:
        #     profile_signal = [np.mean(_data[y0:y0+height, x0:x0+width]) for _data in combine_data]
        # elif combine_algorithm == CombineAlgorithm.median:
        #     profile_signal = [np.median(_data[y0:y0+height, x0:x0+width]) for _data in combine_data]
        # else:
        #     raise NotImplementedError("Combine algorithm not implemented!")

        self.parent.profile_signal = profile_signal
        self.parent.combine_profile_view.clear()
        x_axis = copy.deepcopy(self.parent.time_spectra[time_spectra_x_axis_name])

        if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
            x_axis_label = "file index"
        elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
            x_axis *= 1e6    # to display axis in micros
            x_axis_label = "tof (" + MICRO + "s)"
        elif time_spectra_x_axis_name == TimeSpectraKeys.lambda_array:
            x_axis *= 1e10    # to display axis in Angstroms
            x_axis_label = LAMBDA + "(" + ANGSTROMS + ")"

        self.parent.combine_profile_view.plot(x_axis, profile_signal, pen='r', symbol='x')
        self.parent.combine_profile_view.setLabel("left", f"{combine_algorithm} counts")
        self.parent.combine_profile_view.setLabel("bottom", x_axis_label)

    def fix_linear_bin_radio_button_max_values(self):
        time_spectra = self.parent.time_spectra

        file_index_array = time_spectra[TimeSpectraKeys.file_index_array]
        max_file_index = int(len(file_index_array))

        tof_array = time_spectra[TimeSpectraKeys.tof_array]
        max_tof = float(tof_array[-1]) * 1e6
        min_tof = float(tof_array[0]) * 1e6

        lambda_array = time_spectra[TimeSpectraKeys.lambda_array]
        max_lambda = float(lambda_array[-1]) * 1e10
        min_lambda = float(lambda_array[0]) * 1e10

        logging.info(f"Max values of bin linear spin box has been fixed:")
        logging.info(f"-> file index: {max_file_index}")
        logging.info(f"-> tof: {min_tof =} to {max_tof =}")
        logging.info(f"-> lambda: {min_lambda =} to {max_lambda =}")
