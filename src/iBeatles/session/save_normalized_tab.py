import logging

from .save_tab import SaveTab
from .. import DataType
from ..utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities


class SaveNormalizedTab(SaveTab):

    def normalized(self):
        """ record the ROI selected"""

        data_type = DataType.normalized

        list_files = self.parent.list_files[data_type]
        current_folder = self.parent.data_metadata[data_type]['folder']
        time_spectra_filename = self.parent.data_metadata[data_type]['time_spectra']['filename']
        list_files_selected = [int(index) for index in self.parent.list_file_selected[data_type]]
        list_roi = self.parent.list_roi[data_type]

        o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                    image_view=self.parent.ui.normalized_image_view,
                                    data_type=data_type)
        state = o_pyqt.get_state()
        o_pyqt.save_histogram_level()
        histogram = self.parent.image_view_settings[data_type]['histogram']

        logging.info("Recording parameters of normalized tab")
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
