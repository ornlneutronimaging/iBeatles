from qtpy.QtWidgets import QFileDialog, QApplication
import json
import logging
import copy

from ibeatles import DataType, Material
from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
from ibeatles.utilities.get import Get
from ibeatles.fitting.march_dollase import SessionSubKeys as MarchSessionSubKeys
from ibeatles.fitting.kropff import SessionSubKeys as KropffSessionSubKeys

from ibeatles.session import SessionKeys, SessionSubKeys
from ibeatles.session.save_load_data_tab import SaveLoadDataTab
from ibeatles.session.save_normalization_tab import SaveNormalizationTab
from ibeatles.session.save_normalized_tab import SaveNormalizedTab
from ibeatles.session.save_bin_tab import SaveBinTab
from ibeatles.session.save_fitting_tab import SaveFittingTab
from ibeatles.session.session_utilities import SessionUtilities
from ibeatles.session.load_load_data_tab import LoadLoadDataTab
from ibeatles.session.load_normalization_tab import LoadNormalization
from ibeatles.session.load_normalized_tab import LoadNormalized
from ibeatles.session.load_bin_tab import LoadBin
from ibeatles.session.load_fitting_tab import LoadFitting
from ibeatles.session.general import General


class SessionHandler:
    config_file_name = ""
    load_successful = True

    session_dict = {SessionSubKeys.config_version: None,
                    SessionSubKeys.log_buffer_size: 500,
                    DataType.sample: {SessionSubKeys.list_files: None,
                                      SessionSubKeys.current_folder: None,
                                      SessionSubKeys.time_spectra_filename: None,
                                      SessionSubKeys.list_files_selected: None,
                                      SessionSubKeys.list_rois: None,
                                      SessionSubKeys.image_view_state: None,
                                      SessionSubKeys.image_view_histogram: None,
                                      },
                    DataType.ob: {SessionSubKeys.list_files: None,
                                  SessionSubKeys.current_folder: None,
                                  SessionSubKeys.list_files_selected: None,
                                  },
                    DataType.normalization: {SessionSubKeys.roi: None,
                                             SessionSubKeys.image_view_state: None,
                                             SessionSubKeys.image_view_histogram: None,
                                             },
                    DataType.normalized: {SessionSubKeys.list_files: None,
                                          SessionSubKeys.current_folder: None,
                                          SessionSubKeys.time_spectra_filename: None,
                                          SessionSubKeys.list_files_selected: None,
                                          SessionSubKeys.list_rois: None,
                                          SessionSubKeys.image_view_state: None,
                                          SessionSubKeys.image_view_histogram: None,
                                          },
                    SessionKeys.instrument: {SessionSubKeys.distance_source_detector: None,
                                             SessionSubKeys.beam_index: 0,
                                             SessionSubKeys.detector_value: None,
                                             },
                    SessionKeys.material: {SessionSubKeys.selected_element: {SessionSubKeys.name: None,
                                                                             SessionSubKeys.user_defined: False,
                                                                             SessionSubKeys.index: 0},
                                           SessionSubKeys.lattice: None,
                                           Material.hkl_d0: None,
                                           SessionSubKeys.crystal_structure: {SessionSubKeys.name: 'fcc',
                                                                              SessionSubKeys.index: 0,
                                                                              },
                                           Material.user_defined_bragg_edge_list: None,
                                           },
                    SessionKeys.reduction: {SessionSubKeys.activate: True,
                                            SessionSubKeys.dimension: '2d',
                                            SessionSubKeys.size: {'flag': 'default',
                                                                  'y': 20,
                                                                  'x': 20,
                                                                  'l': 3,
                                                                  },
                                            SessionSubKeys.type: 'box',
                                            SessionSubKeys.process_order: 'option1',
                                            },
                    SessionKeys.bin: {SessionSubKeys.roi: None,
                                      SessionSubKeys.binning_line_view: {'pos': None,
                                                                         'adj': None,
                                                                         'line color': None,
                                                                         },
                                      SessionSubKeys.image_view_state: None,
                                      SessionSubKeys.image_view_histogram: None,
                                      SessionSubKeys.ui_accessed: False,
                                      },
                    DataType.fitting: {SessionSubKeys.lambda_range_index: None,
                                       SessionSubKeys.x_axis: None,
                                       SessionSubKeys.transparency: 50,
                                       SessionSubKeys.image_view_state: None,
                                       SessionSubKeys.image_view_histogram: None,
                                       SessionSubKeys.ui_accessed: False,
                                       SessionSubKeys.ui: {'splitter_2': None,
                                                           'splitter': None,
                                                           'splitter_3': None,
                                                           },
                                       SessionSubKeys.march_dollase: {MarchSessionSubKeys.table_dictionary: None,
                                                                      MarchSessionSubKeys.plot_active_row_flag: True,
                                                                      },
                                       SessionSubKeys.kropff: {KropffSessionSubKeys.table_dictionary: None,
                                                               KropffSessionSubKeys.high_tof: {
                                                                   KropffSessionSubKeys.a0: '1',
                                                                   KropffSessionSubKeys.b0: '1',
                                                                   KropffSessionSubKeys.graph: 'a0',
                                                                   },
                                                               KropffSessionSubKeys.low_tof: {
                                                                   KropffSessionSubKeys.ahkl: '1',
                                                                   KropffSessionSubKeys.bhkl: '1',
                                                                   KropffSessionSubKeys.graph: 'ahkl',
                                                                   },
                                                               KropffSessionSubKeys.bragg_peak: {
                                                                   KropffSessionSubKeys.lambda_hkl: '5e-8',
                                                                   KropffSessionSubKeys.tau: '1',
                                                                   KropffSessionSubKeys.sigma: '1e-7',
                                                                   KropffSessionSubKeys.table_selection: 'single',
                                                                   KropffSessionSubKeys.graph: 'lambda_hkl',
                                                                   },
                                                               KropffSessionSubKeys.automatic_bragg_peak_threshold_finder: True,
                                                               KropffSessionSubKeys.kropff_bragg_peak_good_fit_conditions:
                                                                   {KropffSessionSubKeys.l_hkl_error: {
                                                                       KropffSessionSubKeys.state: True,
                                                                       KropffSessionSubKeys.value: 0.01},
                                                                    KropffSessionSubKeys.t_error: {
                                                                        KropffSessionSubKeys.state: True,
                                                                        KropffSessionSubKeys.value: 0.01},
                                                                    KropffSessionSubKeys.sigma_error: {
                                                                        KropffSessionSubKeys.state: True,
                                                                        KropffSessionSubKeys.value: 0.01},
                                                                    },
                                                               KropffSessionSubKeys.kropff_lambda_settings: {
                                                                   KropffSessionSubKeys.state: 'fix',
                                                                   KropffSessionSubKeys.fix: 5e-8,
                                                                   KropffSessionSubKeys.range: [1e-8, 1e-7, 1e-8],
                                                                   },
                                                               KropffSessionSubKeys.bragg_peak_row_rejections_conditions: {
                                                                   KropffSessionSubKeys.l_hkl: {
                                                                       KropffSessionSubKeys.less_than: {
                                                                           KropffSessionSubKeys.state: True,
                                                                           KropffSessionSubKeys.value: 0,
                                                                           },
                                                                       KropffSessionSubKeys.more_than: {
                                                                           KropffSessionSubKeys.state: True,
                                                                           KropffSessionSubKeys.value: 10,
                                                                           },
                                                                       },
                                                                   },
                                                               },
                                       },
                    }

    default_session_dict = copy.deepcopy(session_dict)

    def __init__(self, parent=None):
        logging.info("-> Saving current session before leaving the application")
        self.parent = parent

    def save_from_ui(self):
        self.session_dict[SessionSubKeys.config_version] = self.parent.config[SessionSubKeys.config_version]
        self.session_dict[SessionSubKeys.log_buffer_size] = self.parent.session_dict[SessionSubKeys.log_buffer_size]

        # Load data tab
        o_save_load_data_tab = SaveLoadDataTab(parent=self.parent,
                                               session_dict=self.session_dict)
        o_save_load_data_tab.sample()
        o_save_load_data_tab.ob()
        o_save_load_data_tab.instrument()
        o_save_load_data_tab.material()
        self.session_dict = o_save_load_data_tab.session_dict

        # save normalization
        o_save_normalization = SaveNormalizationTab(parent=self.parent,
                                                    session_dict=self.session_dict)
        o_save_normalization.normalization()
        self.session_dict = o_save_normalization.session_dict

        # save normalized
        o_save_normalized = SaveNormalizedTab(parent=self.parent,
                                              session_dict=self.session_dict)
        o_save_normalized.normalized()
        self.session_dict = o_save_normalized.session_dict

        # save bin
        o_save_bin = SaveBinTab(parent=self.parent,
                                session_dict=self.session_dict)
        o_save_bin.bin()
        self.session_dict = o_save_bin.session_dict

        # save fitting
        o_save_fitting = SaveFittingTab(parent=self.parent,
                                        session_dict=self.session_dict)
        o_save_fitting.fitting()
        self.session_dict = o_save_fitting.session_dict

        self.parent.session_dict = self.session_dict

    def load_to_ui(self, tabs_to_load=None):
        if not self.load_successful:
            return

        logging.info(f"Automatic session tabs to load: {tabs_to_load}")

        try:

            o_general = General(parent=self.parent)
            o_general.settings()

            if DataType.sample in tabs_to_load:
                # load data tab
                o_load = LoadLoadDataTab(parent=self.parent)
                o_load.sample()
                o_load.ob()
                # o_load.instrument()
                # o_load.material()
                self.parent.load_data_tab_changed(tab_index=0)

                # load normalization tab
                o_norm = LoadNormalization(parent=self.parent)
                o_norm.roi()
                o_norm.check_widgets()
                o_norm.image_settings()

            o_load = LoadLoadDataTab(parent=self.parent)
            o_load.instrument()
            o_load.material()

            if DataType.normalized in tabs_to_load:
                # load normalized tab
                o_normalized = LoadNormalized(parent=self.parent)
                o_normalized.all()

            if DataType.bin in tabs_to_load:
                # load bin tab
                o_bin = LoadBin(parent=self.parent)
                o_bin.all()

            if DataType.fitting in tabs_to_load:
                # load fitting
                o_fit = LoadFitting(parent=self.parent)
                o_fit.table_dictionary()

            o_util = SessionUtilities(parent=self.parent)
            if tabs_to_load:
                o_util.jump_to_tab_of_data_type(tabs_to_load[-1])

            show_status_message(parent=self.parent,
                                message=f"Loaded {self.config_file_name}",
                                status=StatusMessageStatus.ready,
                                duration_s=10)

        except FileNotFoundError:
            show_status_message(parent=self.parent,
                                message=f"One of the data file could not be located. Aborted loading session!",
                                status=StatusMessageStatus.error,
                                duration_s=10)
            logging.info("Loading session aborted! FileNotFoundError raised!")
            self.parent.session_dict = SessionHandler.session_dict

        except ValueError:
            show_status_message(parent=self.parent,
                                message=f"One of the data file raised an error. Aborted loading session!",
                                status=StatusMessageStatus.error,
                                duration_s=10)
            logging.info("Loading session aborted! ValueError raised!")
            self.parent.session_dict = SessionHandler.session_dict

    def automatic_save(self):
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.get_automatic_config_file_name()
        self.save_to_file(config_file_name=full_config_file_name)

    def save_to_file(self, config_file_name=None):
        if config_file_name is None:
            config_file_name = QFileDialog.getSaveFileName(self.parent,
                                                           caption="Select session file name ...",
                                                           directory=self.parent.default_path[DataType.sample],
                                                           filter="session (*.json)",
                                                           initialFilter="session")

            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            output_file_name = config_file_name
            session_dict = self.parent.session_dict

            with open(output_file_name, 'w') as json_file:
                json.dump(session_dict, json_file)

            show_status_message(parent=self.parent,
                                message=f"Session saved in {config_file_name}",
                                status=StatusMessageStatus.ready,
                                duration_s=10)
            logging.info(f"Saving configuration into {config_file_name}")

    def load_from_file(self, config_file_name=None):
        self.parent.loading_from_config = True

        if config_file_name is None:
            config_file_name = QFileDialog.getOpenFileName(self.parent,
                                                           directory=self.parent.default_path[DataType.sample],
                                                           caption="Select session file ...",
                                                           filter="session (*.json)",
                                                           initialFilter="session")
            QApplication.processEvents()
            config_file_name = config_file_name[0]

        if config_file_name:
            config_file_name = config_file_name
            self.config_file_name = config_file_name
            show_status_message(parent=self.parent,
                                message=f"Loading {config_file_name} ...",
                                status=StatusMessageStatus.ready)

            with open(config_file_name, "r") as read_file:
                session_to_save = json.load(read_file)
                if session_to_save.get(SessionSubKeys.config_version, None) is None:
                    logging.info(f"Session file is out of date!")
                    logging.info(f"-> expected version: {self.parent.config[SessionSubKeys.config_version]}")
                    logging.info(f"-> session version: Unknown!")
                    self.load_successful = False
                elif session_to_save[SessionSubKeys.config_version] == self.parent.config[
                    SessionSubKeys.config_version]:
                    self.parent.session_dict = session_to_save
                    logging.info(f"Loaded from {config_file_name}")
                else:
                    logging.info(f"Session file is out of date!")
                    logging.info(f"-> expected version: {self.parent.config[SessionSubKeys.config_version]}")
                    logging.info(f"-> session version: {session_to_save[SessionSubKeys.config_version]}")
                    self.load_successful = False

                if not self.load_successful:
                    show_status_message(parent=self.parent,
                                        message=f"{config_file_name} not loaded! (check log for more information)",
                                        status=StatusMessageStatus.ready,
                                        duration_s=10)

        else:
            self.load_successful = False
            show_status_message(parent=self.parent,
                                message=f"{config_file_name} not loaded! (check log for more information)",
                                status=StatusMessageStatus.ready,
                                duration_s=10)

    def get_tabs_to_load(self):
        session_dict = self.parent.session_dict
        list_tabs_to_load = []
        if session_dict[DataType.sample][SessionSubKeys.list_files]:
            list_tabs_to_load.append(DataType.sample)
        if session_dict[DataType.normalized][SessionSubKeys.list_files]:
            list_tabs_to_load.append(DataType.normalized)
        if session_dict[DataType.bin][SessionSubKeys.ui_accessed]:
            list_tabs_to_load.append(DataType.bin)
        if session_dict[DataType.fitting][SessionSubKeys.ui_accessed]:
            list_tabs_to_load.append(DataType.fitting)

        return list_tabs_to_load
