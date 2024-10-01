from qtpy.QtWidgets import QMainWindow
import logging
import warnings
from src.ibeatles import load_ui
from src.ibeatles.tools.utilities import TimeSpectraKeys
from src.ibeatles.tools.utilities.time_spectra import TimeSpectraLauncher

from src.ibeatles.tools.tof_bin import session
from src.ibeatles.tools.tof_bin import BinAutoMode, BinMode
from src.ibeatles.tools.tof_bin.event_handler import EventHandler
from src.ibeatles.tools.tof_bin.initialization import Initialization
from src.ibeatles.tools.tof_bin.event_handler import EventHandler as TofBinEventHandler
from src.ibeatles.tools.tof_bin.auto_event_handler import AutoEventHandler
from src.ibeatles.tools.tof_bin.manual_event_handler import ManualEventHandler
from src.ibeatles.tools.tof_bin.manual_right_click import ManualRightClick
from src.ibeatles.tools.tof_bin.statistics import Statistics
from src.ibeatles.tools.tof_bin.preview_full_bin_axis import PreviewFullBinAxis
from src.ibeatles.tools.tof_bin.tof_bin_export_launcher import TofBinExportLauncher

warnings.filterwarnings("ignore")


class TofBinningLauncher:
    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.binning_ui is None:
            tof_combining_binning_window = TofBinning(parent=parent)
            tof_combining_binning_window.show()
            self.parent.tof_combining_binning_ui = tof_combining_binning_window

        else:
            self.parent.binning_ui.setFocus()
            self.parent.binning_ui.activateWindow()


