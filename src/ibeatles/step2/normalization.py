#!/usr/bin/env python
"""
Normalization

The math runs through ibeatles.core.processing.normalization (the
NeuNorm 2.0 port shared with the headless CLI); this module keeps the
GUI plumbing: output-folder dialog, status messages, session bookkeeping
and the step3 re-import of the exported folder.

Two pre-existing behaviors are preserved on purpose so the port changes
one variable at a time (both are 2026-06-12 audit findings, fixed in the
coordinated science-fixes PR, not here):

- the open beam is never smoothed by the moving average (the OB branch
  in the 1.x-era code was dead);
- in the "normalization then moving average" order, the moving average
  runs but cannot affect the exported/normalized output (it only ever
  smoothed the raw sample buffer, after the normalized data had already
  been computed).
"""

import copy
import os
import shutil

import numpy as np
from loguru import logger
from qtpy.QtWidgets import QFileDialog

from ibeatles import DataType
from ibeatles.core.processing.normalization import (
    export_normalized_stack,
    normalize_stacks,
)
from ibeatles.session import ReductionDimension, SessionKeys, SessionSubKeys
from ibeatles.step2.get import Get
from ibeatles.step2.reduction_settings_handler import ReductionSettingsHandler
from ibeatles.step2.reduction_tools import moving_average
from ibeatles.step2.roi_handler import Step2RoiHandler
from ibeatles.step3.event_handler import EventHandler
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.utilities.status_message_config import (
    StatusMessageStatus,
    show_status_message,
)


