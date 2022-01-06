from qtpy.QtWidgets import QFileDialog
import os
import shutil
import logging

from NeuNorm.normalization import Normalization as NeuNormNormalization
from NeuNorm.roi import ROI

from ..step2.roi_handler import Step2RoiHandler
from ..step3.event_handler import EventHandler
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

        o_norm = self.create_o_norm()

        if self.parent.session_dict["reduction"]["processes order"] == "option1":
            # running moving average before running normalization
            o_norm = self.running_moving_average(o_norm=o_norm)
            o_norm = self.running_normalization(o_norm=o_norm)
        else:
            # running normalization then moving average
            o_norm = self.running_normalization(o_norm=o_norm)
            o_norm = self.running_moving_average(o_norm=o_norm)

        if not o_norm:
            logging.info("Normalization failed!")
            show_status_message(parent=self.parent,
                                message="Normalization Failed (check logbook)!",
                                status=StatusMessageStatus.error)
            return

        self.export_normalization(o_norm=o_norm, output_folder=full_output_folder)
        self.saving_normalization_parameters(o_norm=o_norm, output_folder=full_output_folder)
        self.moving_time_spectra_to_normalizaton_folder(output_folder=full_output_folder)

        # repopulate ui with normalized data
        o_step3 = EventHandler(parent=self.parent,
                               data_type=DataType.normalized)
        o_step3.import_button_clicked_automatically(folder=full_output_folder)

    def create_o_norm(self):

        logging.info("Creating o_norm object (to prepare data normalization!")

        _data = self.parent.data_metadata['sample']['data']
        _ob = self.parent.data_metadata['ob']['data']

        show_status_message(parent=self.parent,
                            message="Loading data ...",
                            status=StatusMessageStatus.working)
        o_norm = NeuNormNormalization()
        o_norm.load(data=_data)
        show_status_message(parent=self.parent,
                            message="Loading data ... Done!",
                            status=StatusMessageStatus.working,
                            duration_s=5)

        if _ob:

            show_status_message(parent=self.parent,
                                message="Loading ob data ...",
                                status=StatusMessageStatus.working)
            o_norm.load(data=_ob, data_type=DataType.ob)
            show_status_message(parent=self.parent,
                                message="Loading ob data ... Done!",
                                status=StatusMessageStatus.working,
                                duration_s=5)

        return o_norm

    def export_normalization(self, o_norm=None, output_folder=None):
        show_status_message(parent=self.parent,
                            message="Exporting normalized files ...",
                            status=StatusMessageStatus.working)
        o_norm.export(folder=output_folder)
        show_status_message(parent=self.parent,
                            message="Exporting normalized files ... Done!",
                            status=StatusMessageStatus.working,
                            duration_s=5)

    def moving_time_spectra_to_normalizaton_folder(self, output_folder=None):
        logging.info("Copying time spectra file from input folder to output folder.")
        time_spectra = self.parent.data_metadata['sample']['time_spectra']
        filename = time_spectra['filename']
        folder = time_spectra['folder']
        full_time_spectra = os.path.join(folder, filename)
        shutil.copy(full_time_spectra, output_folder)

    def saving_normalization_parameters(self, o_norm=None, output_folder=None):
        logging.info("Internally saving normalization parameters (data, folder, time_spectra)")
        self.parent.data_metadata[DataType.normalized]['data'] = o_norm.get_normalized_data()
        self.parent.data_metadata[DataType.normalized]['folder'] = output_folder
        self.parent.data_metadata[DataType.normalized]['time_spectra'] = \
            self.parent.data_metadata[DataType.sample]['time_spectra']

    def running_moving_average(self, o_norm=None):

        if o_norm is None:
            return None

        running_moving_average_settings = self.parent.session_dict["reduction"]
        if not running_moving_average_settings["activate"]:
            return o_norm

        return o_norm

    def running_normalization(self, o_norm=None):
        logging.info(" running normalization!")

        # if o_norm is None:
        #     _data = self.parent.data_metadata['sample']['data']
        #     _ob = self.parent.data_metadata['ob']['data']
        # else:
        #     _data = o_norm.data[DataType.sample]['data']
        #     _ob = o_norm.data[DataType.ob]['data']

        # check if roi selected or not
        o_roi_handler = Step2RoiHandler(parent=self.parent)
        try:  # to avoid valueError when row not fully filled
            list_roi_to_use = o_roi_handler.get_list_of_background_roi_to_use()
        except ValueError:
            logging.info(" Error raised when retrieving the background ROI!")
            return None

        logging.info(f" Background list of ROI: {list_roi_to_use}")

        if not o_norm.data['ob']['data']:
            # if just sample data
            return self.normalization_only_sample_data(o_norm, list_roi_to_use)
        else:
            # if ob
            return self.normalization_sample_and_ob_data(o_norm, list_roi_to_use)

    def normalization_only_sample_data(self, o_norm, list_roi):
        logging.info(" running normalization with only sample data ...")

        # show_status_message(parent=self.parent,
        #                     message="Loading data ...",
        #                     status=StatusMessageStatus.working)
        # o_norm = NeuNormNormalization()
        # o_norm.load(data=data)
        # show_status_message(parent=self.parent,
        #                     message="Loading data ... Done!",
        #                     status=StatusMessageStatus.working,
        #                     duration_s=5)

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

        # self.o_norm = o_norm

        show_status_message(parent=self.parent,
                            message="Running normalization ... Done!",
                            status=StatusMessageStatus.working,
                            duration_s=5)

        logging.info(" running normalization with only sample data ... Done!")
        return o_norm

    def normalization_sample_and_ob_data(self, o_norm, list_roi):
        logging.info(" running normalization with sample and ob data ...")

        # # sample
        # show_status_message(parent=self.parent,
        #                     message="Loading sample data ...",
        #                     status=StatusMessageStatus.working)
        # o_norm = NeuNormNormalization()
        # o_norm.load(data=data)
        # show_status_message(parent=self.parent,
        #                     message="Loading sample data ... Done!",
        #                     status=StatusMessageStatus.working)
        #
        # # ob
        # show_status_message(parent=self.parent,
        #                     message="Loading ob data ...",
        #                     status=StatusMessageStatus.working)
        # o_norm.load(data=ob, data_type=DataType.ob)
        # show_status_message(parent=self.parent,
        #                     message="Loading ob data ... Done!",
        #                     status=StatusMessageStatus.working,
        #                     duration_s=5)

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

        # self.o_norm = o_norm
        #
        # show_status_message(parent=self.parent,
        #                     message="Running normalization ... Done!",
        #                     status=StatusMessageStatus.working,
        #                     duration_s=5)
        #
        # show_status_message(parent=self.parent,
        #                     message="Exporting normalized files ...",
        #                     status=StatusMessageStatus.working)
        # o_norm.export(folder=output_folder)
        # show_status_message(parent=self.parent,
        #                     message="Exporting normalized files ... Done!",
        #                     status=StatusMessageStatus.working,
        #                     duration_s=5)

        logging.info(" running normalization with sample and ob data ... Done!")
        return o_norm
