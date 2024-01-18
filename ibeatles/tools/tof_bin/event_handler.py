import os
from qtpy.QtWidgets import QFileDialog
import logging
import numpy as np
import pyqtgraph as pg
import copy

from ibeatles import DataType
from ibeatles.session import SessionSubKeys
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
from ibeatles.utilities.load_files import LoadFiles

from ibeatles.tools.tof_bin import BinMode, BinAutoMode
from ibeatles.tools.tof_bin.plot import Plot
from ibeatles.tools import ANGSTROMS, LAMBDA, MICRO
from ibeatles.tools.utilities.time_spectra import GetTimeSpectraFilename, TimeSpectraHandler
from ibeatles.tools.tof_bin.utilities.get import Get
from ibeatles.tools.utilities import TimeSpectraKeys
from ibeatles.tools.tof_bin.auto_event_handler import AutoEventHandler
from ibeatles.tools.tof_bin.manual_event_handler import ManualEventHandler

from ibeatles.tools.tof_bin.utilities.get import Get as TofBinGet


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
        self.parent.ui.export_bin_table_pushButton.setEnabled(enabled_state)
        self.parent.ui.export_pushButton.setEnabled(enabled_state)
        self.parent.ui.image_tabWidget.setEnabled(enabled_state)

    def select_input_folder(self):
        default_path = self.top_parent.session_dict[DataType.sample][SessionSubKeys.current_folder]
        folder = QFileDialog.getExistingDirectory(parent=self.parent,
                                                  caption="Select folder containing images to load",
                                                  directory=default_path,
                                                  options=QFileDialog.ShowDirsOnly)

        if folder == "":
            logging.info("User Canceled the selection of folder!")
            show_status_message(parent=self.parent,
                                message=f"User cancelled the file dialog window",
                                duration_s=5,
                                status=StatusMessageStatus.warning)
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
        if not self.parent.list_tif_files:
            return

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
        folder = self.parent.ui.folder_selected.text()

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

    def display_integrated_image(self):
        self.parent.integrated_view.clear()

        if self.parent.integrated_image is None:
            return

        self.parent.integrated_view.setImage(self.parent.integrated_image)

        roi = self.parent.bin_roi
        x0 = roi['x0']
        y0 = roi['y0']
        width = roi['width']
        height = roi['height']
        roi_item = pg.ROI([x0, y0], [width, height])
        roi_item.addScaleHandle([1, 1], [0, 0])
        self.parent.integrated_view.addItem(roi_item)
        roi_item.sigRegionChanged.connect(self.parent.bin_roi_changed)
        self.parent.roi_item = roi_item

    def display_profile(self):

        if self.parent.integrated_image is None:
            return

        integrated_image = self.parent.integrated_image
        image_view = self.parent.integrated_view
        roi_item = self.parent.roi_item

        region = roi_item.getArraySlice(integrated_image,
                                        image_view.imageItem)
        x0 = region[0][0].start
        x1 = region[0][0].stop - 1
        y0 = region[0][1].start
        y1 = region[0][1].stop - 1

        width = x1 - x0
        height = y1 - y0

        self.parent.bin_roi = {'x0': x0,
                               'y0': y0,
                               'width': width,
                               'height': height}

        o_plot = Plot(parent=self.parent)
        o_plot.refresh_profile_plot()

        # o_get = TofBinGet(parent=self.parent)
        # time_spectra_x_axis_name = o_get.x_axis_selected()
        # x_axis = copy.deepcopy(self.parent.time_spectra[time_spectra_x_axis_name])
        #
        # array_of_data = self.parent.images_array
        # profile_signal = [np.mean(_data[y0:y0 + height, x0:x0 + width]) for _data in array_of_data]
        #
        # self.parent.profile_signal = profile_signal
        # self.parent.bin_profile_view.clear()
        #
        # if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
        #     x_axis_label = "file index"
        # elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
        #     x_axis *= 1e6    # to display axis in micros
        #     x_axis_label = "tof (" + MICRO + "s)"
        # elif time_spectra_x_axis_name == TimeSpectraKeys.lambda_array:
        #     x_axis *= 1e10    # to display axis in Angstroms
        #     x_axis_label = LAMBDA + "(" + ANGSTROMS + ")"
        #
        # self.parent.bin_profile_view.plot(x_axis, profile_signal, pen='r', symbol='x')
        # self.parent.bin_profile_view.setLabel("left", f"Average counts")
        # self.parent.bin_profile_view.setLabel("bottom", x_axis_label)




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

    def bin_auto_manual_tab_changed(self, new_tab_index=-1):

        if new_tab_index == -1:
            new_tab_index = self.parent.ui.bin_tabWidget.currentIndex()

        if new_tab_index == 0:
            self.parent.session[SessionSubKeys.bin_mode] = BinMode.auto

        elif new_tab_index == 1:
            self.parent.session[SessionSubKeys.bin_mode] = BinMode.manual

        elif new_tab_index == 2:
            pass

        else:
            raise NotImplementedError("LinearBin mode not implemented!")

        self.entering_tab()

    def entering_tab(self):
        o_get = Get(parent=self.parent)
        if o_get.bin_mode() == BinMode.auto:
            o_auto_event = AutoEventHandler(parent=self.parent)
            if o_get.bin_auto_mode() == BinAutoMode.linear:
                o_auto_event.auto_linear_radioButton_changed()
            elif o_get.bin_auto_mode() == BinAutoMode.log:
                o_auto_event.auto_log_radioButton_changed()
            o_auto_event.refresh_auto_tab()

        elif o_get.bin_mode() == BinMode.manual:
            o_manual_event = ManualEventHandler(parent=self.parent)
            o_manual_event.refresh_manual_tab()
            # o_manual_event.display_all_items()

        else:
            pass
