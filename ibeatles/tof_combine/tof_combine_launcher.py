from qtpy.QtWidgets import QMainWindow
from qtpy.QtWidgets import QApplication
from qtpy import QtCore
import logging
import warnings

warnings.filterwarnings("ignore")

# from .utilities.get import Get
# from .utilities.config_handler import ConfigHandler
# from .utilities import TimeSpectraKeys, BinAutoMode
from ibeatles.tof_combine.utilities.time_spectra import TimeSpectraLauncher
# from .event_hander import EventHandler
# from .session import session
# from .session.session_handler import SessionHandler
# from .session import SessionKeys
from ibeatles.tof_combine.initialization import Initialization
# from .utilities.check import Check
from ibeatles.tof_combine.combine.event_handler import EventHandler as CombineEventHandler
# from maverick.export.export_images import ExportImages
# from maverick.export.export_bin_table import ExportBinTable
from ibeatles.tof_combine.utilities import TimeSpectraKeys

from ibeatles import load_ui
from ibeatles.tof_combine import SessionKeys


class TofCombineLauncher:

    def __init__(self, parent=None):

        if parent.binning_ui is None:
            tof_combine_window = TofCombine(parent=parent)
            tof_combine_window.show()
            parent.tof_combining_binning_ui = tof_combine_window

        else:
            parent.binning_ui.setFocus()
            parent.binning_ui.activateWindow()


