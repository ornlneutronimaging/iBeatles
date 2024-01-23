from qtpy.QtWidgets import QDialog
from qtpy.QtWidgets import QFileDialog
import logging
import os
import numpy as np

import warnings
warnings.filterwarnings("ignore")

from NeuNorm.normalization import Normalization

from ibeatles import load_ui
from ibeatles import DataType
from ibeatles.session import SessionSubKeys
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.tools.utilities import TimeSpectraKeys
from ibeatles.tools.utilities import CombineAlgorithm

from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
from ibeatles.tools.tof_bin.utilities.get import Get


class TofBinExportLauncher(QDialog):

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent
        QDialog.__init__(self, parent=parent)
        self.ui = load_ui('ui_tof_bin_export.ui', baseinstance=self)

    def bin_and_export_radio_button_clicked(self):
        self.check_buttons()

    def check_buttons(self):
        """ok disabled if we don't have anything to export
        reload group is also disable if nothing to export
        """
        if not self._at_least_one_image_checked():
            self.ui.ok_pushButton.setEnabled(False)
            self.ui.reload_groupBox.setEnabled(False)
        else:
            self.ui.ok_pushButton.setEnabled(True)
            self.ui.reload_groupBox.setEnabled(True)

    def _at_least_one_image_checked(self):
        """we need to check if at least one bin/export option has been checked"""
        if self.ui.full_image_checkBox.isChecked():
            return True

        if self.ui.roi_checkBox.isChecked():
            return True

        return False

    def bin_and_export(self, output_folder=None, data_type='full_image'):
        logging.info(f"binning and exporting {data_type}:")
        FileHandler.make_or_reset_folder(output_folder)
        logging.info(f" -> exported to {output_folder}")

        o_get = Get(parent=self.parent)
        bins_dict = o_get.current_bins_activated()
        number_of_bins = len(bins_dict[TimeSpectraKeys.file_index_array])

        file_index_array = bins_dict[TimeSpectraKeys.file_index_array]
        tof_array = bins_dict[TimeSpectraKeys.tof_array]
        lambda_array = bins_dict[TimeSpectraKeys.lambda_array]

        # initialize progress bar
        self.parent.eventProgress.setMinimum(0)
        self.parent.eventProgress.setMaximum(number_of_bins-1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        file_info_dict = {}
        number_of_files_created = 0

        counts_array = []

        for _index, _bin in enumerate(file_index_array):

            logging.info(f" working with bin#{_index}")

            if len(_bin) == 0:
                logging.info(f" -> empty bin, skipping!")
                self.parent.eventProgress.setValue(_index + 1)
                continue

            short_file_name = f"image_{_index:04d}.tif"
            output_file_name = os.path.join(output_folder, short_file_name)

            # create array of that bin
            _data_dict = self.extract_data_for_this_bin(list_runs=_bin)

            # full image export
            full_image = _data_dict['full_image']
            counts_array_full_image.append(int(np.sum(full_image)))
            o_norm = Normalization()
            o_norm.load(data=full_image)
            o_norm.data['sample']['file_name'][0] = os.path.basename(output_file_name_full_image)
            o_norm.export(folder=output_folder_full_image, data_type='sample', file_type='tiff')
            logging.info(f" -> exported {output_file_name_full_image}")

            # roi image export
            roi_image = _data_dict['roi_of_image']
            counts_array_roi.append(int(np.sum(roi_image)))
            o_norm = Normalization()
            o_norm.load(data=roi_image)
            o_norm.data['sample']['file_name'][0] = os.path.basename(output_file_name_roi)
            o_norm.export(folder=output_folder_roi, data_type='sample', file_type='tiff')
            logging.info(f" -> exported {output_file_name_roi}")

            file_info_dict[short_file_name] = {'file_index': _bin,
                                               'tof': tof_array[_index],
                                               'lambda': lambda_array[_index]}
            number_of_files_created += 1
            self.parent.eventProgress.setValue(_index + 1)

    def ok_clicked(self):
        working_dir = self.top_parent.session_dict[DataType.sample][SessionSubKeys.current_folder]

        _folder = str(QFileDialog.getExistingDirectory(caption="Select Folder to export binned Images",
                                                       directory=working_dir,
                                                       options=QFileDialog.ShowDirsOnly))

        if _folder == "":
            logging.info("User cancel export binned images!")
            self.close()
            return

        self.close()

        # define output folder names
        base_folder_name = os.path.basename(os.path.dirname(self.parent.list_tif_files[0]))
        time_stamp = FileHandler.get_current_timestamp()

        if self.ui.full_image_checkBox.isChecked():

            output_folder_full_image = os.path.join(_folder, f"{base_folder_name}_full_image_binned_{time_stamp}")
            self.bin_and_export(output_folder=output_folder_full_image,
                                )

        if self.ui.roi_checkBox.isChecked():

            output_folder_roi = os.path.join(_folder, f"{base_folder_name}_roi_binned_{time_stamp}")
            self.bin_and_export(output_folder=output_folder_roi,
                                )




        file_info_dict = {}
        number_of_files_created = 0

        counts_array_full_image = []
        counts_array_roi = []

        for _index, _bin in enumerate(file_index_array):

            logging.info(f" working with bin#{_index}")

            if len(_bin) == 0:
                logging.info(f" -> empty bin, skipping!")
                self.parent.eventProgress.setValue(_index + 1)
                continue

            short_file_name = f"image_{_index:04d}.tif"
            output_file_name_full_image = os.path.join(output_folder_full_image, short_file_name)
            output_file_name_roi = os.path.join(output_folder_roi, short_file_name)

            # create array of that bin
            _data_dict = self.extract_data_for_this_bin(list_runs=_bin)

            # full image export
            full_image = _data_dict['full_image']
            counts_array_full_image.append(int(np.sum(full_image)))
            o_norm = Normalization()
            o_norm.load(data=full_image)
            o_norm.data['sample']['file_name'][0] = os.path.basename(output_file_name_full_image)
            o_norm.export(folder=output_folder_full_image, data_type='sample', file_type='tiff')
            logging.info(f" -> exported {output_file_name_full_image}")

            # roi image export
            roi_image = _data_dict['roi_of_image']
            counts_array_roi.append(int(np.sum(roi_image)))
            o_norm = Normalization()
            o_norm.load(data=roi_image)
            o_norm.data['sample']['file_name'][0] = os.path.basename(output_file_name_roi)
            o_norm.export(folder=output_folder_roi, data_type='sample', file_type='tiff')
            logging.info(f" -> exported {output_file_name_roi}")

            file_info_dict[short_file_name] = {'file_index': _bin,
                                               'tof': tof_array[_index],
                                               'lambda': lambda_array[_index]}
            number_of_files_created += 1
            self.parent.eventProgress.setValue(_index + 1)


        self.parent.eventProgress.setVisible(False)

        # o_get = Get(parent=self)
        # data_type_selected = o_get.combine_export_mode()
        # self.close()
        # output_folder = self.parent.combine_run(data_type_selected=data_type_selected)
        # if output_folder:
        #     self.parent.reload_run_in_main_ui(data_type_selected=data_type_selected,
        #                                       output_folder=output_folder)
        #     self.parent.close()
        #
        #     message = f"TOF combined exported to {output_folder}"
        #     if not (data_type_selected == DataType.none):
        #         message += f" and loaded back in {data_type_selected}"
        #     message += "!"
        #     status = StatusMessageStatus.ready
        #
        # else:
        #     message = "User cancel export process!"
        #     status = StatusMessageStatus.warning
        #
        # show_status_message(parent=self.grand_parent,
        #                     message=message,
        #                     status=status,
        #                     duration_s=10)

    def extract_data_for_this_bin(self, list_runs=None, full_image=True):
        """
        this method isolate the data of only the runs of the corresponding runs if full_image is True,
        otherwise will return the ROI selected

        :param list_runs:
        :return:
            image binned
        """

        data_to_work_with = []
        for _run_index in list_runs:
            data_to_work_with.append(self.parent.images_array[_run_index])

        if not full_image:
            bin_roi = self.parent.bin_roi
            x0 = bin_roi['x0']
            y0 = bin_roi['y0']
            width = bin_roi['width']
            height = bin_roi['height']
            region_to_work_with = [_data[y0: y0+height, x0: x0+width] for _data in data_to_work_with]
            data_to_work_with = region_to_work_with

        # how to add images
        o_get = Get(parent=self.parent)
        bin_method = o_get.bin_add_method()
        if bin_method == CombineAlgorithm.mean:
            image_to_export = np.mean(data_to_work_with, axis=0)
        elif bin_method == CombineAlgorithm.median:
            image_to_export = np.median(data_to_work_with, axis=0)
        else:
            raise NotImplementedError("this method of adding the binned images is not supported!")

        return {'full_image': image_to_export,
                }
