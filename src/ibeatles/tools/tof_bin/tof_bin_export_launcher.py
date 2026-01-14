#!/usr/bin/env python
"""
TOF bin export launcher
"""

import json
import logging
import os
import warnings

import numpy as np
from NeuNorm.normalization import Normalization
from qtpy.QtWidgets import QApplication, QDialog, QFileDialog

from ibeatles import DataType, load_ui
from ibeatles.core.detector import compute_counts_with_uncertainty
from ibeatles.session import SessionSubKeys
from ibeatles.tools.tof_bin.event_handler import EventHandler as TofBinEventHandler
from ibeatles.tools.tof_bin.utilities.get import Get
from ibeatles.tools.tof_bin.utilities.time_spectra import export_time_stamp_file
from ibeatles.tools.tof_bin.utilities.units import (
    convert_from_wavelength_to_energy_ev,
)
from ibeatles.tools.utilities import CombineAlgorithm, TimeSpectraKeys
from ibeatles.tools.utilities.reload.reload import Reload
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.utilities.status_message_config import (
    StatusMessageStatus,
    show_status_message,
)

warnings.filterwarnings("ignore")

# label for combobox
NONE = "None"
FULL_IMAGE_LABEL = "Full image"
ROI_LABEL = "Images of ROI selected"


class ExportDataType:
    """Type of image to export, either the full image or only the roi selected"""

    full_image = "full_image"
    roi = "roi"


