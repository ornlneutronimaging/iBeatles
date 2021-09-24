from qtpy.QtWidgets import QFileDialog, QApplication
import json
import logging
import numpy as np
import os

from .. import DataType
from ..utilities.status_message_config import StatusMessageStatus, show_status_message
from ..utilities.get import Get
from .save_load_data_tab import SaveLoadDataTab
from .save_normalization_tab import SaveNormalizationTab
from ..step1.data_handler import DataHandler
from ..step1.gui_handler import Step1GuiHandler
from ..utilities.gui_handler import GuiHandler
from ..step2.plot import Step2Plot
from .load_load_data_tab import LoadLoadDataTab


class SessionHandler:

    config_file_name = ""
    load_successful = True

    session_dict = {'config version': None,
                    'sample': {'list files': None,
                               'current folder': None,
                               'time spectra filename': None,
                               'list files selected': None,
                               'list rois': None,
                               },
                    'ob': {'list files'           : None,
                               'current folder'       : None,
                               'list files selected'  : None,
                          },
                    'normalization': {'roi': None,
                                      },
                    "instrument": {'distance source detector': None,
                                   'beam index': 0,
                                   'detector value': None},
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

        o_save_normalization = SaveNormalizationTab(parent=self.parent,
                                                    session_dict=self.session_dict)
        o_save_normalization.normalization()
        self.session_dict = o_save_normalization.session_dict

        self.parent.session_dict = self.session_dict

    def load_to_ui(self):

        if not self.load_successful:
            return

        session_dict = self.parent.session_dict

        # load data tab
        o_load = LoadLoadDataTab(parent=self.parent)
        o_load.sample()
        o_load.ob()
        o_load.instrument()

        # # sample
        # list_sample_files = session_dict[DataType.sample]['list files']
        # if list_sample_files:
        #     input_folder = session_dict[DataType.sample]['current folder']
        #     o_data_handler = DataHandler(parent=self.parent,
        #                                  data_type=DataType.sample)
        #     list_sample_files_fullname = [os.path.join(input_folder, _file) for _file in list_sample_files]
        #     o_data_handler.load_files(list_of_files=list_sample_files_fullname)
        #     time_spectra_file = session_dict[DataType.sample]['time spectra filename']
        #     o_data_handler.load_time_spectra(time_spectra_file=time_spectra_file)
        #     list_files_selected = session_dict[DataType.sample]['list files selected']
        #     self.parent.list_roi[DataType.sample] = session_dict[DataType.sample]['list rois']
        #     o_gui = Step1GuiHandler(parent=self.parent, data_type=DataType.sample)
        #     o_gui.initialize_rois_and_labels()
        #     for _row_selected in list_files_selected:
        #         _item = self.parent.ui.list_sample.item(_row_selected)
        #         _item.setSelected(True)
        #     o_gui.check_time_spectra_widgets()
        #     o_gui.check_step1_widgets()
        #     self.parent.check_files_error()
        #     self.parent.retrieve_general_infos(data_type=DataType.sample)
        #     self.parent.retrieve_selected_row_infos(data_type=DataType.sample)
        #
        #     o_step2_plot = Step2Plot(parent=self.parent)
        #     o_step2_plot.prepare_data()
        #     o_step2_plot.init_roi_table()

        # # ob
        # list_ob_files = session_dict[DataType.ob]['list files']
        # if list_ob_files:
        #     input_folder = session_dict[DataType.ob]['current folder']
        #     o_data_handler = DataHandler(parent=self.parent,
        #                                  data_type=DataType.ob)
        #     list_ob_files_fullname = [os.path.join(input_folder, _file) for _file in list_ob_files]
        #     o_data_handler.load_files(list_of_files=list_ob_files_fullname)
        # list_files_selected = session_dict[DataType.ob]['list files selected']
        # self.parent.list_roi[DataType.ob] = session_dict[DataType.ob]['list rois']
        # o_gui = Step1GuiHandler(parent=self.parent, data_type=DataType.ob)
        # o_gui.initialize_rois_and_labels()
        # for _row_selected in list_files_selected:
        #     _item = self.parent.ui.list_open_beam.item(_row_selected)
        #     _item.setSelected(True)

        # # instrument
        # o_gui = GuiHandler(parent=self.parent)
        # list_ui = {'distance': self.parent.ui.distance_source_detector,
        #            'beam': self.parent.ui.beam_rate,
        #            'detector': self.parent.ui.detector_offset}
        #
        # for _key in list_ui.keys():
        #     list_ui[_key].blockSignals(True)
        #
        # o_gui.set_index_selected(index=session_dict["instrument"]["beam index"], ui=list_ui['beam'])
        # o_gui.set_text(value=session_dict["instrument"]["distance source detector"], ui=list_ui['distance'])
        #
        # for _key in list_ui.keys():
        #     list_ui[_key].blockSignals(False)
        #
        # o_gui.set_text(value=session_dict["instrument"]["detector value"], ui=list_ui['detector'])

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
