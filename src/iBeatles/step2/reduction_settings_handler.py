from qtpy.QtWidgets import QDialog
import os

from .. import load_ui


class ReductionSettingsHandler(QDialog):

    default_kernel_size_label = {'3d': u"y:3  x:3  \u03BB:3",
                                 '2d': "y:3  x:3"}

    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'moving_average_settings.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Load previous session?")
        self.ui.pushButton.setFocus(True)

    def activate_moving_average_clicked(self):
        state = self.ui.activate_moving_average_checkBox.isChecked()
        self.ui.dimension_groupBox.setEnabled(state)
        self.ui.size_groupBox.setEnabled(state)
        self.ui.type.setEnabled(state)

    def dimension_radio_button_clicked(self):
        is_3d_clicked = self.ui.kernel_dimension_3d_radioButton.isChecked()
        if is_3d_clicked:
            kernel_size = '3d'
        else:
            kernel_size = '2d'
        self.ui.kernel_size_default_label.setText(self.default_kernel_size_label[kernel_size])
        self.ui.kernel_size_custom_lambda_label.setVisible(is_3d_clicked)
        self.ui.kernel_size_custom_lambda_lineEdit.setVisible(is_3d_clicked)

    def size_radio_button_clicked(self):
        is_default_clicked = self.ui.kernel_size_default_radioButton.isChecked()
        self.ui.kernel_size_default_label.setEnabled(is_default_clicked)
        self.ui.kernel_size_custom_y_label.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_y_lineEdit.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_x_label.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_x_lineEdit.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_lambda_label.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_lambda_lineEdit.setEnabled(not is_default_clicked)

    def ok_clicked(self):
        self.close()