class TofBinning(QMainWindow):
    session = session

    list_tif_files = None
    images_array = None
    integrated_image = None
    roi_item = None

    integrated_view = None  # pg integrated image (for ROI selection)
    bin_profile_view = None  # pg profile

    image_size = {"width": None, "height": None}

    # time spectra dict
    time_spectra = {
        TimeSpectraKeys.file_name: None,
        TimeSpectraKeys.tof_array: None,
        TimeSpectraKeys.lambda_array: None,
        TimeSpectraKeys.file_index_array: None,
    }

    bin_roi = {"x0": 0, "y0": 0, "width": 100, "height": 100}

    profile_signal = None

    # dictionary of all the bins pg item
    # {0: pg.regionitem1,
    #  2: pg.regionitem2,
    #  ...
    # }
    dict_of_bins_item = None

    linear_bins_selected = None
    log_bins_selected = None

    # each will be a dictionaries of ranges
    # ex: TimeSpectraKeys.tof_array = {0: [1],
    #                                  1: [2,6],
    #                                  3: [7,8,9,10], ...}
    manual_bins = {
        TimeSpectraKeys.tof_array: None,
        TimeSpectraKeys.file_index_array: None,
        TimeSpectraKeys.lambda_array: None,
    }

    # list of manual bins.
    # using a list because any of the bin can be removed by the user
    list_of_manual_bins_item = []

    current_auto_bin_rows_highlighted = []

    # stats currently displayed in the bin stats table
    # {StatisticsName.mean: {Statistics.full: [],
    #                        Statistics.roi: [],
    #                        },
    # StatisticsName.median: ....
    #  }
    current_stats = {BinMode.auto: None, BinMode.manual: None}

    def __init__(self, parent=None):
        """
        Initialization
        Parameters
        ----------
        """
        super(TofBinning, self).__init__(parent)
        self.ui = load_ui("ui_tof_binning.ui", baseinstance=self)
        self.top_parent = parent

        o_init = Initialization(parent=self, top_parent=parent)
        o_init.all()
        o_init.setup()

        o_event = TofBinEventHandler(parent=self, top_parent=parent)
        o_event.check_widgets()

        self.setWindowTitle("TOF bin")

    # event
    def select_folder_clicked(self):
        o_event = TofBinEventHandler(parent=self, top_parent=self.top_parent)
        o_event.select_input_folder()
        if self.list_tif_files:
            o_event.load_data()
            o_event.load_time_spectra_file()
            o_event.display_integrated_image()
            o_event.display_profile()
            self.bin_auto_manual_tab_changed()
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
        o_event.bin_xaxis_changed()
        # self.bin_auto_manual_tab_changed()
        o_event.check_widgets()

    # - auto mode
    def bin_auto_log_linear_radioButton_changed(self):
        o_event = AutoEventHandler(parent=self)
        o_event.bin_auto_radioButton_clicked()
        self.update_statistics()

    def time_spectra_preview_clicked(self):
        TimeSpectraLauncher(parent=self)

    def combine_mean_median_changed(self):
        self.update_statistics()

    def bin_auto_manual_tab_changed(self, new_tab_index=-1):
        if self.images_array:
            o_event = TofBinEventHandler(parent=self)
            o_event.bin_auto_manual_tab_changed(new_tab_index)
            self.update_statistics()
            o_event_global = EventHandler(parent=self)
            o_event_global.check_widgets()

    def bin_auto_log_file_index_changed(self):
        if self.images_array:
            o_event = AutoEventHandler(parent=self)
            o_event.bin_auto_log_changed(
                source_radio_button=TimeSpectraKeys.file_index_array
            )
            self.update_statistics()

    def bin_auto_log_tof_changed(self):
        if self.images_array:
            o_event = AutoEventHandler(parent=self)
            o_event.bin_auto_log_changed(source_radio_button=TimeSpectraKeys.tof_array)
            self.update_statistics()

    def bin_auto_log_lambda_changed(self):
        if self.images_array:
            o_event = AutoEventHandler(parent=self)
            o_event.bin_auto_log_changed(
                source_radio_button=TimeSpectraKeys.lambda_array
            )
            self.update_statistics()

    def bin_auto_linear_file_index_changed(self):
        if self.images_array:
            o_event = AutoEventHandler(parent=self)
            o_event.clear_selection(auto_mode=BinAutoMode.linear)
            o_event.bin_auto_linear_changed(
                source_radio_button=TimeSpectraKeys.file_index_array
            )
            self.update_statistics()

    def bin_auto_linear_tof_changed(self):
        o_event = AutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.bin_auto_linear_changed(source_radio_button=TimeSpectraKeys.tof_array)
        self.update_statistics()

    def bin_auto_linear_lambda_changed(self):
        o_event = AutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.bin_auto_linear_changed(
            source_radio_button=TimeSpectraKeys.lambda_array
        )
        self.update_statistics()

    def auto_log_radioButton_changed(self):
        o_event = AutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.log)
        o_event.auto_log_radioButton_changed()
        self.update_statistics()

    def auto_linear_radioButton_changed(self):
        o_event = AutoEventHandler(parent=self)
        o_event.clear_selection(auto_mode=BinAutoMode.linear)
        o_event.auto_linear_radioButton_changed()
        self.update_statistics()

    def auto_table_use_checkbox_changed(self, state, row):
        o_event = AutoEventHandler(parent=self)
        state = True if state == 2 else False
        o_event.use_auto_bin_state_changed(row=row, state=state)
        self.bin_auto_table_selection_changed()
        self.update_statistics()
        o_event_global = EventHandler(parent=self)
        o_event_global.check_widgets()

    def bin_auto_hide_empty_bins(self):
        o_event = AutoEventHandler(parent=self)
        o_event.update_auto_table()

    def bin_auto_visualize_axis_generated_button_clicked(self):
        o_preview = PreviewFullBinAxis(parent=self)
        o_preview.show()

    def bin_auto_table_right_clicked(self, position):
        o_event = AutoEventHandler(parent=self)
        o_event.auto_table_right_click(position=position)

    def bin_auto_table_selection_changed(self):
        o_event = AutoEventHandler(parent=self)
        o_event.auto_table_selection_changed()

    def mouse_moved_in_combine_image_preview(self):
        """Mouse moved in the combine pyqtgraph image preview (top right)"""
        pass

    # - manual mode
    def bin_manual_add_bin_clicked(self):
        o_event = ManualEventHandler(parent=self)
        o_event.add_bin()
        self.update_statistics()
        o_event_global = EventHandler(parent=self)
        o_event_global.check_widgets()

    def bin_manual_populate_table_with_auto_mode_bins_clicked(self):
        o_event = ManualEventHandler(parent=self)
        o_event.clear_all_items()
        o_event.populate_table_with_auto_mode()
        self.update_statistics()
        o_event_global = EventHandler(parent=self)
        o_event_global.check_widgets()

    def bin_manual_region_changed(self, item_id):
        o_event = ManualEventHandler(parent=self)
        o_event.bin_manually_moved(item_id=item_id)
        self.update_statistics()
        o_event_global = EventHandler(parent=self)
        o_event_global.check_widgets()

    def bin_manual_region_changing(self, item_id):
        o_event = ManualEventHandler(parent=self)
        o_event.bin_manually_moving(item_id=item_id)

    def bin_manual_table_right_click(self, position):
        o_event = ManualRightClick(parent=self)
        o_event.manual_table_right_click()
        o_event_global = EventHandler(parent=self)
        o_event_global.check_widgets()

    # - statistics
    def update_statistics(self):
        o_stat = Statistics(parent=self)
        o_stat.update()
        o_stat.plot_statistics()

    def bin_statistics_comboBox_changed(self):
        o_stat = Statistics(parent=self)
        o_stat.plot_statistics()

    # export images
    def export_bin_images_clicked(self):
        o_export = TofBinExportLauncher(parent=self, top_parent=self.top_parent)
        o_export.show()

    def closeEvent(self, event):
        logging.info(" #### Leaving combine/binning ####")
        self.close()
