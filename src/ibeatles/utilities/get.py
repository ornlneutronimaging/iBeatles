import os
from os.path import expanduser
from src.ibeatles.session import SessionKeys, SessionSubKeys


class Get:
    def __init__(self, parent=None):
        self.parent = parent

    def get_material(self):
        top_tab_index = self.parent.ui.material_top_tabWidget.currentIndex()
        if top_tab_index == 0:  # pre-defined
            return self.parent.ui.pre_defined_list_of_elements.currentText()
        else:  # custom
            return self.parent.ui.user_defined_element_name.text()

    def get_log_file_name(self):
        log_file_name = self.parent.config["log_file_name"]
        full_log_file_name = Get.get_full_home_file_name(log_file_name)
        return full_log_file_name

    def get_automatic_config_file_name(self):
        config_file_name = self.parent.config["session_file_name"]
        full_config_file_name = Get.get_full_home_file_name(config_file_name)
        return full_config_file_name

    @staticmethod
    def get_full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name

    def distance_source_detector(self) -> str:
        session_dict = self.parent.session_dict
        return str(
            session_dict[SessionKeys.instrument][
                SessionSubKeys.distance_source_detector
            ]
        )

    def detector_offset(self) -> str:
        session_dict = self.parent.session_dict
        return str(session_dict[SessionKeys.instrument][SessionSubKeys.detector_value])

    def bin_size(self):
        session_dict = self.parent.session_dict
        return session_dict[SessionKeys.bin][SessionSubKeys.roi][-1]

    # def auto_bins_currently_activated(self):
    #     auto_bin_mode = self.bin_auto_mode()
    #     if auto_bin_mode == BinAutoMode.linear:
    #         return self.parent.linear_bins
    #     elif auto_bin_mode == BinAutoMode.log:
    #         return self.parent.log_bins
    #     else:
    #         raise NotImplementedError("Auto bin mode not implemented!")
