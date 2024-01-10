import os


class EventHandler:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def check_widgets(self):
        folder_selected = self.parent.ui.folder_selected.text()
        if os.path.exists(folder_selected):
            Enabled_state = True
        else:
            Enabled_state = False

        self.parent.ui.bin_tabWidget.setEnabled(Enabled_state)
        self.parent.ui.x_axis_groupBox.setEnabled(Enabled_state)
        self.parent.ui.stats_tabWidget.setEnabled(Enabled_state)
        self.parent.ui.bin_bottom_tabWidget.setEnabled(Enabled_state)
        self.parent.ui.bin_settings_pushButton.setEnabled(Enabled_state)
        self.parent.ui.export_bin_table_pushButton.setEnabled(Enabled_state)
        self.parent.ui.export_pushButton.setEnabled(Enabled_state)
