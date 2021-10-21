import logging

from .. import DataType
from .save_tab import SaveTab
from ..utilities.gui_handler import GuiHandler
from ..utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities


class SaveLoadDataTab(SaveTab):

    def sample(self):
        """record all the parameters of the Load Data tab / Sample accordion tab"""

        data_type = DataType.sample

        list_files = self.parent.list_files[data_type]
        current_folder = self.parent.data_metadata[data_type]['folder']
        time_spectra_filename = self.parent.data_metadata[data_type]['time_spectra']['filename']
        list_files_selected = [int(index) for index in self.parent.list_file_selected[data_type]]
        list_roi = self.parent.list_roi[data_type]
        o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                    image_view=self.parent.ui.image_view,
                                    data_type=data_type)
        state = o_pyqt.get_state()
        o_pyqt.save_histogram_level()
        histogram = self.parent.image_view_settings[data_type]['histogram']

        logging.info("Recording parameters of Load Data / Sample")
        logging.info(f" len(list files) = {len(list_files)}")
        logging.info(f" current folder: {current_folder}")
        logging.info(f" time spectra filename: {time_spectra_filename}")
        logging.info(f" list files selected: {list_files_selected}")
        logging.info(f" len(list rois): {len(list_roi)}")
        logging.info(f" state: {state}")
        logging.info(f" histogram: {histogram}")

        self.session_dict[data_type]['list files'] = list_files
        self.session_dict[data_type]['current folder'] = current_folder
        self.session_dict[data_type]['time spectra filename'] = time_spectra_filename
        self.session_dict[data_type]['list files selected'] = list_files_selected
        self.session_dict[data_type]['list rois'] = list_roi
        self.session_dict[data_type]['image view state'] = state
        self.session_dict[data_type]['image view histogram'] = histogram

    def ob(self):
        """record all the parameters of the Load Data tab / ob accordion tab"""

        data_type = DataType.ob

        list_files = self.parent.list_files[data_type]
        current_folder = self.parent.data_metadata[data_type]['folder']
        list_files_selected = [int(index) for index in self.parent.list_file_selected[data_type]]
        list_roi = self.parent.list_roi[data_type]
        o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                    image_view=self.parent.ui.ob_image_view,
                                    data_type=data_type)
        state = o_pyqt.get_state()
        o_pyqt.save_histogram_level()
        histogram = self.parent.image_view_settings[data_type]['histogram']

        logging.info("Recording parameters of Load Data / OB")
        logging.info(f" len(list files) = {len(list_files)}")
        logging.info(f" current folder: {current_folder}")
        logging.info(f" list files selected: {list_files_selected}")
        logging.info(f" len(list rois): {len(list_roi)}")
        logging.info(f" state: {state}")
        logging.info(f" histogram: {histogram}")

        self.session_dict[data_type]['list files'] = list_files
        self.session_dict[data_type]['current folder'] = current_folder
        self.session_dict[data_type]['list files selected'] = list_files_selected
        self.session_dict[data_type]['list rois'] = list_roi
        self.session_dict[data_type]['image view state'] = state
        self.session_dict[data_type]['image view histogram'] = histogram

    def instrument(self):
        """record the settings of the instrument such as offset, distance source/detector ..."""

        list_ui = {'distance': self.parent.ui.distance_source_detector,
                   'beam': self.parent.ui.beam_rate,
                   'detector': self.parent.ui.detector_offset}

        o_gui = GuiHandler(parent=self.parent)
        distance_value = o_gui.get_text(ui=list_ui['distance'])
        detector_value = o_gui.get_text(ui=list_ui['detector'])
        beam_index = o_gui.get_index_selected(ui=list_ui['beam'])

        logging.info("Recording instrument")
        logging.info(f" distance source detector: {distance_value}")
        logging.info(f" detector value: {detector_value}")
        logging.info(f" beam index: {beam_index}")

        self.session_dict["instrument"]["distance source detector"] = distance_value
        self.session_dict["instrument"]["detector value"] = detector_value
        self.session_dict["instrument"]["beam index"] = beam_index

