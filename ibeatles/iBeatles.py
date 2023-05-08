from qtpy import QtCore
from qtpy.QtWidgets import QApplication, QMainWindow
import os
import logging
import warnings

from ibeatles import load_ui, get_version
from ibeatles import DataType, RegionType, DEFAULT_ROI, DEFAULT_NORMALIZATION_ROI, ScrollBarParameters

from ibeatles.config_handler import ConfigHandler

from ibeatles.all_steps.log_launcher import LogLauncher, LogHandler
from ibeatles.all_steps.event_handler import EventHandler as GeneralEventHandler
from ibeatles.all_steps.list_hkl_lambda_d0 import ListHKLLambdaD0Handler
from ibeatles.all_steps.infos_launcher import InfosLauncher

from ibeatles.step1.event_handler import EventHandler as Step1EventHandler
from ibeatles.step1.data_handler import DataHandler
from ibeatles.step1.gui_handler import Step1GuiHandler
from ibeatles.step1.time_spectra_handler import TimeSpectraHandler
from ibeatles.step1.plot import Step1Plot
from ibeatles.step1.check_error import CheckError
from ibeatles.step1.initialization import Initialization

from ibeatles.utilities.get import Get
from ibeatles.session.load_previous_session_launcher import LoadPreviousSessionLauncher
from ibeatles.session.session_handler import SessionHandler

from ibeatles.step2.initialization import Initialization as Step2Initialization
from ibeatles.step2.gui_handler import Step2GuiHandler
from ibeatles.step2.roi_handler import Step2RoiHandler
from ibeatles.step2.plot import Step2Plot
from ibeatles.step2.normalization import Normalization
from ibeatles.step2.reduction_settings_handler import ReductionSettingsHandler

from ibeatles.step3.gui_handler import Step3GuiHandler
from ibeatles.step3.event_handler import EventHandler as Step3EventHandler

from ibeatles.binning.binning_launcher import BinningLauncher

from ibeatles.fitting.fitting_launcher import FittingLauncher
from ibeatles.fitting import KropffThresholdFinder

from ibeatles.step6.strain_mapping_launcher import StrainMappingLauncher

from ibeatles.tools.rotate_images import RotateImages

from ibeatles.utilities.retrieve_data_infos import RetrieveGeneralDataInfos, RetrieveGeneralFileInfos
from ibeatles.utilities.list_data_handler import ListDataHandler
from ibeatles.utilities.roi_editor import RoiEditor
from ibeatles.utilities.bragg_edge_selection_handler import BraggEdgeSelectionHandler
from ibeatles.utilities.bragg_edge_element_handler import BraggEdgeElementHandler
from ibeatles.utilities.gui_handler import GuiHandler
from ibeatles.add_element.add_element_editor import AddElement

from ibeatles.utilities.array_utilities import find_nearest_index

from ibeatles.about.about_launcher import AboutLauncher

warnings.filterwarnings("ignore")


