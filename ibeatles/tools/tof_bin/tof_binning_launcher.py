from qtpy.QtWidgets import QApplication, QMainWindow
import sys
import os
import logging
import warnings

warnings.filterwarnings("ignore")

from ibeatles.tools.utilities import TimeSpectraKeys
from ibeatles.tools.utilities.time_spectra import TimeSpectraLauncher
from ibeatles.tools.tof_bin.initialization import Initialization
from ibeatles.tools.tof_bin.event_handler import EventHandler as TofBinEventHandler
from ibeatles.tools.tof_bin.auto_event_handler import AutoEventHandler

# from .utilities.get import Get
# from .utilities.config_handler import ConfigHandler
# from .utilities import TimeSpectraKeys, BinAutoMode
# from .utilities.time_spectra import TimeSpectraLauncher
# from .event_hander import EventHandler
# from .session import session
# from .session.session_handler import SessionHandler
# from .session import SessionKeys
# from .initialization import Initialization
# from .utilities.check import Check
# from .combine.event_handler import EventHandler as CombineEventHandler
# from .bin.event_hander import EventHandler as BinEventHandler
# from .bin.manual_event_handler import ManualEventHandler as BinManualEventHandler
# from .bin.auto_event_handler import AutoEventHandler as BinAutoEventHandler
# from .bin.preview_full_bin_axis import PreviewFullBinAxis
# from .bin.statistics import Statistics
# from .bin.settings import Settings as BinSettings
# from .bin.manual_right_click import ManualRightClick
# from maverick.export.export_images import ExportImages
# from maverick.export.export_bin_table import ExportBinTable
# from .log.log_launcher import LogLauncher

from ibeatles import load_ui


class TofBinningLauncher:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.binning_ui is None:
            tof_combining_binning_window = TofBinning(parent=parent)
            tof_combining_binning_window.show()
            self.parent.tof_combining_binning_ui = tof_combining_binning_window
            # o_binning = BinningHandler(parent=self.parent)
            # o_binning.display_image()
        else:
            self.parent.binning_ui.setFocus()
            self.parent.binning_ui.activateWindow()