class TofCombine(QMainWindow):

    # list of folders listed in the combine table
    list_folders = None

    # full path to the top folder selected and used to fill the table
    top_folder = None

    # folder we will use or not
    list_of_folders_status = None

    combine_roi = {'x0': 0,
                   'y0': 0,
                   'width': 200,
                   'height': 200}

    # dictionary that will keep record of the entire UI and used to load and save the session
    session = {SessionKeys.list_folders: None,
               SessionKeys.list_folders_status: None,
               SessionKeys.top_folder: None,
               SessionKeys.combine_roi: combine_roi,
               }

    # save info from all the folders
    # {0: {SessionKeys.folder: None,
    #      SessionKeys.data: None,
    #      SessionKeys.list_files: None,
    #      SessionKeys.nbr_files: None,
    #      SessionKeys.use: False,
    #      },
    #  1: ....,
    # }
    dict_data_folders = {}

    combine_image_view = None
    combine_roi_item_id = None

    # time spectra dict
    time_spectra = {TimeSpectraKeys.file_name: None,
                    TimeSpectraKeys.tof_array: None,
                    TimeSpectraKeys.lambda_array: None,
                    TimeSpectraKeys.file_index_array: None}

    # log_id = None  # ui id of the log QDialog
    # version = None   # current version of application
    #
    # # raw_data_folders = {'full_path_to_folder1': {'data': [image1, image2, image3...],
    # #                                              'list_files': [file1, file2, file3,...],
    # #                                              'nbr_files': 0,
    # #                                              },
    # #                     'full_path_to_folder2': {'data': [image1, image2, image3...],
    # #                                              'list_files': [file1, file2, file3,...],
    # #                                              'nbr_files': 0,
    # #                                              },
    # #                     ....
    # #                    }
    # raw_data_folders = None  # dictionary of data for each of the folders
    #
    # # combine_data = [image1, image2, image3...]
    # combine_data = None
    #
    # # time spectra file and arrays
    # time_spectra = {TimeSpectraKeys.file_name: None,
    #                 TimeSpectraKeys.tof_array: None,
    #                 TimeSpectraKeys.lambda_array: None,
    #                 TimeSpectraKeys.file_index_array: None}
    #
    # linear_bins = {TimeSpectraKeys.tof_array: None,
    #                TimeSpectraKeys.file_index_array: None,
    #                TimeSpectraKeys.lambda_array: None}
    #
    # log_bins = {TimeSpectraKeys.tof_array: None,
    #             TimeSpectraKeys.file_index_array: None,
    #             TimeSpectraKeys.lambda_array: None}
    #
    # # each will be a dictionaries of ranges
    # # ex: TimeSpectraKeys.tof_array = {0: [1],
    # #                                  1: [2,6],
    # #                                  3: [7,8,9,10], ...}
    # manual_bins = {TimeSpectraKeys.tof_array: None,
    #                TimeSpectraKeys.file_index_array: None,
    #                TimeSpectraKeys.lambda_array: None}
    #
    # # dictionary that will record the range for each bin
    # # {0: [0, 3], 1: [1, 10], ...}
    # manual_snapping_indexes_bins = None
    #
    # # list of rows selected by each of the linear and log bins
    # linear_bins_selected = None
    # log_bins_selected = None
    #
    # # use to preview the full axis
    # # ex: [1,2,3,4,5,6,7] or [0.1, 0.2, 0.4, 0.8, 1.6....]
    # full_bin_axis_requested = None
    #
    # # profile signal (displayed on the top right of combine and bin tab)
    # # 1D array
    # profile_signal = None
    #
    # # pyqtgraph view
    # combine_image_view = None  # combine image view id - top right plot
    # combine_profile_view = None  # combine profile plot view id - bottom right plot
    # bin_profile_view = None  # bin profile

    # combine_file_index_radio_button = None  # in combine view
    # tof_radio_button = None  # in combine view
    # lambda_radio_button = None  # in combine view
    # live_combine_image = None  # live combine image used by ROI
    #
    # # matplotlib plot
    # statistics_plot = None  # matplotlib plot
    #
    # # dictionary of all the bins pg item
    # # {0: pg.regionitem1,
    # #  2: pg.regionitem2,
    # #  ...
    # # }
    # dict_of_bins_item = None
    #
    # # list of manual bins.
    # # using a list because any of the bin can be removed by the user
    # list_of_manual_bins_item = []
    #
    # current_auto_bin_rows_highlighted = []
    #
    # # stats currently displayed in the bin stats table
    # # {StatisticsName.mean: {Statistics.full: [],
    # #                        Statistics.roi: [],
    # #                        },
    # # StatisticsName.median: ....
    # #  }
    # current_stats = None

    def __init__(self, parent=None):
        """
        Initialization
        Parameters
        ----------
        """
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_tof_combine.ui', baseinstance=self)
        self.parent = parent
        self.initialization()
        self.setup()
        self.setWindowTitle(f"TOF combine tool")

    def initialization(self):
        o_init = Initialization(parent=self)
        o_init.all()

    def setup(self):
        logging.info(f"Starting the TOF combine tool!")
        distance_source_detector = self.parent.ui.distance_source_detector.text()
        self.ui.distance_source_detector_label.setText(distance_source_detector)

        detector_offset = self.parent.ui.detector_offset.text()
        self.ui.detector_offset_label.setText(detector_offset)

    # combine events
    def check_combine_widgets(self):
        o_event = CombineEventHandler(parent=self)
        o_event.check_widgets()

    def select_top_folder_button_clicked(self):
        o_event = CombineEventHandler(parent=self,
                                      grand_parent=self.parent)
        o_event.select_top_folder()

    def refresh_table_clicked(self):
        o_event = CombineEventHandler(parent=self)
        o_event.refresh_table_clicked()

    def radio_buttons_of_folder_changed(self):
        self.ui.setEnabled(False)
        o_event = CombineEventHandler(parent=self)
        o_event.update_list_of_folders_to_use()
        o_event.combine_folders()
        o_event.display_profile()
        o_event.check_widgets()
        self.ui.setEnabled(True)
        self.ui.combine_widget.setEnabled(True)

    def time_spectra_preview_clicked(self):
        TimeSpectraLauncher(parent=self)

    def combine_algorithm_changed(self):
        o_event = CombineEventHandler(parent=self)
        o_event.combine_algorithm_changed()
        o_event.display_profile()

    def combine_instrument_settings_changed(self):
        if self.combine_data is None:
            return
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        o_event = CombineEventHandler(parent=self)
        o_event.update_list_of_folders_to_use(force_recalculation_of_time_spectra=True)
        o_event.combine_folders()
        o_event.display_profile()
        QApplication.restoreOverrideCursor()

    def combine_xaxis_changed(self):
        o_event = CombineEventHandler(parent=self)
        o_event.display_profile()

    def combine_roi_changed(self):
        o_event = CombineEventHandler(parent=self)
        o_event.combine_roi_changed()
        o_event.display_profile()

    def mouse_moved_in_combine_image_preview(self):
        """Mouse moved in the combine pyqtgraph image preview (top right)"""
        pass

       # export images
    def export_combined_and_binned_images_clicked(self):
        pass
        # o_export = ExportImages(parent=self)
        # o_export.run()

    def closeEvent(self, event):
        logging.info(" #### Leaving combine TOF####")
        self.parent.tof_combine_ui = None
        self.close()
