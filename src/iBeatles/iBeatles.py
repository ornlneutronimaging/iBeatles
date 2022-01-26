from qtpy import QtCore
from qtpy.QtWidgets import QApplication, QMainWindow
import sys
import os
import logging
import versioneer

from .config_handler import ConfigHandler

from .all_steps.log_launcher import LogLauncher, LogHandler
from .all_steps.event_handler import EventHandler as GeneralEventHandler

from .step1.event_handler import EventHandler as Step1EventHandler
from .step1.data_handler import DataHandler
from .step1.gui_handler import Step1GuiHandler
from .step1.time_spectra_handler import TimeSpectraHandler
from .step1.plot import Step1Plot
from .step1.check_error import CheckError
from .step1.initialization import Initialization

from .utilities.get import Get
from .session.load_previous_session_launcher import LoadPreviousSessionLauncher
from .session.session_handler import SessionHandler

from .step2.initialization import Initialization as Step2Initialization
from .step2.gui_handler import Step2GuiHandler
from .step2.roi_handler import Step2RoiHandler
from .step2.plot import Step2Plot
from .step2.normalization import Normalization
from .step2.reduction_settings_handler import ReductionSettingsHandler

from .step3.gui_handler import Step3GuiHandler
from .step3.event_handler import EventHandler as Step3EventHandler

from .binning.binning_launcher import BinningLauncher

from .fitting.fitting_launcher import FittingLauncher
from .fitting import KropffThresholdFinder

from .step6.strain_mapping_launcher import StrainMappingLauncher

from .tools.rotate_images import RotateImages

from .utilities.retrieve_data_infos import RetrieveGeneralDataInfos, RetrieveGeneralFileInfos
from .utilities.list_data_handler import ListDataHandler
from .utilities.roi_editor import RoiEditor
from .utilities.bragg_edge_selection_handler import BraggEdgeSelectionHandler
from .utilities.bragg_edge_element_handler import BraggEdgeElementHandler
from .utilities.gui_handler import GuiHandler
from .utilities.add_element_editor import AddElement

from .utilities.array_utilities import find_nearest_index
from . import load_ui
from . import DataType, RegionType, DEFAULT_ROI, DEFAULT_NORMALIZATION_ROI