class MainWindow(QMainWindow):
    """
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
    roi_editor_ui = {DataType.sample: None,
                     DataType.ob: None,
                     DataType.normalized: None}

    # infos mainwindow
    infos_id = None
    infos_dict = {DataType.sample: None,
                  DataType.ob: None,
                  DataType.normalized: None}
    # ui of infos pushButton
    infos_ui_dict = {DataType.sample: None,
                     DataType.ob: None,
                     DataType.normalized: None}

    # scrollbar below Bragg plot for main 3 data sets
    hkl_scrollbar_ui = {'label': {DataType.sample: None,
                                  DataType.ob: None,
                                  DataType.normalized: None},
                        'widget': {DataType.sample: None,
                                  DataType.ob: None,
                                  DataType.normalized: None},
                        }

    hkl_scrollbar_dict = {ScrollBarParameters.maximum: 1,
                          ScrollBarParameters.value: 0}

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

    # list hkl, lambda and d0
    list_hkl_lambda_d0_ui = None

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

    # new entry will be local_bragg_edge_list['new_name'] = {Material.lattice: value,
    #                                                        Material.crystal_structure: 'FCC',
    #                                                        Material.hkl_d0: None',
    #                                                        Material.method_used: Material.via_lattice_and_crystal_structure}
    local_bragg_edge_list = {}
    selected_element_bragg_edges_array = []
    selected_element_hkl_array = []
    selected_element_name = ''

    # just like above but for user defined ones
    user_defined_bragg_edge_list = {}

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
                                             'histogram': {'mean': None,
                                                           'sum': None,
                                                          },
                                             'first_time_using_histogram': {'mean': True,
                                                                            'sum': True,
                                                                            },
                                             'first_time_using_state': False,
                                             },
                           DataType.ob: {'state': None,
                                         'histogram': {'mean': None,
                                                       'sum': None,
                                                       },
                                         'first_time_using_histogram': {'mean': True,
                                                                        'sum': True,
                                                                        },
                                         'first_time_using_state': False,
                                         },
                           DataType.normalization: {'state': None,
                                                    'histogram': None,
                                                    'first_time_using_histogram': True,
                                                    'first_time_using_state': True,
                                                    },
                           DataType.normalized: {'state': None,
                                                 'histogram': {'mean': None,
                                                               'sum': None,
                                                               },
                                                 'first_time_using_histogram': {'mean': True,
                                                                                'sum': True,
                                                                                },
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

    kropff_bragg_peak_good_fit_conditions = {'l_hkl_error': {'state': True,
                                                             'value': 0.01},
                                             't_error'    : {'state': True,
                                                             'value': 0.01},
                                             'sigma_error': {'state': True,
                                                             'value': 0.01},
                                             }
    kropff_lambda_settings = None

    def __init__(self, parent=None):
        """ 
        Initialization
        Parameters
        ----------
        """
        # Base class
        super(MainWindow, self).__init__(parent)

        self.ui = load_ui('ui_mainWindow.ui', baseinstance=self)
        self.setWindowTitle("iBeatles")
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
        logging.info(f" Version: {get_version()}")

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
        o_gui_2.all()

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

        self.infos_ui_dict = {DataType.sample: self.ui.sample_infos_pushButton,
                              DataType.ob: self.ui.ob_infos_pushButton,
                              DataType.normalized: self.ui.normalized_infos_pushButton}

    def automatic_load_of_previous_session(self):
        o_get = Get(parent=self)
        full_config_file_name = o_get.get_automatic_config_file_name()
        if os.path.exists(full_config_file_name):
            load_session_ui = LoadPreviousSessionLauncher(parent=self)
            load_session_ui.show()
        else:
            o_session = SessionHandler(parent=self)
            self.session_dict = o_session.session_dict

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

    def view_instrument_and_material_settings_clicked(self, state):
        """will make the instrument and material widgets visible, only if we are not working with the
        normalization tab"""

        o_gui = GuiHandler(parent=self)
        tab_selected = o_gui.get_active_tab()

        # ignore it if we are working with the normalization tab
        if tab_selected == DataType.normalization:
            return

        self.ui.instrument_and_material_settings.setVisible(state)

    def log_clicked(self):
        LogLauncher(parent=self)

    def about_clicked(self):
        o_about = AboutLauncher(parent=self)
        o_about.show()

    # TAB 1, 2 and 3  ===========================================================================================
    def tab_widget_changed(self, tab_selected):

        general_event_handler = GeneralEventHandler(parent=self)
        is_step_selected_allowed = general_event_handler.is_step_selected_allowed(step_index_requested=tab_selected)

        if is_step_selected_allowed:

            if tab_selected == 1:  # normalization

                material_instrument_group_visible = False
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

            elif (tab_selected == 0) or (tab_selected == 2):

                BraggEdgeElementHandler(parent=self)
                o_plot = Step1Plot(parent=self)
                o_plot.display_general_bragg_edge()
                self.update_hkl_lambda_d0()

                material_instrument_group_visible = self.ui.action_Instrument_Material_Settings.isChecked()

            self.current_tab = tab_selected
            self.ui.instrument_and_material_settings.setVisible(material_instrument_group_visible)

        else:
            self.ui.tabWidget.setCurrentIndex(self.current_tab)

    def infos_button_clicked(self):
        InfosLauncher(parent=self)

    def infos_window_update(self, data_type=DataType.sample):
        """will update the infos view if this one is active"""
        if self.infos_dict[data_type]:
            self.infos_ui_dict[data_type].setEnabled(True)
        if self.infos_id:
            self.infos_id.update()

    def material_display_clicked(self, status):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.check_time_spectra_widgets()
        o_plot = Step1Plot(parent=self)
        o_plot.display_general_bragg_edge()

    # def material_display_2_clicked(self, status):
    #     self.ui.material_display_checkbox.setChecked(status)
    #     o_gui = Step1GuiHandler(parent=self)
    #     o_gui.check_time_spectra_widgets()
    #     o_plot = Step1Plot(parent=self)
    #     o_plot.display_general_bragg_edge()

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
        # o_gui.sync_instrument_widgets(source='load_data')
        if update_delta_lambda:
            self.update_delta_lambda()
        o_data = DataHandler(parent=self)
        o_data.load_time_spectra()
        o_plot = Step1Plot(parent=self)
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

    def add_element_clicked(self):
        _add_ele = AddElement(parent=self)
        _add_ele.run()

    def list_of_element_index_changed(self, index, data_type=None):
        if type(index) == int:
            return

        if data_type is None:
            o_gui = GuiHandler(parent=self)
            data_type = o_gui.get_active_tab()

        self.ui.list_of_elements.blockSignals(True)
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_lattice_and_crystal_when_index_selected()
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self, data_type=data_type)
        o_plot.display_general_bragg_edge(data_type=data_type)
        # self.roi_image_view_changed()
        self.update_hkl_lambda_d0()
        self.check_status_of_material_widgets()
        self.ui.list_of_elements.blockSignals(False)

    def crystal_structure_index_changed(self, index):
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self)
        o_plot.display_general_bragg_edge()
        self.update_hkl_lambda_d0()

    def lattice_text_changed(self):
        # _contain = str(self.ui.lattice_parameter.text())
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self)
        o_plot.display_general_bragg_edge()
        self.update_hkl_lambda_d0()

    def reset_lattice_button_clicked(self):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_lattice_and_crystal_when_index_selected(fill_crystal_structure_flag=False)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self, data_type='sample')
        o_plot.display_general_bragg_edge()
        self.update_hkl_lambda_d0()

    def reset_crystal_structure_button_clicked(self):
        o_gui = Step1GuiHandler(parent=self)
        o_gui.update_lattice_and_crystal_when_index_selected(fill_lattice_flag=False)
        BraggEdgeElementHandler(parent=self)
        o_plot = Step1Plot(parent=self, data_type='sample')
        o_plot.display_general_bragg_edge()
        self.update_hkl_lambda_d0()

    def check_files_error(self):
        CheckError(parent=self)

    def material_list_hkl_lambda_d0_clicked(self):
        ListHKLLambdaD0Handler(parent=self)

    def list_element_changed(self, new_index):
        self.update_hkl_lambda_d0()

    def check_status_of_material_widgets(self):
        o_event = Step1EventHandler(parent=self)
        o_event.check_status_of_material_widgets()

    def update_hkl_lambda_d0(self):
        if self.list_hkl_lambda_d0_ui:
            self.list_hkl_lambda_d0_ui.refresh_populate_table()

    # TAB 1: Sample and OB Tab =========================================================================================

    def sample_import_button_clicked(self):
        o_event = Step1EventHandler(parent=self, data_type='sample')
        o_event.import_button_clicked()
        self.load_data_tab_changed(tab_index=0)

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
            o_plot = Step1Plot(parent=self)
            o_plot.display_general_bragg_edge()

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

        # update the top plot
        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type=DataType.sample)
        o_retrieve_data_infos.update(add_mean_radio_button_changed=True)

    def roi_algorithm_is_mean_clicked(self):
        self.ui.ob_roi_mean_button.setChecked(True)
        self.ui.normalized_roi_mean_button.setChecked(True)
        self.roi_image_view_changed()

        # update the top plot
        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type=DataType.sample)
        o_retrieve_data_infos.update(add_mean_radio_button_changed=True)

    def ob_roi_algorithm_is_add_clicked(self):
        self.ui.roi_add_button.setChecked(True)
        self.ui.normalized_roi_add_button.setChecked(True)
        self.roi_ob_image_view_changed()

        # update the top plot
        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type=DataType.ob)
        o_retrieve_data_infos.update(add_mean_radio_button_changed=True)

    def ob_roi_algorithm_is_mean_clicked(self):
        self.ui.roi_mean_button.setChecked(True)
        self.ui.normalized_roi_mean_button.setChecked(True)
        self.roi_ob_image_view_changed()

        # update the top plot
        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type=DataType.ob)
        o_retrieve_data_infos.update(add_mean_radio_button_changed=True)

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

    def sample_hkl_scrollbar_changed(self, value):
        self.hkl_scrollbar_dict[ScrollBarParameters.value] = value
        o_plot = Step1Plot(parent=self, data_type=DataType.sample)
        o_plot.display_bragg_edge()

    def ob_hkl_scrollbar_changed(self, value):
        self.hkl_scrollbar_dict[ScrollBarParameters.value] = value
        o_plot = Step1Plot(parent=self, data_type=DataType.ob)
        o_plot.display_bragg_edge()

    # TAB 2: Normalization Tab ==================================================================================

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
        norm_worked = o_norm.run_and_export()
        if norm_worked:
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

    # TAB 3: Normalized Tab ==================================================================================

    def normalized_time_spectra_import_button_clicked(self):
        o_load = DataHandler(parent=self, data_type='normalized')
        is_file_selected = o_load.retrieve_time_spectra()
        if is_file_selected:
            o_gui = Step3GuiHandler(parent=self)
            o_gui.check_time_spectra_widgets()
            o_plot = Step1Plot(parent=self)
            o_plot.display_general_bragg_edge()

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
            # self.roi_normalized_image_view_changed(mouse_selection=False)
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

        # update the top plot
        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type=DataType.normalized)
        o_retrieve_data_infos.update(add_mean_radio_button_changed=True)

    def normalized_roi_algorithm_is_mean_clicked(self):
        self.ui.roi_mean_button.setChecked(True)
        self.ui.ob_roi_mean_button.setChecked(True)
        self.roi_normalized_image_view_changed()

        # update the top plot
        o_retrieve_data_infos = RetrieveGeneralDataInfos(parent=self, data_type=DataType.normalized)
        o_retrieve_data_infos.update(add_mean_radio_button_changed=True)

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

    def normalized_hkl_scrollbar_changed(self, value):
        self.hkl_scrollbar_dict[ScrollBarParameters.value] = value
        o_plot = Step1Plot(parent=self, data_type='normalized')
        o_plot.display_bragg_edge()

    # GENERAL UI =======================================================================================
    def closeEvent(self, event):
        o_session = SessionHandler(parent=self)
        o_session.save_from_ui()
        o_session.automatic_save()
        self.check_log_file_size()
        logging.info(" #### Leaving iBeatles ####")
        self.close()


def main(args):
    app = QApplication(args)
    app.setStyle("Fusion")
    app.aboutToQuit.connect(clean_up)
    app.setApplicationDisplayName("iBeatles")
    app.setOrganizationName("iBeatles")
    app.setOrganizationDomain("N/A")
    app.setApplicationName("iBeatles")

    # root = os.path.dirname(os.path.realpath(__file__))
    # refresh_image = os.path.join(root, "icons/refresh.png")
    # app.setWindowIcon(QIcon(refresh_image))

    application = MainWindow()
    application.show()
    # sys.exit(app.exec_())
    app.exec_()


def clean_up():
    app = QApplication.instance()
    app.closeAllWindows()
