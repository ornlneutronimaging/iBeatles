from qtpy.QtWidgets import QFileDialog, QApplication
import json
import logging

from ..utilities.status_message_config import StatusMessageStatus, show_status_message
from ..utilities.get import Get
from .save_load_data_tab import SaveLoadDataTab
from .save_normalization_tab import SaveNormalizationTab
from .save_normalized_tab import SaveNormalizedTab
from .save_bin_tab import SaveBinTab
from .load_load_data_tab import LoadLoadDataTab
from .load_normalization_tab import LoadNormalization
from .load_normalized_tab import LoadNormalized
from .load_bin_tab import LoadBin


from .. import DataType


class SessionHandler:

    config_file_name = ""
    load_successful = True

    session_dict = {'config version': None,
                    DataType.sample: {'list files': None,
                                      'current folder': None,
                                      'time spectra filename': None,
                                      'list files selected': None,
                                      'list rois': None,
                                      },
                    DataType.ob: {'list files'           : None,
                                  'current folder'       : None,
                                  'list files selected'  : None,
                                  },
                    DataType.normalization: {'roi': None,
                                             },
                    DataType.normalized: {'list files': None,
                                          'current folder': None,
                                          'time spectra filename': None,
                                          'list files selected': None,
                                          'list rois': None,
                                          },
                    "instrument": {'distance source detector': None,
                                   'beam index': 0,
                                   'detector value': None,
                                   },
                    "bin": {'roi': None,
                            'binning line view': {'pos': None,
                                                  'adj': None,
                                                  'pen': None,
                                                  },
                            },
                    }

    def __init__(self, parent=None):
        logging.info("-> Saving current session before leaving the application")
        self.parent = parent

    def save_from_ui(self):

        self.session_dict['config version'] = self.parent.config["config version"]

        # Load data tab
        o_save_load_data_tab = SaveLoadDataTab(parent=self.parent,
                                               session_dict=self.session_dict)
        o_save_load_data_tab.sample()
        o_save_load_data_tab.ob()
        o_save_load_data_tab.instrument()
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
        self.session_dict = o_save_normalized.session_dict

        self.parent.session_dict = self.session_dict

    def load_to_ui(self, tabs_to_load=None):

        if not self.load_successful:
            return

        logging.info(f"Automatic session tabs to load: {tabs_to_load}")

        if DataType.sample in tabs_to_load:

            # load data tab
            o_load = LoadLoadDataTab(parent=self.parent)
            o_load.sample()
            o_load.ob()
            o_load.instrument()

            # load normalization tab
            o_norm = LoadNormalization(parent=self.parent)
            o_norm.roi()
            o_norm.check_widgets()

        if DataType.normalized in tabs_to_load:

            # load normalized tab
            o_normalized = LoadNormalized(parent=self.parent)
            o_normalized.all()

        if DataType.bin in tabs_to_load:

            # load bin tab
            o_bin = LoadBin(parent=self.parent)
            o_bin.all()

        show_status_message(parent=self.parent,
                            message=f"Loaded {self.config_file_name}",
                            status=StatusMessageStatus.ready,
                            duration_s=10)

    def automatic_save(self):
        o_get = Get(parent=self.parent)
        full_config_file_name = o_get.get_automatic_config_file_name()
        self.save_to_file(config_file_name=full_config_file_name)

    def save_to_file(self, config_file_name=None):

        if config_file_name is None:
            config_file_name = QFileDialog.getSaveFileName(self.parent,
                                                           caption="Select session file name ...",
                                                           directory=self.parent.homepath,
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
                                                           directory=self.parent.homepath,
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
                if session_to_save.get("config version", None) is None:
                    logging.info(f"Session file is out of date!")
                    logging.info(f"-> expected version: {self.parent.config['config version']}")
                    logging.info(f"-> session version: Unknown!")
                    self.load_successful = False
                elif session_to_save["config version"] == self.parent.config["config version"]:
                    self.parent.session_dict = session_to_save
                    logging.info(f"Loaded from {config_file_name}")
                else:
                    logging.info(f"Session file is out of date!")
                    logging.info(f"-> expected version: {self.parent.config['config version']}")
                    logging.info(f"-> session version: {session_to_save['config version']}")
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
        if session_dict[DataType.sample]['list files']:
            list_tabs_to_load.append(DataType.sample)
        if session_dict[DataType.normalized]['list files']:
            list_tabs_to_load.append(DataType.normalized)
            list_tabs_to_load.append(DataType.bin)

        return list_tabs_to_load