class Normalization:
    def __init__(self, parent=None):
        self.parent = parent
        # specific failure reason surfaced in the status bar by
        # run_and_export when a step returns None
        self._failure_message = None

    def run_and_export(self):
        logger.info("Running and exporting normalization:")
        self._failure_message = None

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
            logger.info(" No output folder selected, normalization stopped!")
            return False

        # save output folder to session
        self.parent.session_dict[DataType.normalized][SessionSubKeys.current_folder] = output_folder

        logger.info(f" output folder selected: {output_folder}")
        full_output_folder = os.path.join(output_folder, sample_name + "_normalized")
        try:
            full_output_folder = FileHandler.make_or_append_date_time_to_folder(full_output_folder)
        except OSError:
            logger.info(f"ERROR: folder permission error into this folder {full_output_folder}")
            show_status_message(
                parent=self.parent,
                message="You don't have write permission into this folder!",
                status=StatusMessageStatus.error,
                duration_s=10,
            )
            return False

        logger.info(f" full output folder will be: {full_output_folder}")

        sample_stack, ob_stack = self.get_input_stacks()

        if self.parent.session_dict[SessionKeys.reduction][SessionSubKeys.process_order] == "option1":
            # running moving average before running normalization
            sample_stack = self.running_moving_average(sample_stack=sample_stack)
            normalized = self.running_normalization(sample_stack=sample_stack, ob_stack=ob_stack)
        else:
            # running normalization then moving average
            normalized = self.running_normalization(sample_stack=sample_stack, ob_stack=ob_stack)
            # preserved no-op: smoothing in this order never reaches the
            # normalized output (see module docstring) — run it so the GUI
            # behaves identically (status messages, failure failing the
            # run), but the smoothed result is discarded
            if self.running_moving_average(sample_stack=sample_stack) is None:
                normalized = None

        if normalized is None:
            logger.info("Normalization failed!")
            show_status_message(
                parent=self.parent,
                message=self._failure_message or "Normalization Failed (check logbook)!",
                status=StatusMessageStatus.error,
            )
            return False

        self.export_normalization(normalized=normalized, output_folder=full_output_folder)
        self.saving_normalization_parameters(normalized=normalized, output_folder=full_output_folder)
        self.moving_time_spectra_to_normalizaton_folder(output_folder=full_output_folder)

        # repopulate ui with normalized data
        o_step3 = EventHandler(parent=self.parent, data_type=DataType.normalized)
        o_step3.import_button_clicked_automatically(folder=full_output_folder)

        return True

    def get_input_stacks(self):
        """Pull the sample and OB stacks loaded in the GUI.

        Returns (sample_stack, ob_stack) where ob_stack is None when no
        open beam was loaded (the 1.x-era check was `_ob.any()`).
        """
        logger.info("Collecting sample and OB stacks for normalization")

        show_status_message(
            parent=self.parent,
            message="Loading data ...",
            status=StatusMessageStatus.working,
        )
        sample_stack = np.asarray(self.parent.data_metadata["sample"]["data"])
        show_status_message(
            parent=self.parent,
            message="Loading data ... Done!",
            status=StatusMessageStatus.working,
            duration_s=5,
        )

        _ob = self.parent.data_metadata["ob"]["data"]
        ob_stack = None
        if _ob is not None and np.asarray(_ob).any():
            show_status_message(
                parent=self.parent,
                message="Loading ob data ...",
                status=StatusMessageStatus.working,
            )
            ob_stack = np.asarray(_ob)
            show_status_message(
                parent=self.parent,
                message="Loading ob data ... Done!",
                status=StatusMessageStatus.working,
                duration_s=5,
            )

        return sample_stack, ob_stack

    def export_normalization(self, normalized=None, output_folder=None):
        show_status_message(
            parent=self.parent,
            message="Exporting normalized files ...",
            status=StatusMessageStatus.working,
        )
        export_normalized_stack(normalized, output_folder)
        show_status_message(
            parent=self.parent,
            message="Exporting normalized files ... Done!",
            status=StatusMessageStatus.working,
            duration_s=5,
        )

    def moving_time_spectra_to_normalizaton_folder(self, output_folder=None):
        logger.info("Copying time spectra file from input folder to output folder.")
        time_spectra = self.parent.data_metadata["sample"]["time_spectra"]
        filename = time_spectra["filename"]
        folder = time_spectra["folder"]
        full_time_spectra = os.path.join(folder, filename)
        logger.info(f"-> time_spectra: {time_spectra}")
        logger.info(f"-> full_time_spectra: {full_time_spectra}")
        shutil.copy(full_time_spectra, output_folder)

    def saving_normalization_parameters(self, normalized=None, output_folder=None):
        logger.info("Internally saving normalization parameters (data, folder, time_spectra)")
        self.parent.data_metadata[DataType.normalized]["data"] = np.asarray(normalized)
        self.parent.data_metadata[DataType.normalized]["folder"] = output_folder
        self.parent.data_metadata[DataType.normalized]["time_spectra"] = copy.deepcopy(
            self.parent.data_metadata[DataType.sample]["time_spectra"]
        )

    def running_moving_average(self, sample_stack=None):
        """Smooth the sample stack with the configured kernel.

        The open beam is intentionally NOT smoothed — preserved from the
        previous implementation (see module docstring).
        """
        if sample_stack is None:
            return None

        running_moving_average_settings = self.parent.session_dict[SessionKeys.reduction]
        if not running_moving_average_settings["activate"]:
            logger.info("Not running moving average! Option has been turned off")
            return sample_stack

        show_status_message(
            parent=self.parent,
            message="Running moving average ...",
            status=StatusMessageStatus.working,
        )
        logger.info("Running moving average:")
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
        if reduction_settings["dimension"] == ReductionDimension.threed:
            kernel.append(lda)

        o_get = Get(parent=self.parent)
        kernel_type = o_get.kernel_type()

        logger.info(f"-> kernel dimension: {reduction_settings['dimension']}")
        logger.info(f"-> kernel shape: {np.shape(kernel)}")
        logger.info(f"-> sample stack shape: {np.shape(sample_stack)}")
        logger.info(f"-> kernel: {kernel}")
        logger.info(f"-> kernel type: {kernel_type}")

        logger.info("-> Starting to run moving average with sample data")
        show_status_message(
            parent=self.parent,
            message="Moving average of sample data ...",
            status=StatusMessageStatus.working,
        )
        smoothed = moving_average(data=np.asarray(sample_stack), kernel=kernel, kernel_type=kernel_type)
        logger.info("-> Done running moving average with sample data!")
        if smoothed is None:
            logger.info("Moving average failed!")
            show_status_message(
                parent=self.parent,
                message="Running moving average ... Failed",
                status=StatusMessageStatus.error,
            )
            return None

        show_status_message(
            parent=self.parent,
            message="Moving average of sample data ... Done!",
            status=StatusMessageStatus.working,
            duration_s=5,
        )

        return smoothed

    def running_normalization(self, sample_stack=None, ob_stack=None):
        logger.info(" running normalization!")

        if sample_stack is None:
            return None

        # check if roi selected or not
        o_roi_handler = Step2RoiHandler(parent=self.parent)
        try:  # to avoid valueError when row not fully filled
            list_roi_to_use = o_roi_handler.get_list_of_background_roi_to_use()
        except ValueError:
            logger.info(" Error raised when retrieving the background ROI!")
            self._failure_message = "Normalization failed: check the background ROI table entries!"
            return None

        logger.info(f" Background list of ROI: {list_roi_to_use}")

        background_rois = [(int(_roi[0]), int(_roi[1]), int(_roi[2]), int(_roi[3])) for _roi in list_roi_to_use]

        show_status_message(
            parent=self.parent,
            message="Running normalization ...",
            status=StatusMessageStatus.working,
        )
        try:
            normalized = normalize_stacks(
                sample_stack,
                ob_stack=ob_stack,
                background_rois=background_rois,
            )
        except ValueError as error:
            # e.g. no OB and no background ROI — fail through the status
            # bar instead of letting the exception escape the Qt slot
            logger.info(f" Normalization error: {error}")
            self._failure_message = f"Normalization failed: {error}"
            return None

        show_status_message(
            parent=self.parent,
            message="Running normalization ... Done!",
            status=StatusMessageStatus.working,
            duration_s=5,
        )

        logger.info(" running normalization ... Done!")
        return normalized
