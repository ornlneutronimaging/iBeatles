from qtpy.QtWidgets import QFileDialog
import os
import shutil
import logging
import numpy as np
import copy

from NeuNorm.normalization import Normalization as NeuNormNormalization
from NeuNorm.roi import ROI

from src.ibeatles import DataType
from src.ibeatles.step2.roi_handler import Step2RoiHandler
from src.ibeatles.step3.event_handler import EventHandler
from src.ibeatles.utilities.file_handler import FileHandler
from src.ibeatles.utilities.status_message_config import (
    StatusMessageStatus,
    show_status_message,
)
from src.ibeatles.step2.reduction_settings_handler import ReductionSettingsHandler
from src.ibeatles.step2.reduction_tools import moving_average
from src.ibeatles.step2.get import Get
from src.ibeatles.session import SessionKeys, SessionSubKeys


class Normalization:
    coeff_array = 1  # ob / sample of ROI selected
    o_norm = None

    def __init__(self, parent=None):
        self.parent = parent

    def run_and_export(self):
        logging.info("Running and exporting normalization:")

        # ask for output folder location
        sample_folder = self.parent.data_metadata["sample"]["folder"]
        sample_name = os.path.basename(os.path.dirname(sample_folder))
        default_dir = os.path.dirname(os.path.dirname(sample_folder))
        output_folder = str(
            QFileDialog.getExistingDirectory(
                caption="Select Where the Normalized folder will be created...",
                directory=default_dir,
                options=QFileDialog.ShowDirsOnly,
            )
        )

        if not output_folder:
            logging.info(" No output folder selected, normalization stopped!")
            return False

        logging.info(f" output folder selected: {output_folder}")
        full_output_folder = os.path.join(output_folder, sample_name + "_normalized")
        try:
            full_output_folder = FileHandler.make_or_append_date_time_to_folder(
                full_output_folder
            )
        except OSError:
            logging.info(
                f"ERROR: folder permission error into this folder {full_output_folder}"
            )
            show_status_message(
                parent=self.parent,
                message="You don't have write permission into this folder!",
                status=StatusMessageStatus.error,
                duration_s=10,
            )
            return False

        logging.info(f" full output folder will be: {full_output_folder}")

        o_norm = self.create_o_norm()

        if (
            self.parent.session_dict[SessionKeys.reduction][
                SessionSubKeys.process_order
            ]
            == "option1"
        ):
            # running moving average before running normalization
            o_norm = self.running_moving_average(o_norm=copy.deepcopy(o_norm))
            o_norm = self.running_normalization(o_norm=copy.deepcopy(o_norm))
        else:
            # running normalization then moving average
            o_norm = self.running_normalization(o_norm=copy.deepcopy(o_norm))
            o_norm = self.running_moving_average(o_norm=copy.deepcopy(o_norm))

        if not o_norm:
            logging.info("Normalization failed!")
            show_status_message(
                parent=self.parent,
                message="Normalization Failed (check logbook)!",
                status=StatusMessageStatus.error,
            )
            return False

        self.export_normalization(o_norm=o_norm, output_folder=full_output_folder)
        self.saving_normalization_parameters(
            o_norm=o_norm, output_folder=full_output_folder
        )
        self.moving_time_spectra_to_normalizaton_folder(
            output_folder=full_output_folder
        )

        # repopulate ui with normalized data
        o_step3 = EventHandler(parent=self.parent, data_type=DataType.normalized)
        o_step3.import_button_clicked_automatically(folder=full_output_folder)

        return True

    def create_o_norm(self):
        logging.info("Creating o_norm object (to prepare data normalization!")

        _data = self.parent.data_metadata["sample"]["data"]
        _ob = self.parent.data_metadata["ob"]["data"]

        show_status_message(
            parent=self.parent,
            message="Loading data ...",
            status=StatusMessageStatus.working,
        )
        o_norm = NeuNormNormalization()
        o_norm.load(data=_data)
        show_status_message(
            parent=self.parent,
            message="Loading data ... Done!",
            status=StatusMessageStatus.working,
            duration_s=5,
        )

        if _ob.any():
            show_status_message(
                parent=self.parent,
                message="Loading ob data ...",
                status=StatusMessageStatus.working,
            )
            o_norm.load(data=_ob, data_type=DataType.ob)
            show_status_message(
                parent=self.parent,
                message="Loading ob data ... Done!",
                status=StatusMessageStatus.working,
                duration_s=5,
            )

        return o_norm

    def export_normalization(self, o_norm=None, output_folder=None):
        show_status_message(
            parent=self.parent,
            message="Exporting normalized files ...",
            status=StatusMessageStatus.working,
        )
        o_norm.export(folder=output_folder)
        show_status_message(
            parent=self.parent,
            message="Exporting normalized files ... Done!",
            status=StatusMessageStatus.working,
            duration_s=5,
        )

    def moving_time_spectra_to_normalizaton_folder(self, output_folder=None):
        logging.info("Copying time spectra file from input folder to output folder.")
        time_spectra = self.parent.data_metadata["sample"]["time_spectra"]
        filename = time_spectra["filename"]
        folder = time_spectra["folder"]
        full_time_spectra = os.path.join(folder, filename)
        logging.info(f"-> time_spectra: {time_spectra}")
        logging.info(f"-> full_time_spectra: {full_time_spectra}")
        shutil.copy(full_time_spectra, output_folder)

    def saving_normalization_parameters(self, o_norm=None, output_folder=None):
        logging.info(
            "Internally saving normalization parameters (data, folder, time_spectra)"
        )
        self.parent.data_metadata[DataType.normalized]["data"] = np.array(
            o_norm.get_normalized_data()
        )
        self.parent.data_metadata[DataType.normalized]["folder"] = output_folder
        self.parent.data_metadata[DataType.normalized]["time_spectra"] = copy.deepcopy(
            self.parent.data_metadata[DataType.sample]["time_spectra"]
        )

    def running_moving_average(self, o_norm=None):
        if o_norm is None:
            return None

        running_moving_average_settings = self.parent.session_dict[
            SessionKeys.reduction
        ]
        if not running_moving_average_settings["activate"]:
            logging.info("Not running moving average! Option has been turned off")
            return o_norm

        show_status_message(
            parent=self.parent,
            message="Running moving average ...",
            status=StatusMessageStatus.working,
        )
        logging.info("Running moving average:")
        reduction_settings = self.parent.session_dict[SessionKeys.reduction]

        if reduction_settings["size"]["flag"] == "default":
            x = ReductionSettingsHandler.default_kernel_size["x"]
            y = ReductionSettingsHandler.default_kernel_size["y"]
            lda = ReductionSettingsHandler.default_kernel_size["l"]

        else:
            x = reduction_settings["size"]["x"]
            y = reduction_settings["size"]["y"]
            lda = reduction_settings["size"]["l"]

        kernel = [y, x]
        if reduction_settings["dimension"] == "3d":
            kernel.append(lda)

        _data = np.array(o_norm.data[DataType.sample]["data"])  # lambda, x, y
        _data_transposed = _data.transpose(2, 1, 0)  # x, y, lambda

        o_get = Get(parent=self.parent)
        kernel_type = o_get.kernel_type()

        logging.info(f"-> kernel dimension: {reduction_settings['dimension']}")
        logging.info(f"-> kernel shape: {np.shape(kernel)}")
        logging.info(f"-> len(sample): {len(_data_transposed)}")
        logging.info(f"-> kernel: {kernel}")
        logging.info(f"-> kernel type: {kernel_type}")

        logging.info("-> Starting to run moving average with sample data")
        show_status_message(
            parent=self.parent,
            message="Moving average of sample data ...",
            status=StatusMessageStatus.working,
        )
        sample_data = moving_average(data=_data, kernel=kernel, kernel_type=kernel_type)
        logging.info("-> Done running moving average with sample data!")
        if sample_data is None:
            logging.info("Moving average failed!")
            show_status_message(
                parent=self.parent,
                message="Running moving average ... Failed",
                status=StatusMessageStatus.error,
            )
            return
        else:
            sample_data.transpose(2, 1, 0)  # lambda, x, y

        o_norm.data[DataType.sample]["data"] = sample_data
        show_status_message(
            parent=self.parent,
            message="Moving average of sample data ... Done!",
            status=StatusMessageStatus.working,
            duration_s=5,
        )

        _ob = np.array(o_norm.data[DataType.ob]["data"])
        if _ob is None:
            show_status_message(
                parent=self.parent,
                message="Moving average of ob data ...",
                status=StatusMessageStatus.ready,
            )
            logging.info("-> Starting to run moving average with ob data")
            ob_data = moving_average(data=_ob, kernel=kernel, kernel_type=kernel_type)
            logging.info("-> Done running moving average with ob data!")
            if ob_data:
                ob_data.transpose(2, 1, 0)  # lambda, x, y
            else:
                logging.info("Moving average failed!")
                show_status_message(
                    parent=self.parent,
                    message="Running moving average ... Failed",
                    status=StatusMessageStatus.error,
                )
                return

            o_norm.data[DataType.ob]["data"] = ob_data

            show_status_message(
                parent=self.parent,
                message="Moving average of ob data ... Done!",
                status=StatusMessageStatus.ready,
                duration_s=5,
            )

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

        if not o_norm.data["ob"]["data"]:
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
            o_roi = ROI(
                x0=int(_roi[0]),
                y0=int(_roi[1]),
                width=int(_roi[2]),
                height=int(_roi[3]),
            )
            list_roi_object.append(o_roi)

        show_status_message(
            parent=self.parent,
            message="Running normalization ...",
            status=StatusMessageStatus.working,
        )
        o_norm.normalization(roi=list_roi_object, use_only_sample=True)

        # self.o_norm = o_norm

        show_status_message(
            parent=self.parent,
            message="Running normalization ... Done!",
            status=StatusMessageStatus.working,
            duration_s=5,
        )

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
            o_roi = ROI(
                x0=int(_roi[0]),
                y0=int(_roi[1]),
                width=int(_roi[2]),
                height=int(_roi[3]),
            )
            list_roi_object.append(o_roi)

        show_status_message(
            parent=self.parent,
            message="Running normalization ...",
            status=StatusMessageStatus.working,
        )
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

    # def can_we_use_buffered_data(self, kernel_dimension=None, kernel_size=None, kernel_type=None):
    #     if self.parent.moving_average_config is None:
    #         return False
    #
    #     buffered_kernel_dimension = self.parent.moving_average_config.get('kernel_dimension', None)
    #     if buffered_kernel_dimension is None:
    #         return False
    #     if not (kernel_dimension == buffered_kernel_dimension):
    #         return False
    #
    #     buffered_kernel_size = self.parent.moving_average_config.get('kernel_size', None)
    #     if buffered_kernel_size is None:
    #         return False
    #     if not (buffered_kernel_size['x'] == kernel_size['x']):
    #         return False
    #     if not (buffered_kernel_size['y'] == kernel_size['y']):
    #         return False
    #     if kernel_dimension == '3d':
    #         if not (buffered_kernel_size['lambda'] == kernel_size['lambda']):
    #             return False
    #
    #     buffered_kernel_type = self.parent.moving_average_config.get('kernel_type', None)
    #     if buffered_kernel_type is None:
    #         return False
    #     if not (buffered_kernel_type == kernel_type):
    #         return False
    #
    #     return True
