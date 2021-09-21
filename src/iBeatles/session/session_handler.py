from qtpy.QtWidgets import QFileDialog, QApplication
import json
import logging
import numpy as np

from ..utilities.status_message_config import StatusMessageStatus, show_status_message
from ..utilities.get import Get
from .save_load_data_tab import SaveLoadDataTab


class SessionHandler:

    config_file_name = ""
    load_successful = True

    session_dict = {'config version': None,
                    'sample': {'list files': None,
                               'current folder': None,
                               'time spectra filename': None,
                               'list files selected': None,
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
        self.session_dict = o_save_load_data_tab.session_dict

        # # import input tab data
        # list_ui = self.parent.list_ui
        #
        # def retrieve_infos_from_import_data(data_type=DataType.projections):
        #     folder = str(list_ui['select lineEdit'][data_type].text())
        #     return {'folder': folder}
        #
        # # projections, ob, df
        # session_dict[DataType.projections] = retrieve_infos_from_import_data(data_type=DataType.projections)
        # session_dict[DataType.ob] = retrieve_infos_from_import_data(data_type=DataType.ob)
        # session_dict[DataType.df] = retrieve_infos_from_import_data(data_type=DataType.df)
        #
        # # list of angles
        # if not (self.parent.input['list angles'] is None):
        #     session_dict['list angles'] = [str(angle) for angle in self.parent.input['list angles']]
        #
        # # output folder
        # session_dict[DataType.output] = {'folder': str(list_ui['select lineEdit'][DataType.output].text())}
        #
        # # crop tab
        # crop_state = self.parent.ui.cropping_checkBox.isChecked()
        # # crop_width = 2*self.parent.ui.crop_width_horizontalSlider.value()
        # crop_width = int(str(self.parent.ui.crop_width_label.text()))
        # try:
        #     crop_from_slice = self.parent.ui.crop_from_slice_spinBox.value()
        #     crop_to_slice = self.parent.ui.crop_to_slice_spinBox.value()
        # except ValueError:
        #     crop_from_slice = np.NaN
        #     crop_to_slice = np.NaN
        # file_index = self.parent.ui.crop_file_index_horizontalSlider.value()
        # crop_dict = {'state': crop_state,
        #              'width': crop_width,
        #              # 'width / 2': np.int(crop_width/2),
        #              'from slice': crop_from_slice,
        #              'to slice': crop_to_slice,
        #              'to slice - from slice': crop_to_slice - crop_from_slice + 1,
        #              'file index': file_index}
        # session_dict['crop'] = crop_dict
        #
        # # center of rotation
        # o_center = CenterOfRotation(parent=self.parent)
        # center_of_rotation_state = self.parent.ui.master_center_of_rotation_checkBox.isChecked()
        # image_0_file_index = self.parent.ui.center_of_rotation_0_degrees_comboBox.currentIndex()
        # image_180_file_index = self.parent.ui.center_of_rotation_180_degrees_comboBox.currentIndex()
        # algorithm_selected = o_center.get_algorithm_selected()
        # user_value = self.parent.ui.center_of_rotation_user_defined_doubleSpinBox.value()
        # center_of_rotation_value = o_center.get_center_of_rotation()
        # center_rotation_dict = {'state': center_of_rotation_state,
        #                         'image 0 file index': image_0_file_index,
        #                         'image 180 file index': image_180_file_index,
        #                         'algorithm selected': algorithm_selected,
        #                         'center of rotation value': center_of_rotation_value,
        #                         'user value': user_value}
        # session_dict['center rotation'] = center_rotation_dict
        #
        # # tilt correction
        # o_tilt = TiltHandler(parent=self.parent)
        # tilt_correction_state = self.parent.ui.tilt_correction_checkBox.isChecked()
        # tilt_correction_file_index = self.parent.ui.tilt_correction_file_index_horizontalSlider.value()
        # index_of_180_degree_image = self.parent.tilt_correction_index_dict['180_degree']
        # index_of_0_degree_image = self.parent.tilt_correction_index_dict['0_degree']
        # tilt_algorithm = o_tilt.get_algorithm_selected()
        # tilt_calculation = self.parent.tilt_calculation
        # tilt_value_to_use_in_reconstruction = o_tilt.get_tilt_value_to_use_in_reconstruction()
        # use_tilt_value = self.parent.ui.show_tilt_checkBox.isChecked()
        # tilt_dict = {'state': tilt_correction_state,
        #              'file index': tilt_correction_file_index,
        #              'algorithm selected': tilt_algorithm,
        #              'image 0 file index': index_of_0_degree_image,
        #              'image 180 file index': index_of_180_degree_image,
        #              TiltAlgorithm.phase_correlation: tilt_calculation[TiltAlgorithm.phase_correlation],
        #              TiltAlgorithm.direct_minimization: tilt_calculation[TiltAlgorithm.direct_minimization],
        #              TiltAlgorithm.use_center: tilt_calculation[TiltAlgorithm.use_center],
        #              'tilt value to use in reconstruction': tilt_value_to_use_in_reconstruction,
        #              'use title value': use_tilt_value}
        # session_dict['tilt'] = tilt_dict
        #
        # # general parameters
        # diffuseness = self.parent.ui.diffuseness_doubleSpinBox.value()
        # smoothness = self.parent.ui.smoothness_doubleSpinBox.value()
        # sigma = self.parent.ui.sigma_doubleSpinBox.value()
        # o_advanced_parameters = GeneralSettingsHandler(parent=self.parent)
        # reconstruction_algorithm = o_advanced_parameters.get_reconstruction_algorithm_selected()
        # image_width = self.parent.image_size['width']
        # sub_sampling_factor = self.parent.ui.sub_sampling_spinBox.value()
        # session_dict['general parameters'] = {'diffuseness': diffuseness,
        #                                       'smoothness': smoothness,
        #                                       'sigma': sigma,
        #                                       'sigma / smoothness': sigma / smoothness,
        #                                       'reconstruction algorithm': reconstruction_algorithm,
        #                                       'image width': image_width,
        #                                       'sub sampling factor': sub_sampling_factor}
        #
        # # advanced parameters
        # advanced_session_dict = self.parent.session_dict.get("advanced settings", None)
        # if advanced_session_dict is None:
        #     o_advanced = AdvancedSettingsInitialization(parent=self.parent)
        #     o_advanced.from_config_to_session_dict()
        # else:
        #     session_dict['advanced settings'] = advanced_session_dict
        #
        self.parent.session_dict = self.session_dict

    def load_to_ui(self):

        if not self.load_successful:
            return

        session_dict = self.parent.session_dict





        # list_ui = self.parent.list_ui
        #
        # list_load_method = {DataType.projections: self.parent.projections_text_field_returned,
        #                     DataType.ob: self.parent.ob_text_field_returned,
        #                     DataType.df: self.parent.df_text_field_returned,
        #                     DataType.output: self.parent.output_folder_text_field_returned}
        #
        # # input tab
        # for data_type in list_load_method.keys():
        #     _session = session_dict[data_type]
        #     folder = _session['folder']
        #     list_ui['select lineEdit'][data_type].setText(folder)
        #     list_load_method[data_type]()
        #
        # if not (self.parent.input['data'][DataType.projections] is None):
        #
        #     # crop
        #     o_crop = CropHandler(parent=self.parent)
        #     o_crop.initialize_crop()
        #     self.parent.ui.crop_file_index_horizontalSlider.setValue(self.parent.session_dict['crop']['file index'])
        #     crop_width = self.parent.session_dict['crop']['width']
        #     from_slice = self.parent.session_dict['crop']['from slice']
        #     to_slice = self.parent.session_dict['crop']['to slice']
        #
        #     self.parent.ui.crop_to_slice_spinBox.blockSignals(True)
        #     self.parent.ui.crop_from_slice_spinBox.blockSignals(True)
        #     self.parent.ui.crop_from_slice_spinBox.setValue(from_slice)
        #     self.parent.ui.crop_to_slice_spinBox.setValue(to_slice)
        #     self.parent.ui.crop_to_slice_spinBox.blockSignals(False)
        #     self.parent.ui.crop_from_slice_spinBox.blockSignals(False)
        #
        #     self.parent.ui.crop_width_horizontalSlider.setValue(crop_width/2)
        #     self.parent.ui.crop_width_horizontalSlider.setMinimum(10)
        #     o_crop.width_changed()
        #     o_crop.file_index_changed()
        #     o_crop.crop_slice_spinBox_changed(widget='all')
        #
        #     # center of rotation
        #     o_center = CenterOfRotation(parent=self.parent)
        #     o_center.initialize_from_session()
        #
        #     # tilt
        #     o_tilt = TiltHandler(parent=self.parent)
        #     o_tilt.initialize_tilt_from_session()
        #
        #     # general parameters
        #     o_advanced = GeneralSettingsHandler(parent=self.parent)
        #     o_advanced.initialization_from_session()

        show_status_message(parent=self.parent,
                            message=f"Loaded {self.config_file_name}",
                            status=StatusMessageStatus.ready,
                            duration_s=10)

    # def _retrieve_general_settings(self):
    #     number_of_scanned_periods = self.parent.ui.number_of_scanned_periods_spinBox.value()
    #     full_period_true = self.parent.ui.full_period_true_radioButton.isChecked()
    #     rotation_of_g0rz = self.parent.ui.rotation_of_g0rz_doubleSpinBox.value()
    #     images_per_step = self.parent.ui.images_per_step_spinBox.value()
    #     general_settings = {'number of scanned periods': number_of_scanned_periods,
    #                         'full period': full_period_true,
    #                         'rotation of g0rz': rotation_of_g0rz,
    #                         'number of images per step': images_per_step}
    #     return general_settings

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
