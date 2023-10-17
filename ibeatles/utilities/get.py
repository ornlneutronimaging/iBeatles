import os
from os.path import expanduser


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
        log_file_name = self.parent.config['log_file_name']
        full_log_file_name = Get.get_full_home_file_name(log_file_name)
        return full_log_file_name

    def get_automatic_config_file_name(self):
        config_file_name = self.parent.config['session_file_name']
        full_config_file_name = Get.get_full_home_file_name(config_file_name)
        return full_config_file_name

    @staticmethod
    def get_full_home_file_name(base_file_name):
        home_folder = expanduser("~")
        full_log_file_name = os.path.join(home_folder, base_file_name)
        return full_log_file_name