class TofBinning(QMainWindow):

    list_tif_files = None
    images_array = None
    integrated_image = None
    roi_item = None

    integrated_view = None  # pg integrated image (for ROI selection)
    bin_profile_view = None  # pg profile

    image_size = {'width': None,
                  'height': None}

    # time spectra dict
    time_spectra = {TimeSpectraKeys.file_name: None,
                    TimeSpectraKeys.tof_array: None,
                    TimeSpectraKeys.lambda_array: None,
                    TimeSpectraKeys.file_index_array: None}

    bin_roi = {'x0': 0,
               'y0': 0,
               'width': 100,
               'height': 100}

    profile_signal = None

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
        super(TofBinning, self).__init__(parent)
        self.ui = load_ui('ui_tof_binning.ui', baseinstance=self)
        self.top_parent = parent

        o_init = Initialization(parent=self, top_parent=parent)
        o_init.all()
        o_init.setup()

        o_event = TofBinEventHandler(parent=self, top_parent=parent)
        o_event.check_widgets()

        self.setWindowTitle(f"TOF bin")

    # event
    def select_folder_clicked(self):
        o_event = TofBinEventHandler(parent=self,
                                     top_parent=self.top_parent)
        o_event.select_input_folder()
        o_event.load_data()
        o_event.load_time_spectra_file()
        o_event.display_integrated_image()
        o_event.display_profile()
        o_event.check_widgets()

    def bin_roi_changed(self):
        o_event = TofBinEventHandler(parent=self)
        o_event.display_profile()

    # def setup(self):
    #     """
    #     This is taking care of
    #         - initializing the session dict
    #         - setting up the logging
    #         - retrieving the config file
    #         - loading or not the previous session
    #     """
    #     o_config = ConfigHandler(parent=self)
    #     o_config.load()
    #
    #     current_folder = None
    #     if self.config['debugging']:
    #         list_homepath = self.config['homepath']
    #         for _path in list_homepath:
    #             if os.path.exists(_path):
    #                 current_folder = _path
    #         if current_folder is None:
    #             current_folder = os.path.expanduser('~')
    #     else:
    #         current_folder = os.path.expanduser('~')
    #     self.session[SessionKeys.top_folder] = current_folder
    #
    #     o_get = Get(parent=self)
    #     log_file_name = o_get.log_file_name()
    #     version = Get.version()
    #     self.version = version
    #     self.log_file_name = log_file_name
    #     logging.basicConfig(filename=log_file_name,
    #                         filemode='a',
    #                         format='[%(levelname)s] - %(asctime)s - %(message)s',
    #                         level=logging.INFO)
    #     logger = logging.getLogger("maverick")
    #     logger.info("*** Starting a new session ***")
    #     logger.info(f" Version: {version}")
    #
    #     o_event = EventHandler(parent=self)
    #     o_event.automatically_load_previous_session()

    def bin_xaxis_changed(self):
        o_event = TofBinEventHandler(parent=self)
        o_event.display_profile()

    def help_log_clicked(self):
        LogLauncher(parent=self)

    # - auto mode
    def bin_auto_log_linear_radioButton_changed(self):
        o_event = AutoEventHandler(parent=self)
        o_event.bin_auto_radioButton_clicked()
        # self.update_statistics()

    def time_spectra_preview_clicked(self):
        TimeSpectraLauncher(parent=self)




    def bin_auto_manual_tab_changed(self, new_tab_index):
        o_event = AutoEventHandler(parent=self)
        o_event.bin_auto_manual_tab_changed(new_tab_index)
        self.update_statistics()

    def bin_auto_log_file_index_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.bin_auto_log_changed(source_radio_button=TimeSpectraKeys.file_index_array)
        self.update_statistics()

    def bin_auto_log_tof_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.bin_auto_log_changed(source_radio_button=TimeSpectraKeys.tof_array)
        self.update_statistics()

    def bin_auto_log_lambda_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.bin_auto_log_changed(source_radio_button=TimeSpectraKeys.lambda_array)
        self.update_statistics()

    def bin_auto_linear_file_index_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.bin_auto_linear_changed(source_radio_button=TimeSpectraKeys.file_index_array)
        self.update_statistics()

    def bin_auto_linear_tof_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.bin_auto_linear_changed(source_radio_button=TimeSpectraKeys.tof_array)
        self.update_statistics()

    def bin_auto_linear_lambda_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.bin_auto_linear_changed(source_radio_button=TimeSpectraKeys.lambda_array)
        self.update_statistics()

    def auto_log_radioButton_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.log)
        o_event.auto_log_radioButton_changed()
        self.update_statistics()

    def auto_linear_radioButton_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.auto_linear_radioButton_changed()
        self.update_statistics()

    def auto_table_use_checkbox_changed(self, state, row):
        o_event = BinAutoEventHandler(parent=self)
        state = True if state == 2 else False
        o_event.use_auto_bin_state_changed(row=row, state=state)
        self.bin_auto_table_selection_changed()
        self.update_statistics()

    def bin_auto_hide_empty_bins(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.update_auto_table()

    def bin_auto_visualize_axis_generated_button_clicked(self):
        o_preview = PreviewFullBinAxis(parent=self)
        o_preview.show()

    def bin_auto_table_right_clicked(self, position):
        o_event = BinAutoEventHandler(parent=self)
        o_event.auto_table_right_click(position=position)

    def bin_auto_table_selection_changed(self):
        o_event = BinAutoEventHandler(parent=self)
        o_event.auto_table_selection_changed()

    def mouse_moved_in_combine_image_preview(self):
        """Mouse moved in the combine pyqtgraph image preview (top right)"""
        pass

    # - manual mode
    def bin_manual_add_bin_clicked(self):
        o_event = BinManualEventHandler(parent=self)
        o_event.add_bin()
        self.update_statistics()

    def bin_manual_populate_table_with_auto_mode_bins_clicked(self):
        o_event = BinManualEventHandler(parent=self)
        o_event.clear_all_items()
        o_event.populate_table_with_auto_mode()
        self.update_statistics()

    def bin_manual_region_changed(self, item_id):
        o_event = BinManualEventHandler(parent=self)
        o_event.bin_manually_moved(item_id=item_id)
        self.update_statistics()

    def bin_manual_region_changing(self, item_id):
        o_event = BinManualEventHandler(parent=self)
        o_event.bin_manually_moving(item_id=item_id)

    def bin_manual_table_right_click(self, position):
        o_event = ManualRightClick(parent=self)
        o_event.manual_table_right_click()

    # - statistics
    def update_statistics(self):
        o_stat = Statistics(parent=self)
        o_stat.update()
        o_stat.plot_statistics()

    def bin_statistics_comboBox_changed(self):
        o_stat = Statistics(parent=self)
        o_stat.plot_statistics()

    def bin_settings_clicked(self):
        o_bin = BinSettings(parent=self)
        o_bin.show()

    # export images
    def export_combined_and_binned_images_clicked(self):
        o_export = ExportImages(parent=self)
        o_export.run()

    def bin_export_table_pushButton_clicked(self):
        o_export = ExportBinTable(parent=self)
        o_export.run()

    def closeEvent(self, event):
        # o_session = SessionHandler(parent=self)
        # o_session.save_from_ui()
        # o_session.automatic_save()
        #
        # o_event = Check(parent=self)
        # o_event.log_file_size()
        #
        logging.info(" #### Leaving combine/binning ####")
        self.close()