class MainWindow(QMainWindow):
    """ Main FastGR window
    """

    current_tab = 0   # this will be used in case user request to see a tab is not allowed yet
    session_dict = {}  # all the parameters to save to be able to recover the full session

    # log ui
    log_id = None

    config = None  # config such as name of log file, ...

    default_path = {'sample': '',
                    'ob': '',
                    'normalized': '',
                    'time_spectra': '',
                    'time_spectra_normalized': ''}

    list_files = {'sample': [],    # ex data_files
                  'ob': [],
                  'normalized': [],
                  'time_spectra': []}

    DEBUGGING = True
    loading_flag = False
    current_data_type = 'sample'
    cbar = None
    live_data = []
    add_element_editor_ui = None
    roi_editor_ui = {'sample': None,
                     'ob': None,
                     'normalized': None}

    # used to report in status bar the error messages
    steps_error = {'step1': {'status': True,
                             'message': ''}}

    # binning window stuff
    binning_ui = None
    binning_line_view = {'ui': None,
                         'pos': None,
                         'adj': None,
                         'pen': None,
                         'image_view': None,
                         'roi': None}

    binning_roi = None    # x0, x1, width, height, bin_size
    # binning_bin_size = 20
    binning_done = False

    ## FITTING TAB
    # fitting window stuff
    fitting_image_view = None
    there_is_a_roi = False
    init_sigma_alpha_ui = None
    fitting_ui = None
    fitting_story_ui = None
    advanced_selection_ui = None
    fitting_set_variables_ui = None
    fitting_selection = {'nbr_column': -1,
                         'nbr_row': -1}
    fitting_bragg_edge_linear_selection = []   # [left lambda, right lambda]
    fitting_transparency_slider_value = 50      # from 0 to 100
    display_active_row_flag = True
    # fitting_lr = None
    table_loaded_from_session = False

    # strain mapping ui (step6)
    strain_mapping_ui = None

    # rotate images ui
    rotate_ui = None

    # table dictionary used in fitting/binning/advanced_selection/review
    march_table_dictionary = {}
    table_fitting_story_dictionary = {}
    table_dictionary_from_session = None

    # table dictionary for kropff
    kropff_table_dictionary = {}

    # new entry will be local_bragg_edge_list['new_name'] = {'lattice': value, 'crystal_structure': 'FCC'}
    local_bragg_edge_list = {}
    selected_element_bragg_edges_array = []
    selected_element_hkl_array = []
    selected_element_name = ''

    # # [['label', 'x0', 'y0', 'width', 'height', 'group'], ...]
    # init_array = ['label_roi', '0', '0', '20', '20', '0']

    # [[use?, x0, y0, width, height, mean_counts]]
    init_array_normalization = [True, 0, 0, 20, 20, RegionType.background]

    # list roi ui id (when multiple roi in plots)
    list_roi_id = {'sample': [],
                   'ob': [],
                   'normalization': [],
                   'normalized': []}

    list_label_roi_id = {'sample': [],
                         'ob': [],
                         'normalization': [],
                         'normalized': []}

    list_bragg_edge_selection_id = {'sample': None,
                                    'ob': None,
                                    'normalized': None}

    list_roi = {'sample': [],
                'ob': [],
                'normalization': [],
                'normalized': []}

    old_list_roi = {'sample': [],
                    'ob': [],
                    'normalized': []}

    list_file_selected = {'sample': [],
                          'ob': [],
                          'normalized': []}

    current_bragg_edge_x_axis = {'sample': [],
                                 'ob': [],
                                 'normalized': [],
                                 'normalization': []}
    normalized_lambda_bragg_edge_x_axis = []  # will be used by the fitting window

    step2_ui = {'area': None,
                'image_view': None,
                'roi': None,
                'bragg_edge_plot': None,
                'normalized_profile_plot': None,
                'caxis': None,
                'xaxis_tof': None,
                'xaxis_lambda': None,
                'xaxis_file_index': None,
                'bragg_edge_selection': None}

    xaxis_button_ui = {'sample': {'file_index': None,
                                  'tof': None,
                                  'lambda': None},
                       'ob': {'file_index': None,
                              'tof': None,
                              'lambda': None},
                       'normalized': {'file_index': None,
                                      'tof': None,
                                      'lambda': None},
                       'normalization': {'file_index': None,
                                         'tof': None,
                                         'lambda': None},
                       }

    # dictionary that will save the pan and zoom of each of the image view
    image_view_settings = {DataType.sample: {'state': None,
                                             'histogram': None,
                                             'first_time_using_histogram': False,
                                             'first_time_using_state': False,
                                             },
                           DataType.ob: {'state': None,
                                         'histogram': None,
                                         'first_time_using_histogram': False,
                                         'first_time_using_state': False,
                                         },
                           DataType.normalization: {'state': None,
                                                    'histogram': None,
                                                    'first_time_using_histogram': True,
                                                    'first_time_using_state'     : True,
                                                    },
                           DataType.normalized: {'state': None,
                                                 'histogram': None,
                                                 'first_time_using_histogram': False,
                                                 'first_time_using_state'     : False,
                                                 },
                           DataType.bin: {'state': None,
                                          'histogram': None,
                                          'first_time_using_histogram': True,
                                          'first_time_using_state'     : True,
                                          },
                           DataType.fitting: {'state': None,
                                              'histogram': None,
                                              'first_time_using_histogram': True,
                                              'first_time_using_state': True,
                                              }
                           }

    # use to display lable that illustrate normalization process in tab2
    normalization_label = {'data_ob': '',
                           'data': '',
                           'no_data': '',
                           'previous_status': {'data': False,
                                               'ob': False},
                           }

    # kropff
    kropff_fitting = None  # pyqtgraph plot
    kropff_is_automatic_bragg_peak_threshold_finder = True
    kropff_automatic_threshold_finder_algorithm = KropffThresholdFinder.sliding_average

    def __init__(self, parent=None):
        """ 
        Initialization
        Parameters
        ----------
        """
        # Base class
        super(MainWindow, self).__init__(parent)

        self.ui = load_ui('ui_mainWindow.ui', baseinstance=self)
        self.setup()
        self.init_interface()

        # configuration of config
        o_get = Get(parent=self)
        log_file_name = o_get.get_log_file_name()
        self.log_file_name = log_file_name
        logging.basicConfig(filename=log_file_name,
                            filemode='a',
                            format='[%(levelname)s] - %(asctime)s - %(message)s',
                            level=logging.INFO)
        logging.info("*** Starting a new session ***")
        logging.info(f" Version: {versioneer.get_version()}")

        self.automatic_load_of_previous_session()

    def check_log_file_size(self):
        o_handler = LogHandler(parent=self,
                               log_file_name=self.log_file_name)
        o_handler.cut_log_size_if_bigger_than_buffer()

    def init_interface(self):
        o_gui = Initialization(parent=self)
        o_gui.all()
        self.update_delta_lambda()
        o_gui.connect_widgets()

        # init bragg edge element
        BraggEdgeElementHandler(parent=self)

        o_gui_2 = Step2Initialization(parent=self)
        o_gui_2.pyqtgraph()
        o_gui_2.table()

    def setup(self):

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

        for _key in self.default_path.keys():
            self.default_path[_key] = current_folder

        # self.sample_path = current_folder
        # self.ob_path = current_folder
        # self.normalized_path = current_folder
        # self.time_spectra_path = current_folder
        # self.time_spectra_normalized_path = current_folder

        self.data_metadata = {DataType.sample: {'title': "Select folder or list of files",
                                                'list_widget_ui': self.ui.list_sample,
                                                'folder': current_folder,
                                                'general_infos': None,
                                                'data': [],
                                                'xaxis': 'file_index',
                                                'time_spectra': {'folder': '',
                                                                 'filename': '',
                                                                 },
                                                },
                              DataType.ob: {'title': 'Select folder or list of files',
                                            'list_widget_ui': self.ui.list_open_beam,
                                            'folder': current_folder,
                                            'general_infos': None,
                                            'xaxis': 'file_index',
                                            'data': [],
                                            },
                              DataType.normalized: {'title': 'Select folder or list of files',
                                                    'folder': current_folder,
                                                    'general_infos': None,
                                                    'data': [],
                                                    'xaxis': 'file_index',
                                                    'data_live_selection': [],
                                                    'time_spectra': {'folder': '',
                                                                     'filename': '',
                                                                     },
                                                    },
                              DataType.normalization: {'data': [],
                                                       },
                              'time_spectra': {'title': 'Select file',
                                               'folder': current_folder,
                                               'normalized_folder': current_folder,
                                               'general_infos': None,
                                               'data': [],
                                               'lambda': [],
                                               'full_file_name': '',
                                               'normalized_data': [],
                                               'normalized_lambda': []},
                              DataType.bin: {'ui_accessed': False,
                                             },
                              DataType.fitting: {'ui_accessed': False,
                                                 }
                              }

        self.range_files_to_normalized_step2 = {'file_index': [],
                                                'tof': [],
                                                'lambda': []}

        self.list_roi[DataType.sample] = [DEFAULT_ROI]
        self.list_roi[DataType.ob] = [DEFAULT_ROI]
        self.list_roi[DataType.normalized] = [DEFAULT_ROI]
        self.list_roi[DataType.normalization] = [DEFAULT_NORMALIZATION_ROI]

        self.old_list_roi[DataType.sample] = [DEFAULT_ROI]
        self.old_list_roi[DataType.ob] = [DEFAULT_ROI]
        self.old_list_roi[DataType.normalized] = [DEFAULT_ROI]
        self.old_list_roi[DataType.normalization] = [DEFAULT_NORMALIZATION_ROI]

    def automatic_load_of_previous_session(self):
        o_get = Get(parent=self)
        full_config_file_name = o_get.get_automatic_config_file_name()
        if os.path.exists(full_config_file_name):
            load_session_ui = LoadPreviousSessionLauncher(parent=self)
            load_session_ui.show()

    # Menu
    def load_session_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.load_from_file()
        o_session.load_to_ui()

    def save_session_clicked(self):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.save_to_file()

    def menu_view_load_data_clicked(self):
        self.ui.tabWidget.setCurrentIndex(0)

    def menu_view_normalization_clicked(self):
        self.ui.tabWidget.setCurrentIndex(1)

    def menu_view_normalized_clicked(self):
        self.ui.tabWidget.setCurrentIndex(2)

    def menu_view_binning_clicked(self):
        o_event = GeneralEventHandler(parent=self)
        if o_event.is_step_selected_allowed(step_index_requested=3):
            BinningLauncher(parent=self)

    def menu_view_fitting_clicked(self):
        o_event = GeneralEventHandler(parent=self)
        if o_event.is_step_selected_allowed(step_index_requested=4):
            FittingLauncher(parent=self)

    def menu_view_strain_mapping_clicked(self):
        o_event = GeneralEventHandler(parent=self)
        if o_event.is_step_selected_allowed(step_index_requested=5):
            StrainMappingLauncher(parent=self)

    def rotate_normalized_images_clicked(self):
        o_event = GeneralEventHandler(parent=self)
        if o_event.is_step_selected_allowed(step_index_requested=6):
            RotateImages(parent=self)

    def log_clicked(self):
        LogLauncher(parent=self)

    # TAB 1, 2 and 3
    def tab_widget_changed(self, tab_selected):

        general_event_handler = GeneralEventHandler(parent=self)
        is_step_selected_allowed = general_event_handler.is_step_selected_allowed(step_index_requested=tab_selected)

        if is_step_selected_allowed:

            if tab_selected == 1:  # normalization

                o_gui = Step2GuiHandler(parent=self)
                o_gui.update_widgets()
                time_spectra_data = self.data_metadata['time_spectra']['data']
                if time_spectra_data == []:
                    o_gui.enable_xaxis_button(tof_flag=False)
                else:
                    o_gui.enable_xaxis_button(tof_flag=True)
                self.step2_file_index_radio_button_clicked()
                o_plot = Step2Plot(parent=self)
                o_plot.display_bragg_edge()

            self.current_tab = tab_selected

        else:
            self.ui.tabWidget.setCurrentIndex(self.current_tab)

    def material_display_clicked(self, status):
        self.ui.material_display_checkbox_2.setChecked(status)
        o_gui = Step1GuiHandler(parent=self)
        o_gui.check_time_spectra_widgets()
        o_plot = Step1Plot(parent=self)
        o_plot.display_general_bragg_edge()

    def material_display_2_clicked(self, status):
        self.ui.material_display_checkbox.setChecked(status)
        o_gui = Step1GuiHandler(parent=self)
        o_gui.check_time_spectra_widgets()
        o_plot = Step1Plot(parent=self)
        o_plot.display_general_bragg_edge()

    def roi_image_view_changed(self, mouse_selection=True):
        o_plot = Step1Plot(parent=self, data_type='sample')
        o_plot.display_bragg_edge(mouse_selection=mouse_selection)

    def roi_ob_image_view_changed(self, mouse_selection=True):
        o_plot = Step1Plot(parent=self, data_type='ob')
        o_plot.display_bragg_edge(mouse_selection=mouse_selection)

    def retrieve_general_infos(self, data_type='sample'):
        if data_type in (DataType.sample, DataType.normalized):
            o_general_infos = RetrieveGeneralFileInfos(parent=self, data_type=data_type)
            o_general_infos.update()

    def retrieve_general_data_infos(self, data_type='sample'):
        if data_type == 'sample':
            self.sample_retrieve_general_data_infos()
        elif data_type == 'ob':
            self.open_beam_retrieve_general_data_infos()
        elif data_type == 'normalized':
            self.normalized_retrieve_general_data_infos()

    def load_data_tab_changed(self, tab_index):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.load_data_tab_changed(tab_index=tab_index)
        if tab_index == 0:
            self.current_data_type = 'sample'
            self.ui.image_preview.setCurrentIndex(0)
        else:
            self.current_data_type = 'ob'
            self.ui.image_preview.setCurrentIndex(1)

    def roi_editor_button_clicked(self):
        o_roi_editor = RoiEditor(parent=self)
        o_roi_editor.run()

    def refresh_roi(self, data_type='sample'):
        o_step1_plot = Step1Plot(parent=self, data_type=data_type)
        o_step1_plot.display_bragg_edge()

    def bragg_edge_selection_changed(self):
        o_gui = GuiHandler(parent=self)
        data_type = o_gui.get_active_tab()

        _ui_list = None
        if data_type == 'sample':
            _ui_list = self.ui.list_sample
        elif data_type == 'ob':
            _ui_list = self.ui.list_open_beam
        else:
            _ui_list = self.ui.list_normalized

        _ui_list.blockSignals(True)
        o_bragg_selection = BraggEdgeSelectionHandler(parent=self, data_type=data_type)
        o_bragg_selection.update_dropdown()

        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type=data_type)
        o_retrieve_data_infos.update()

        _ui_list.blockSignals(False)

    # Instrument    

    # global load data instruments widgets handler
    def instruments_widgets(self, update_delta_lambda=True):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.sync_instrument_widgets(source='load_data')
        if update_delta_lambda:
            self.update_delta_lambda()
        o_data = DataHandler(parent=self)
        o_data.load_time_spectra()
        o_plot = Step1Plot(parent=self, data_type='sample')
        o_plot.display_bragg_edge(mouse_selection=False)

    def distance_source_detector_changed(self):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.block_instrument_widgets(status=True)
        self.instruments_widgets()
        o_gui.block_instrument_widgets(status=False)

    def beam_rate_changed(self):
        self.instruments_widgets()

    def detector_offset_changed(self):
        self.instruments_widgets()

    # global normalized instruments widgets handler
    def instruments_2_widgets(self, update_delta_lambda=True):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.block_instrument_widgets(status=True)
        o_gui.sync_instrument_widgets(source='normalized')
        if update_delta_lambda:
            self.update_delta_lambda()
        o_data = DataHandler(parent=self, data_type='normalized')
        o_data.load_time_spectra()
        o_plot = Step1Plot(parent=self, data_type='normalized')
        o_plot.display_bragg_edge(mouse_selection=False)

        o_event = Step1EventHandler(parent=self)
        o_event.sample_list_selection_changed()

        o_gui.block_instrument_widgets(status=False)

    def distance_source_detector_2_changed(self):
        self.instruments_2_widgets()

    def beam_rate_2_changed(self):
        self.instruments_2_widgets()

    def detector_offset_2_changed(self):
        self.instruments_2_widgets(update_delta_lambda=False)

    # Material widgets

    def add_element_clicked(self):
        _add_ele = AddElement(parent=self)
        _add_ele.run()

    def list_of_element_index_changed(self, index):
        self.ui.list_of_elements_2.blockSignals(True)
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_lattice_and_crystal_when_index_selected(source='load_data')
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self, data_type='sample')
        o_plot.display_general_bragg_edge()
        self.ui.list_of_elements_2.blockSignals(False)

    def list_of_element_2_index_changed(self, index):
        self.ui.list_of_elements.blockSignals(True)
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_lattice_and_crystal_when_index_selected(source='normalized')
        BraggEdgeElementHandler(parent=self)
        self.ui.list_of_elements.blockSignals(False)

    def crystal_structure_index_changed(self, index):
        self.ui.crystal_structure_2.setCurrentIndex(index)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self)
        o_plot.display_general_bragg_edge()

    def crystal_structure_2_index_changed(self, index):
        self.ui.crystal_structure.setCurrentIndex(index)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self)
        o_plot.display_general_bragg_edge()

    def lattice_text_changed(self):
        _contain = str(self.ui.lattice_parameter.text())
        self.ui.lattice_parameter_2.setText(_contain)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self)
        o_plot.display_general_bragg_edge()

    def lattice_2_text_changed(self):
        _contain = str(self.ui.lattice_parameter_2.text())
        self.ui.lattice_parameter.setText(_contain)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self)
        o_plot.display_general_bragg_edge()

    def reset_lattice_button_clicked(self):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_lattice_and_crystal_when_index_selected(source='load_data',
                                                             fill_crystal_structure_flag=False)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self, data_type='sample')
        o_plot.display_general_bragg_edge()

    def reset_lattice_button_2_clicked(self):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_lattice_and_crystal_when_index_selected(source='normalized',
                                                             fill_crystal_structure_flag=False)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self, data_type='normalized')
        o_plot.display_general_bragg_edge()

    def reset_crystal_structure_button_clicked(self):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_lattice_and_crystal_when_index_selected(source='load_data',
                                                             fill_lattice_flag=False)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self, data_type='sample')
        o_plot.display_general_bragg_edge()

    def reset_crystal_structure_button_2_clicked(self):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_lattice_and_crystal_when_index_selected(source='normalized',
                                                             fill_lattice_flag=False)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self, data_type='normalized')
        o_plot.display_general_bragg_edge()

    def check_files_error(self):
        CheckError(parent=self)

    # TAB 1: Load Data Tab

    def sample_import_button_clicked(self):
        o_event = Step1EventHandler(parent=self, data_type='sample')
        o_event.import_button_clicked()

    def select_load_data_row(self, data_type='sample', row=0):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.select_load_data_row(data_type=data_type,
                                   row=row)

    def sample_retrieve_general_data_infos(self):
        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type='sample')
        o_retrieve_data_infos.update()

    def open_beam_retrieve_general_data_infos(self):
        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type='ob')
        o_retrieve_data_infos.update()

    def sample_list_right_click(self, position):
        o_list_handler = ListDataHandler(parent=self)
        o_list_handler.right_click(position=position)

    def open_beam_import_button_clicked(self):
        o_event = Step1EventHandler(parent=self, data_type='ob')
        o_event.import_button_clicked()

        # self.loading_flag = True
        # o_load = DataHandler(parent=self)
        # o_load.retrieve_files(data_type='ob')
        # if not o_load.user_canceled:
        #     self.select_load_data_row(data_type='ob', row=0)
        #     self.retrieve_general_infos(data_type='ob')
        #     self.retrieve_selected_row_infos(data_type='ob')
        #     o_plot = Step1Plot(parent=self, data_type='ob')
        #     o_plot.display_bragg_edge()
        #     self.check_files_error()

    def open_beam_list_selection_changed(self):
        if not self.loading_flag:
            o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type='ob')
            o_retrieve_data_infos.update()
            self.roi_ob_image_view_changed(mouse_selection=False)
        else:
            self.loading_flag = False

    def time_spectra_import_button_clicked(self):
        o_load = DataHandler(parent=self)
        is_file_selected = o_load.retrieve_time_spectra()
        if is_file_selected:
            o_gui = Step1GuiHandler(parent=self)
            o_gui.check_time_spectra_widgets()

    def time_spectra_preview_button_clicked(self):
        o_time_spectra = TimeSpectraHandler(parent=self)
        o_time_spectra.display()

    def update_delta_lambda(self):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_delta_lambda()

    def roi_algorithm_is_add_clicked(self):
        self.ui.ob_roi_add_button.setChecked(True)
        self.ui.normalized_roi_add_button.setChecked(True)
        self.roi_image_view_changed()

    def roi_algorithm_is_mean_clicked(self):
        self.ui.ob_roi_mean_button.setChecked(True)
        self.ui.normalized_roi_mean_button.setChecked(True)
        self.roi_image_view_changed()

    def ob_roi_algorithm_is_add_clicked(self):
        self.ui.roi_add_button.setChecked(True)
        self.ui.normalized_roi_add_button.setChecked(True)
        self.roi_ob_image_view_changed()

    def ob_roi_algorithm_is_mean_clicked(self):
        self.ui.roi_mean_button.setChecked(True)
        self.ui.normalized_roi_mean_button.setChecked(True)
        self.roi_ob_image_view_changed()

    def file_index_xaxis_button_clicked(self):
        self.data_metadata[DataType.sample]['xaxis'] = 'file_index'
        o_event = Step1EventHandler(parent=self)
        o_event.sample_list_selection_changed()

    def tof_xaxis_button_clicked(self):
        self.data_metadata[DataType.sample]['xaxis'] = 'tof'
        o_event = Step1EventHandler(parent=self)
        o_event.sample_list_selection_changed()

    def lambda_xaxis_button_clicked(self):
        self.data_metadata[DataType.sample]['xaxis'] = 'lambda'
        o_event = Step1EventHandler(parent=self)
        o_event.sample_list_selection_changed()

    def sample_list_selection_changed(self):
        o_event = Step1EventHandler(parent=self)
        o_event.sample_list_selection_changed()

    def ob_file_index_xaxis_button_clicked(self):
        self.data_metadata[DataType.ob]['xaxis'] = 'file_index'
        self.open_beam_list_selection_changed()

    def ob_tof_xaxis_button_clicked(self):
        self.data_metadata[DataType.ob]['xaxis'] = 'tof'
        self.open_beam_list_selection_changed()

    def ob_lambda_xaxis_button_clicked(self):
        self.data_metadata[DataType.ob]['xaxis'] = 'lambda'
        self.open_beam_list_selection_changed()

    # TAB 2:

    def normalization_manual_roi_changed(self):
        self.ui.normalization_tableWidget.blockSignals(True)
        o_roi = Step2RoiHandler(parent=self)
        o_roi.save_roi()
        o_plot = Step2Plot(parent=self)
        o_plot.update_roi_table()
        o_plot.update_label_roi()
        o_plot.check_error_in_roi_table()
        o_plot.display_bragg_edge()
        self.ui.normalization_tableWidget.blockSignals(False)

    def normalization_row_status_changed(self):
        o_roi = Step2RoiHandler(parent=self)
        o_roi.save_table()
        o_roi.enable_selected_roi()
        o_plot = Step2Plot(parent=self)
        o_plot.display_bragg_edge()
        o_plot.update_label_roi()
        o_gui = Step2GuiHandler(parent=self)
        o_gui.check_run_normalization_button()

    def normalization_row_status_region_type_changed(self, value):
        self.normalization_row_status_changed()
        o_gui = Step2GuiHandler(parent=self)
        o_gui.check_run_normalization_button()

    def normalization_remove_roi_button_clicked(self):
        self.ui.normalization_tableWidget.blockSignals(True)
        o_roi = Step2RoiHandler(parent=self)
        o_roi.remove_roi()
        o_plot = Step2Plot(parent=self)
        o_plot.display_roi()
        o_plot.display_bragg_edge()
        o_gui = Step2GuiHandler(parent=self)
        o_gui.check_run_normalization_button()
        self.ui.normalization_tableWidget.blockSignals(False)

    def normalization_add_roi_button_clicked(self):
        self.ui.normalization_tableWidget.blockSignals(True)
        o_roi = Step2RoiHandler(parent=self)
        o_roi.add_roi()
        o_gui = Step2GuiHandler(parent=self)
        o_gui.check_run_normalization_button()
        self.ui.normalization_tableWidget.blockSignals(False)

    def normalization_button_clicked(self):
        o_norm = Normalization(parent=self)
        o_norm.run_and_export()
        self.ui.tabWidget.setCurrentIndex(2)

    def step2_file_index_radio_button_clicked(self):
        self.data_metadata[DataType.normalization]['xaxis'] = 'file_index'
        o_plot = Step2Plot(parent=self)
        o_plot.display_bragg_edge()

    def step2_tof_radio_button_clicked(self):
        self.data_metadata[DataType.normalization]['xaxis'] = 'tof'
        o_plot = Step2Plot(parent=self)
        o_plot.display_bragg_edge()

    def step2_lambda_radio_button_clicked(self):
        self.data_metadata[DataType.normalization]['xaxis'] = 'lambda'
        o_plot = Step2Plot(parent=self)
        o_plot.display_bragg_edge()

    def normalization_tableWidget_cell_changed(self, row, col):
        o_roi = Step2RoiHandler(parent=self)
        o_roi.save_table()
        o_plot = Step2Plot(parent=self)
        o_plot.display_roi()
        o_plot.check_error_in_roi_table()

    def step2_bragg_edge_selection_changed(self):
        lr = self.bragg_edge_selection
        selection = list(lr.getRegion())

        x_axis = self.current_bragg_edge_x_axis['normalization']
        left_index = find_nearest_index(array=x_axis, value=selection[0])
        right_index = find_nearest_index(array=x_axis, value=selection[1])
        self.range_files_to_normalized_step2['file_index'] = [left_index, right_index]

    def normalization_moving_average_settings_clicked(self):
        settings = ReductionSettingsHandler(parent=self)
        settings.show()

    # TAB 3: Normalized Data Tab

    def normalized_time_spectra_import_button_clicked(self):
        o_load = DataHandler(parent=self, data_type='normalized')
        o_load.retrieve_time_spectra(auto_load=False)
        o_gui = Step3GuiHandler(parent=self)
        o_gui.check_time_spectra_widgets()

    def normalized_time_spectra_preview_button_clicked(self):
        o_time_spectra = TimeSpectraHandler(parent=self, data_type='normalized')
        o_time_spectra.display()

    def normalized_import_button_clicked(self):
        o_event = Step3EventHandler(parent=self, data_type='normalized')
        o_event.import_button_clicked()

    def normalized_retrieve_general_data_infos(self):
        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type='normalized')
        o_retrieve_data_infos.update()

    def select_normalized_row(self, row=0):
        o_gui = Step3GuiHandler(parent=self)
        o_gui.select_normalized_row(row=row)

    def normalized_list_selection_changed(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if not self.loading_flag:
            o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type=DataType.normalized)
            o_retrieve_data_infos.update()
            self.roi_normalized_image_view_changed(mouse_selection=False)
        else:
            self.loading_flag = False
        QApplication.restoreOverrideCursor()

    def roi_normalized_image_view_changed(self, mouse_selection=True):
        o_plot = Step1Plot(parent=self, data_type='normalized')
        o_plot.display_bragg_edge(mouse_selection=mouse_selection)

    def normalized_roi_algorithm_is_add_clicked(self):
        self.ui.roi_add_button.setChecked(True)
        self.ui.ob_roi_add_button.setChecked(True)
        self.roi_normalized_image_view_changed()

    def normalized_roi_algorithm_is_mean_clicked(self):
        self.ui.roi_mean_button.setChecked(True)
        self.ui.ob_roi_mean_button.setChecked(True)
        self.roi_normalized_image_view_changed()

    def normalized_file_index_xaxis_button_clicked(self):
        self.data_metadata[DataType.normalized]['xaxis'] = 'file_index'
        o_event = Step3EventHandler(parent=self)
        o_event.sample_list_selection_changed()

    def normalized_tof_xaxis_button_clicked(self):
        self.data_metadata[DataType.normalized]['xaxis'] = 'tof'
        o_event = Step3EventHandler(parent=self)
        o_event.sample_list_selection_changed()

    def normalized_lambda_xaxis_button_clicked(self):
        self.data_metadata[DataType.normalized]['xaxis'] = 'lambda'
        o_event = Step3EventHandler(parent=self)
        o_event.sample_list_selection_changed()

    def closeEvent(self, event):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.automatic_save()
        self.check_log_file_size()
        logging.info(" #### Leaving iBeatles ####")
        self.close()

    def test_button_clicked(self):
        self.ui.area.setVisible(True)


def main(args):
    app = QApplication(args)
    app.setStyle("Fusion")
    app.aboutToQuit.connect(clean_up)
    app.setApplicationDisplayName("iBeatles")
    # app.setWindowIcon(PyQt4.QtGui.QIcon(":/icon.png"))
    application = MainWindow()
    application.show()
    sys.exit(app.exec_())


def clean_up():
    app = QApplication.instance()
    app.closeAllWindows()
