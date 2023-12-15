import os
from qtpy.QtWidgets import QFileDialog, QCheckBox
import logging
import numpy as np
import copy

from ibeatles.session import SessionSubKeys
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

        o_get = TofCombineGet(parent=parent)
        list_working_folders = o_get.list_of_folders_to_use()
        if list_working_folders == [None]:
            self.no_data_loaded = True

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
        list_folders = FileHandler.get_list_of_folders(folder)
        self.parent.list_folders = list_folders
        self.parent.top_folder = folder

        # initialize parameters when using new working folder
        self.reset_data()

        # # display the full path of the top folder selected
        self.parent.ui.top_folder_label.setText(folder)
        #
        # # display list of folders in widget and column showing working folders used
        self.populate_list_of_folders_to_combine()
        #
        # # update ui
        # self.check_widgets()

    def check_widgets(self):
        o_get = TofCombineGet(parent=self.parent)

        if (o_get.list_of_folders_to_use() == []) or (o_get.list_of_folders_to_use() is None):
            self.parent.ui.combine_refresh_top_folder_pushButton.setEnabled(False)
            self.parent.ui.combine_bin_tabWidget.setTabEnabled(1, False)
            self.parent.ui.combine_widget.setEnabled(False)
        else:
            self.parent.ui.combine_refresh_top_folder_pushButton.setEnabled(True)
            self.parent.ui.combine_bin_tabWidget.setTabEnabled(1, True)
            self.parent.ui.combine_widget.setEnabled(True)

    def refresh_table_clicked(self):
        self.logger.info("User clicked the refresh table!")
        top_folder = self.parent.top_folder

        list_folders = FileHandler.get_list_of_folders(top_folder)
        # checking if there is any new folder
        current_list_of_folders = self.parent.session[SessionKeys.list_working_folders]
        for _folder in list_folders:
            if not (_folder in current_list_of_folders):
                self.parent.session[SessionKeys.list_working_folders].append(_folder)
                self.parent.session[SessionKeys.list_working_folders_status].append(False)

                list_files = FileHandler.get_list_of_files(_folder)
                nbr_files = len(list_files)
                data = {'data': None,
                        'list_files': list_files,
                        'nbr_files': nbr_files}
                self.parent.raw_data_folders[_folder] = data
                self.insert_row_entry(_folder)

    def reset_data(self):
        """
        This re-initialize all the parameters when working with a new top folder
        """

        # reset master dictionary that contains the raw data
        list_folders = self.parent.list_folders
        if list_folders is None:
            return

        _data_dict = {}
        for _folder in list_folders:
            list_files = FileHandler.get_list_of_tif(_folder)
            nbr_files = len(list_files)
            _data_dict[_folder] = {'data': None,
                                   'list_files': list_files,
                                   'nbr_files': nbr_files,
                                   }
        self.parent.raw_data_folders = _data_dict

        # initialize list of selected folders
        # self.parent.session[SessionKeys.list_working_folders_status] = [False for _index in np.arange(len(list_folders))]

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
        list_of_folders = self.parent.list_folders
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        o_table.remove_all_rows()

        if list_of_folders is None:
            return

        for _folder in list_of_folders:
            self.insert_row_entry(folder=_folder)

    def insert_row_entry(self, folder=None):
        
        list_of_folders_status = self.parent.list_of_folders_status
        raw_data_folders = self.parent.raw_data_folders

        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        row = o_table.row_count()
        o_table.insert_empty_row(row=row)

        # use or not that row
        check_box = QCheckBox()
        if list_of_folders_status is None:
            status = False
        else:
            status = list_of_folders_status[row]
        check_box.setChecked(status)

        # check if this file has more than 1 file
        # if not disable radio button
        # number of images in that folder
        nbr_files = raw_data_folders[folder]['nbr_files']
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
                            value=folder,
                            editable=False)

    def update_list_of_folders_to_use(self, force_recalculation_of_time_spectra=False):
        o_get = Get(parent=self.parent)
        list_of_folders_to_use = o_get.list_of_folders_to_use()

        # o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        # nbr_row = o_table.row_count()
        # list_of_folders_to_use = []
        # list_of_folders_to_use_status = []
        # for _row_index in np.arange(nbr_row):
        #     _horizontal_widget = o_table.get_widget(row=_row_index,
        #                                             column=0)
        #     radio_button = _horizontal_widget.layout().itemAt(1).widget()
        #     if radio_button.isChecked():
        #         list_of_folders_to_use.append(o_table.get_item_str_from_cell(row=_row_index,
        #                                                                      column=2))
        #         status = True
        #     else:
        #         status = False
        #     list_of_folders_to_use_status.append(status)
        #
        # self.parent.session[SessionKeys.list_working_folders_status] = list_of_folders_to_use_status

        self.logger.info("Updating list of folders to use:")
        self.logger.info(f"{list_of_folders_to_use}")

        # check or load the selected rows
        loading_worked = True

        for _folder_name in list_of_folders_to_use:

            if force_recalculation_of_time_spectra:
                self.load_time_spectra_file(folder=_folder_name)
                self.fix_linear_bin_radio_button_max_values()

            if self.parent.raw_data_folders[_folder_name]['data'] is None:
                loading_worked = self.load_that_folder(folder_name=_folder_name)

                # load time spectra if not already there
                if self.parent.time_spectra['file_name'] is None:
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
            self.logger.info(f"Unable to load data from folder {folder_name}")
            return False

        # load the data
        o_load = LoadFiles(parent=self.parent,
                           folder=folder_name)
        data = o_load.retrieve_data()
        self.parent.raw_data_folders[folder_name]['data'] = data

        return True

    def combine_algorithm_changed(self):
        if self.no_data_loaded:
            return

        o_get = Get(parent=self.parent)

        combine_algorithm = o_get.combine_algorithm()
        self.parent.session[SessionKeys.combine_algorithm] = combine_algorithm
        self.logger.info(f"Algorithm to combine changed to: {combine_algorithm}")
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

        self.parent.session[SessionKeys.combine_roi] = [x0, y0, width, height]

    def display_profile(self):
        if self.no_data_loaded:
            return

        combine_data = self.parent.combine_data

        if combine_data is None:
            self.parent.combine_profile_view.clear()
            return

        [x0, y0, width, height] = self.parent.session[SessionKeys.combine_roi]

        o_get = Get(parent=self.parent)
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

        self.parent.ui.auto_linear_file_index_spinBox.setMaximum(max_file_index)
        self.parent.ui.auto_linear_tof_doubleSpinBox.setMaximum(max_tof-min_tof)
        self.parent.ui.auto_linear_lambda_doubleSpinBox.setMaximum(max_lambda-min_lambda)

        self.logger.info(f"Max values of bin linear spin box has been fixed:")
        self.logger.info(f"-> file index: {max_file_index}")
        self.logger.info(f"-> tof: {max_tof}")
        self.logger.info(f"-> lambda: {max_lambda}")
