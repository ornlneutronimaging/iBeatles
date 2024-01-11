import os
from qtpy.QtWidgets import QFileDialog
import logging
import numpy as np

from ibeatles import DataType
from ibeatles.session import SessionSubKeys
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
from ibeatles.utilities.load_files import LoadFiles

from ibeatles.tools.utilities.time_spectra import GetTimeSpectraFilename, TimeSpectraHandler
from ibeatles.tools.utilities import TimeSpectraKeys


class EventHandler:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def check_widgets(self):
        folder_selected = self.parent.ui.folder_selected.text()
        if os.path.exists(folder_selected):
            enabled_state = True
        else:
            enabled_state = False

        self.parent.ui.bin_tabWidget.setEnabled(enabled_state)
        self.parent.ui.x_axis_groupBox.setEnabled(enabled_state)
        self.parent.ui.stats_tabWidget.setEnabled(enabled_state)
        self.parent.ui.bin_bottom_tabWidget.setEnabled(enabled_state)
        self.parent.ui.bin_settings_pushButton.setEnabled(enabled_state)
        self.parent.ui.export_bin_table_pushButton.setEnabled(enabled_state)
        self.parent.ui.export_pushButton.setEnabled(enabled_state)

    def select_input_folder(self):
        default_path = self.top_parent.session_dict[DataType.sample][SessionSubKeys.current_folder]
        folder = str(QFileDialog.getExistingDirectory(caption="Select folder containing images to load",
                                                      directory=default_path,
                                                      options=QFileDialog.ShowDirsOnly))
        if folder == "":
            logging.info("User Canceled the selection of folder!")
            return

        list_tif_files = FileHandler.get_list_of_tif(folder=folder)
        if not list_tif_files:
            logging.info(f"-> folder does not contain any tif file!")
            show_status_message(parent=self.parent,
                                message=f"Folder {os.path.basename(folder)} does not contain any TIFF files!",
                                duration_s=5,
                                status=StatusMessageStatus.error)
            return

        self.parent.ui.folder_selected.setText(folder)
        logging.info(f"Users selected the folder: {folder}")
        self.parent.list_tif_files = list_tif_files

    def load_data(self):
        dict = LoadFiles.load_interactive_data(parent=self.parent,
                                               list_tif_files=self.parent.list_tif_files)
        self.parent.image_size['height'] = dict['height']
        self.parent.image_size['width'] = dict['width']
        self.parent.images_array = dict['image_array']
        self.parent.integrated_image = np.mean(dict['image_array'], axis=0)

    def load_time_spectra_file(self):
        """
        load the time spectra file
        """
        folder = self.parent.ui.folder_selected.Text()

        o_time_spectra = GetTimeSpectraFilename(parent=self.parent, folder=folder)
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

    def display_profile(self):

        if self.parent.integrated_image is None:
            return

        # o_get = Get(parent=self.parent)
        # combine_algorithm = o_get.combine_algorithm()
        # time_spectra_x_axis_name = o_get.combine_x_axis_selected()
        #
        # profile_signal = [
        #     np.mean(_data[y0 : y0 + height, x0 : x0 + width]) for _data in combine_data
        # ]
        # # if combine_algorithm == CombineAlgorithm.mean:
        # #     profile_signal = [np.mean(_data[y0:y0+height, x0:x0+width]) for _data in combine_data]
        # # elif combine_algorithm == CombineAlgorithm.median:
        # #     profile_signal = [np.median(_data[y0:y0+height, x0:x0+width]) for _data in combine_data]
        # # else:
        # #     raise NotImplementedError("Combine algorithm not implemented!")
        #
        # self.parent.profile_signal = profile_signal
        # self.parent.combine_profile_view.clear()
        # x_axis = copy.deepcopy(self.parent.time_spectra[time_spectra_x_axis_name])
        #
        # if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
        #     x_axis_label = "file index"
        # elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
        #     x_axis *= 1e6  # to display axis in micros
        #     x_axis_label = "tof (" + MICRO + "s)"
        # elif time_spectra_x_axis_name == TimeSpectraKeys.lambda_array:
        #     x_axis *= 1e10  # to display axis in Angstroms
        #     x_axis_label = LAMBDA + "(" + ANGSTROMS + ")"
        #
        # self.parent.combine_profile_view.plot(x_axis, profile_signal, pen="r", symbol="x")
        # self.parent.combine_profile_view.setLabel("left", f"{combine_algorithm} counts")
        # self.parent.combine_profile_view.setLabel("bottom", x_axis_label)