class TofBinExportLauncher(QDialog):
    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent
        QDialog.__init__(self, parent=parent)
        self.ui = load_ui("ui_tof_bin_export.ui", baseinstance=self)
        self.update_buttons()

    def update_buttons(self):
        self.ui.reload_full_image_checkBox.setEnabled(self.ui.rebin_full_images_checkBox.isChecked())

    def rebin_full_image_checkBox_clicked(self):
        self.update_buttons()

    def bin_and_export_radio_button_clicked(self):
        pass

    # def _at_least_one_image_checked(self):
    #     """we need to check if at least one bin/export option has been checked"""
    #     if self.ui.full_image_checkBox.isChecked():
    #         return True

    #     if self.ui.roi_checkBox.isChecked():
    #         return True

    #     return False

    def bin_and_export(self, output_folder=None, data_type=ExportDataType.full_image):
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
        self.parent.eventProgress.setMaximum(number_of_bins - 1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        file_info_dict = {}
        number_of_files_created = 0

        counts_array = []

        for _index, _bin in enumerate(file_index_array):
            logging.info(f" working with bin#{_index}")

            if len(_bin) == 0:
                logging.info(" -> empty bin, skipping!")
                self.parent.eventProgress.setValue(_index + 1)
                continue

            short_file_name = f"image_{_index:04d}.tif"
            output_file_name = os.path.join(output_folder, short_file_name)

            # create array of that bin
            _image = self.extract_data_for_this_bin(
                list_runs=_bin,
                full_image_flag=(data_type == ExportDataType.full_image),
            )

            # full image export
            counts_array.append(int(np.sum(_image)))
            o_norm = Normalization()
            o_norm.load(data=_image)
            o_norm.data["sample"]["file_name"][0] = os.path.basename(output_file_name)
            o_norm.export(folder=output_folder, data_type="sample", file_type="tiff")
            logging.info(f" -> exported {output_file_name}")

            file_info_dict[short_file_name] = {
                "file_index": _bin,
                "tof": tof_array[_index],
                "lambda": lambda_array[_index],
            }
            number_of_files_created += 1
            self.parent.eventProgress.setValue(_index + 1)
            QApplication.processEvents()

        # export the json file
        metadata_file_name = os.path.join(output_folder, "metadata.json")
        with open(metadata_file_name, "w") as json_file:
            json.dump(file_info_dict, json_file)

        self.parent.eventProgress.setVisible(False)
        QApplication.processEvents()

        # export the new time stamp file
        export_time_stamp_file(
            counts_array=counts_array,
            tof_array=self.parent.time_spectra[TimeSpectraKeys.tof_array],
            file_index_array=file_index_array,
            export_folder=output_folder,
        )

    def ok_clicked(self):
        logging.info("User clicked OK to export binned images")

        # check first if we want with experimental errors or not
        if self.ui.use_experimental_errors_radioButton.isChecked():
            logging.info("\tUser wants to use experimental errors")
            shutter_counts_file = self.parent.shutter_counts_file
            logging.info(f"\tShutter counts file used: {shutter_counts_file}")

            if shutter_counts_file is None or not os.path.exists(shutter_counts_file):
                logging.info(f"Shutter counts file not found: {shutter_counts_file}")
                logging.info("User will browse for the shutter count file")
                o_event = TofBinEventHandler(parent=self.parent, top_parent=self.top_parent)
                o_event.browse_for_shutter_counts_file()

        self.ok_clicked_step2()

    def ok_clicked_step2(self):
        working_dir = self.top_parent.session_dict[DataType.sample][SessionSubKeys.current_folder]

        message = "Working on exporting files ..."
        show_status_message(
            parent=self.parent,
            message=message,
            status=StatusMessageStatus.working,
        )

        _folder = str(
            QFileDialog.getExistingDirectory(
                caption="Select Folder to export binned Images",
                directory=working_dir,
                options=QFileDialog.ShowDirsOnly,
            )
        )

        if _folder == "":
            logging.info("User cancel export binned images!")
            self.close()
            return

        self.close()

        # define output folder names
        base_folder_name = os.path.basename(os.path.dirname(self.parent.list_tif_files[0]))
        time_stamp = FileHandler.get_current_timestamp()

        nbr_output_created_dict = {"images": 0, "ascii": 0}

        output_folder_full_image = ""
        if self.ui.rebin_full_images_checkBox.isChecked():
            output_folder_full_image = os.path.join(_folder, f"{base_folder_name}_full_image_binned_{time_stamp}")
            self.bin_and_export(
                output_folder=output_folder_full_image,
                data_type=ExportDataType.full_image,
            )
            nbr_output_created_dict["images"] += 1

        if self.ui.rebin_roi_selected_checkBox.isChecked():
            output_folder_roi = os.path.join(_folder, f"{base_folder_name}_roi_binned_{time_stamp}")
            self.bin_and_export(
                output_folder=output_folder_roi,
                data_type=ExportDataType.roi,
            )
            nbr_output_created_dict["images"] += 1

        if self.ui.ascii_full_image_checkBox.isChecked():
            output_file_name = os.path.join(_folder, f"{base_folder_name}_full_image_binned_{time_stamp}.txt")
            self.export_ascii(
                add_uncertainties=self.ui.use_experimental_errors_radioButton.isChecked(),
                data_type=ExportDataType.full_image,
                output_file_name=output_file_name,
            )
            nbr_output_created_dict["ascii"] += 1

        if self.ui.ascii_roi_selected_checkBox.isChecked():
            output_file_name = os.path.join(_folder, f"{base_folder_name}_roi_binned_{time_stamp}.txt")
            self.export_ascii(
                add_uncertainties=self.ui.use_experimental_errors_radioButton.isChecked(),
                data_type=ExportDataType.roi,
                output_file_name=output_file_name,
            )
            nbr_output_created_dict["ascii"] += 1

        # reload if user requested it
        want_to_reload = (
            self.ui.reload_full_image_checkBox.isEnabled() and self.ui.reload_full_image_checkBox.isChecked()
        )
        if not want_to_reload:
            logging.info("Nothing to reload, we are done here!")
            message = (
                f"{nbr_output_created_dict['images']} binned images and {nbr_output_created_dict['ascii']} "
                + "ASCII files created successfully!"
            )
            show_status_message(
                parent=self.parent,
                message=message,
                status=StatusMessageStatus.ready,
                duration_s=15,
            )

        else:
            if os.path.exists(output_folder_full_image):
                o_reload = Reload(parent=self.parent, top_parent=self.top_parent)
                o_reload.run(data_type=DataType.normalized, output_folder=output_folder_full_image)
                self.parent.close()

    def compute_counts_array_only(self, tiff_stack=None, roi_mask=None):
        """Compute counts array for a given tiff stack and roi mask.

        :param tiff_stack: The tiff stack to process.
        :param roi_mask: The roi mask to apply.
        """
        if roi_mask is not None:
            _tiff_stack = [tiff[roi_mask] for tiff in tiff_stack]
        else:
            _tiff_stack = tiff_stack

        counts_array = np.sum(_tiff_stack, axis=1)
        return counts_array

    def export_ascii(self, add_uncertainties=False, data_type=ExportDataType.full_image, output_file_name=None):
        """Export TOF binned data to an ASCII text file.

        The exported file contains, for each active bin: bin index, mean time-of-flight,
        mean wavelength, mean energy, total counts, and the associated uncertainty.

        :param add_uncertainties: If True, compute and include experimental uncertainties
            using shutter counts data. If False, uncertainties are set to NaN.
        :param data_type: Type of data to export. Use ExportDataType.full_image for
            full detector image or ExportDataType.roi for the selected ROI.
        :param output_file_name: Path to the ASCII file to create.
        """

        if data_type == ExportDataType.roi:
            bin_roi = self.parent.bin_roi
            x0 = bin_roi["x0"]
            y0 = bin_roi["y0"]
            width = bin_roi["width"]
            height = bin_roi["height"]
            roi_mask = np.zeros(self.parent.images_array[0].shape, dtype=bool)
            roi_mask[y0 : y0 + height, x0 : x0 + width] = True
            logging.info(f"Exporting ASCII for ROI: x0={x0}, y0={y0}, width={width}, height={height}")

        else:
            roi_mask = None
            logging.info("Exporting ASCII for full image")

        metadata_lines = ["# bin index\tmean_tof (micros)\tmean_lambda (Angstroms)\tmean_energy (meV)\ttotal_counts"]
        if add_uncertainties:
            logging.info("Adding experimental uncertainties to the exported ASCII file")
            # calculate uncertainties of all images
            result_full = compute_counts_with_uncertainty(
                tiff_stack=self.parent.images_array,
                roi_mask=roi_mask,
                tof_array=self.parent.time_spectra[TimeSpectraKeys.tof_array],
                shutter_counts_file=self.parent.shutter_counts_file,
            )

            logging.info(f"result_full: {result_full}")
            logging.info(f"result_full keys: {list(result_full.keys())}")
            counts_array = list(result_full["counts"])
            uncertainties_array = list(result_full["uncertainty"])
            metadata_lines[0] += "\tuncertainty"

        else:
            counts_array = self.compute_counts_array_only(tiff_stack=self.parent.images_array, roi_mask=roi_mask)

        # format of the output ascii file
        # index, start tof, end tof, start lambda, end lambda, start energy, end energy, total counts, uncertainty
        o_get = Get(parent=self.parent)
        bins_dict = o_get.current_bins_activated()
        file_index_array = bins_dict[TimeSpectraKeys.file_index_array]
        logging.info(f"{file_index_array = }")
        statistics_dict = self.parent.statistics_dict

        logging.info(f"\t{statistics_dict = }")

        data_lines = []

        for _bin_index in statistics_dict.keys():
            list_file_index = statistics_dict[_bin_index]["list_file"]
            logging.info(f"\tProcessing bin index {_bin_index} with file indices {list_file_index}")

            if list_file_index is None:
                logging.info(f"\tSkipping bin index {_bin_index} as it has no files.")
                continue

            list_total_counts = [counts_array[_file_index] for _file_index in list_file_index]
            logging.info(f"\t{list_total_counts = }")
            mean_counts = np.mean(list_total_counts)
            logging.info(f"\t{mean_counts = }")

            if add_uncertainties:
                _uncertainties_array = [uncertainties_array[_file_index] for _file_index in list_file_index]
                uncertainty = self.calculate_uncertainty_of_mean(_uncertainties_array)

            list_lambda = statistics_dict[_bin_index]["list_lambda"]
            average_lambda = np.mean(list_lambda)
            average_energy = convert_from_wavelength_to_energy_ev(average_lambda)

            list_tof = statistics_dict[_bin_index]["list_tof"]
            average_tof = np.mean(list_tof)

            if add_uncertainties:
                data_lines.append(
                    f"{_bin_index}\t{average_tof:.6f}\t{average_lambda:.6f}\t{average_energy:.6f}\t{mean_counts:.2f}\t{uncertainty:.2f}"
                )
            else:
                data_lines.append(
                    f"{_bin_index}\t{average_tof:.6f}\t{average_lambda:.6f}\t{average_energy:.6f}\t{mean_counts:.2f}"
                )

        # write the output ascii file
        logging.info(f"Writing ASCII file to {output_file_name}")
        with open(output_file_name, "w") as fout:
            for _line in metadata_lines:
                fout.write(f"{_line}\n")
            for _line in data_lines:
                fout.write(f"{_line}\n")

    def calculate_uncertainty_of_mean(self, list_uncertainties):
        """calculate the uncertainty of the mean of counts
        assuming the uncertainties are independent

        :param
        list_uncertainties: list of uncertainties to mean
        :return:
            uncertainty of the mean
        """
        n = len(list_uncertainties)

        sum_squared = 0.0
        for _uncertainty in list_uncertainties:
            sum_squared += _uncertainty**2

        return np.sqrt(sum_squared) / np.sqrt(n)

    def extract_data_for_this_bin(self, list_runs=None, full_image_flag=True):
        """
        this method isolate the data of only the runs of the corresponding runs if full_image is True,
        otherwise will return the ROI selected

        :param
        list_runs: list of runs to extract
        full_image_flag: True of False (False if we want only the ROI selected)
        :return:
            image binned
        """

        data_to_work_with = []
        for _run_index in list_runs:
            data_to_work_with.append(self.parent.images_array[_run_index])

        if not full_image_flag:
            bin_roi = self.parent.bin_roi
            x0 = bin_roi["x0"]
            y0 = bin_roi["y0"]
            width = bin_roi["width"]
            height = bin_roi["height"]
            region_to_work_with = [_data[y0 : y0 + height, x0 : x0 + width] for _data in data_to_work_with]
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

        return image_to_export
