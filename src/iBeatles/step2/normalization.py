from qtpy.QtWidgets import QFileDialog
import os
import shutil
import logging

from NeuNorm.normalization import Normalization as NeuNormNormalization
from NeuNorm.roi import ROI

from ..step2.roi_handler import Step2RoiHandler
from ..utilities.file_handler import FileHandler
from ..utilities.status_message_config import StatusMessageStatus, show_status_message

from .. import DataType


class Normalization(object):

    coeff_array = 1  # ob / sample of ROI selected
    o_norm = None

    def __init__(self, parent=None):
        self.parent = parent

    def run_and_export(self):

        logging.info("Running and exporting normalization:")

        # ask for output folder location
        sample_folder = self.parent.data_metadata['sample']['folder']
        sample_name = os.path.basename(os.path.dirname(sample_folder))
        default_dir = os.path.dirname(os.path.dirname(sample_folder))
        output_folder = str(
            QFileDialog.getExistingDirectory(caption="Select Where the Normalized folder will be created...",
                                             directory=default_dir,
                                             options=QFileDialog.ShowDirsOnly))

        if not output_folder:
            logging.info(" No output folder selected, normalization stopped!")
            return

        logging.info(f" output folder selected: {output_folder}")
        full_output_folder = os.path.join(output_folder, sample_name + "_normalized")
        FileHandler.make_or_reset_folder(full_output_folder)
        logging.info(f" full output folder will be: {full_output_folder}")

        self.running_normalization(output_folder=full_output_folder)
        self.saving_normalization_parameters(output_folder=full_output_folder)
        self.moving_time_spectra_to_normalizaton_folder(output_folder=full_output_folder)

        # # perform normalization on all images selected
        # self.normalize_full_set(output_folder=output_folder, base_folder_name=sample_name)

    def moving_time_spectra_to_normalizaton_folder(self, output_folder=None):
        logging.info("Copying time spectra file from input folder to output folder.")
        time_spectra = self.parent.data_metadata['sample']['time_spectra']
        filename = time_spectra['filename']
        folder = time_spectra['folder']
        full_time_spectra = os.path.join(folder, filename)
        shutil.copy(full_time_spectra, output_folder)

    def saving_normalization_parameters(self, output_folder=None):
        logging.info("Internally saving normalization parameters (data, folder, time_spectra)")
        o_norm = self.o_norm
        self.parent.data_metadata[DataType.normalized]['data'] = o_norm.get_normalized_data()
        self.parent.data_metadata[DataType.normalized]['folder'] = output_folder
        self.parent.data_metadata[DataType.normalized]['time_spectra'] = \
            self.parent.data_metadata[DataType.sample]['time_spectra']

    def running_normalization(self, output_folder=None):
        logging.info(" running normalization!")
        _data = self.parent.data_metadata['sample']['data']
        _ob = self.parent.data_metadata['ob']['data']

        # no data, nothing to do
        if not _data:
            print("I shouldn't be able to see this!")
            return

        # check if roi selected or not
        o_roi_handler = Step2RoiHandler(parent=self.parent)
        try:  # to avoid valueError when row not fully filled
            list_roi_to_use = o_roi_handler.get_list_of_background_roi_to_use()
        except ValueError:
            logging.info(" Error raised when retrieving the background ROI!")
            return

        logging.info(f" Background list of ROI: {list_roi_to_use}")

        if not _ob:
            # if just sample data
            self.normalization_only_sample_data(_data, list_roi_to_use, output_folder)
        else:
            # if ob
            self.normalization_sample_and_ob_data(_data, _ob, list_roi_to_use, output_folder)

    def normalization_only_sample_data(self, data, list_roi, output_folder):
        logging.info(" running normalization with only sample data ...")

        show_status_message(parent=self.parent,
                            message="Loading data ...",
                            status=StatusMessageStatus.working)
        o_norm = NeuNormNormalization()
        o_norm.load(data=data)
        show_status_message(parent=self.parent,
                            message="Loading data ... Done!",
                            status=StatusMessageStatus.working,
                            duration_s=5)

        list_roi_object = []
        for _roi in list_roi:
            o_roi = ROI(x0=int(_roi[0]),
                        y0=int(_roi[1]),
                        width=int(_roi[2]),
                        height=int(_roi[3]))
            list_roi_object.append(o_roi)

        show_status_message(parent=self.parent,
                            message="Running normalization ...",
                            status=StatusMessageStatus.working)
        o_norm.normalization(roi=list_roi_object,
                             use_only_sample=True)

        self.o_norm = o_norm

        show_status_message(parent=self.parent,
                            message="Running normalization ... Done!",
                            status=StatusMessageStatus.working,
                            duration_s=5)

        show_status_message(parent=self.parent,
                            message="Exporting normalized files ...",
                            status=StatusMessageStatus.working)
        o_norm.export(folder=output_folder)
        show_status_message(parent=self.parent,
                            message="Exporting normalized files ... Done!",
                            status=StatusMessageStatus.working,
                            duration_s=5)

        logging.info(" running normalization with only sample data ... Done!")

    def normalization_sample_and_ob_data(self, data, ob, list_roi, output_folder):
        logging.info(" running normalization with sample and ob data ...")

        # sample
        show_status_message(parent=self.parent,
                            message="Loading sample data ...",
                            status=StatusMessageStatus.working)
        o_norm = NeuNormNormalization()
        o_norm.load(data=data)
        show_status_message(parent=self.parent,
                            message="Loading sample data ... Done!",
                            status=StatusMessageStatus.working)

        # ob
        show_status_message(parent=self.parent,
                            message="Loading ob data ...",
                            status=StatusMessageStatus.working)
        o_norm.load(data=ob, data_type=DataType.ob)
        show_status_message(parent=self.parent,
                            message="Loading ob data ... Done!",
                            status=StatusMessageStatus.working,
                            duration_s=5)

        list_roi_object = []
        for _roi in list_roi:
            o_roi = ROI(x0=int(_roi[0]),
                        y0=int(_roi[1]),
                        width=int(_roi[2]),
                        height=int(_roi[3]))
            list_roi_object.append(o_roi)

        show_status_message(parent=self.parent,
                            message="Running normalization ...",
                            status=StatusMessageStatus.working)
        if list_roi_object:
            o_norm.normalization(roi=list_roi_object)
        else:
            o_norm.normalization()

        self.o_norm = o_norm

        show_status_message(parent=self.parent,
                            message="Running normalization ... Done!",
                            status=StatusMessageStatus.working,
                            duration_s=5)

        show_status_message(parent=self.parent,
                            message="Exporting normalized files ...",
                            status=StatusMessageStatus.working)
        o_norm.export(folder=output_folder)
        show_status_message(parent=self.parent,
                            message="Exporting normalized files ... Done!",
                            status=StatusMessageStatus.working,
                            duration_s=5)

        logging.info(" running normalization with sample and ob data ... Done!")
