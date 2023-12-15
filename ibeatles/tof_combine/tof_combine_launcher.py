from qtpy.QtWidgets import QMainWindow
import os
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
# from .initialization import Initialization
# from .utilities.check import Check
from ibeatles.tof_combine.combine.event_handler import EventHandler as CombineEventHandler
# from maverick.export.export_images import ExportImages
# from maverick.export.export_bin_table import ExportBinTable

from ibeatles import load_ui


class TofCombineLauncher:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.binning_ui is None:
            tof_combine_window = TofCombine(parent=parent)
            tof_combine_window.show()
            self.parent.tof_combining_binning_ui = tof_combine_window
            # o_binning = BinningHandler(parent=self.parent)
            # o_binning.display_image()
        else:
            self.parent.binning_ui.setFocus()
            self.parent.binning_ui.activateWindow()


class TofCombine(QMainWindow):

    # session = session  # dictionary that will keep record of the entire UI and used to load and save the session
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
    # combine_roi_item_id = None  # pyqtgraph item id of the roi (combine tab)
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
        # self.initialization()
        # self.setup()
        # self.setWindowTitle(f"maverick - v{self.version}")

    def initialization(self):
        o_init = Initialization(parent=self)
        o_init.all()

    def setup(self):
        """
        This is taking care of
            - initializing the session dict
            - setting up the logging
            - retrieving the config file
            - loading or not the previous session
        """
        o_config = ConfigHandler(parent=self)
        o_config.load()

        current_folder = None
        if self.config['debugging']:
            list_homepath = self.config['homepath']
            for _path in list_homepath:
                if os.path.exists(_path):
                    current_folder = _path
            if current_folder is None:
                current_folder = os.path.expanduser('~')
        else:
            current_folder = os.path.expanduser('~')
        self.session[SessionKeys.top_folder] = current_folder

        o_get = Get(parent=self)
        log_file_name = o_get.log_file_name()
        version = Get.version()
        self.version = version
        self.log_file_name = log_file_name
        logging.basicConfig(filename=log_file_name,
                            filemode='a',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logger = logging.getLogger("maverick")
        logger.info("*** Starting a new session ***")
        logger.info(f" Version: {version}")

        o_event = EventHandler(parent=self)
        o_event.automatically_load_previous_session()

    # combine events
    def check_combine_widgets(self):
        o_event = CombineEventHandler(parent=self)
        o_event.check_widgets()

    def select_top_folder_button_clicked(self):
        o_event = CombineEventHandler(parent=self)
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

    def time_spectra_preview_clicked(self):
        TimeSpectraLauncher(parent=self)

    def combine_algorithm_changed(self):
        o_get = Get(parent=self)
        list_working_folders = o_get.list_of_folders_to_use()
        if list_working_folders == []:
            return

        o_event = CombineEventHandler(parent=self)
        o_event.combine_algorithm_changed()
        o_event.display_profile()

    def combine_instrument_settings_changed(self):
        if self.combine_data is None:
            return
        o_event = CombineEventHandler(parent=self)
        o_event.update_list_of_folders_to_use(force_recalculation_of_time_spectra=True)
        o_event.combine_folders()
        o_event.display_profile()

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
        logging.info(" #### Leaving combine ####")
        self.parent.tof_combining_binning_ui = None
        self.close()
