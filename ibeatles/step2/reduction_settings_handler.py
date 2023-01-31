from qtpy.QtWidgets import QDialog
import os

from .. import load_ui


class ReductionSettingsHandler(QDialog):

    default_kernel_size = {'x': 3,
                           'y': 3,
                           'l': 3}
    default_kernel_size_label = {'3d': u"y:{}  x:{}  \u03BB:{}".format(default_kernel_size['y'],
                                                                       default_kernel_size['x'],
                                                                       default_kernel_size['l']),
                                 '2d': f"y:{default_kernel_size['y']}  x:{default_kernel_size['x']}"}

    def __init__(self, parent=None):
        self.parent = parent
        QDialog.__init__(self, parent=parent)
        ui_full_path = os.path.join(os.path.dirname(__file__),
                                    os.path.join('ui',
                                                 'ui_reduction_settings.ui'))
        self.ui = load_ui(ui_full_path, baseinstance=self)
        self.setWindowTitle("Load previous session?")
        self.ui.pushButton.setFocus(True)
        self.initialization()

    def initialization(self):
        reduction_dict = self.parent.session_dict["reduction"]
        self.ui.activate_moving_average_checkBox.setChecked(reduction_dict["activate"])
        self.activate_moving_average_clicked()
        if reduction_dict["dimension"] == "3d":
            self.ui.kernel_dimension_3d_radioButton.setChecked(True)
        if reduction_dict["size"]["flag"] == "custom":
            self.ui.kernel_size_custom_radioButton.setChecked(True)
        self.ui.kernel_size_custom_y_spinBox.setValue(int(reduction_dict["size"]["y"]))
        self.ui.kernel_size_custom_x_spinBox.setValue(int(reduction_dict["size"]["x"]))
        self.ui.kernel_size_custom_lambda_spinBox.setValue(int(reduction_dict["size"]["l"]))
        self.size_radio_button_clicked()
        if reduction_dict["type"] == "gaussian":
            self.ui.kernel_type_gaussian_radioButton.setChecked(True)
        if reduction_dict["processes order"] == 'option1':
            self.ui.processes_order_option1_radio_button.setChecked(True)
        else:
            self.ui.processes_order_option2_radio_button.setChecked(True)

    def activate_moving_average_clicked(self):
        state = self.ui.activate_moving_average_checkBox.isChecked()
        self.ui.dimension_groupBox.setEnabled(state)
        self.ui.size_groupBox.setEnabled(state)
        self.ui.type_groupBox.setEnabled(state)
        self.ui.processing_order_groupBox.setEnabled(state)

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
        self.ui.kernel_size_custom_y_spinBox.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_x_label.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_x_spinBox.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_lambda_label.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_lambda_spinBox.setEnabled(not is_default_clicked)

    def ok_clicked(self):
        reduction_dict = self.parent.session_dict["reduction"]
        reduction_dict["activate"] = self.ui.activate_moving_average_checkBox.isChecked()
        reduction_dict["dimension"] = "2d" if self.ui.kernel_dimension_2d_radioButton.isChecked() else "3d"
        reduction_dict["size"]["flag"] = "default" if self.ui.kernel_size_default_radioButton.isChecked() else "custom"
        reduction_dict["size"]["y"] = self.ui.kernel_size_custom_y_spinBox.value()
        reduction_dict["size"]["x"] = self.ui.kernel_size_custom_x_spinBox.text()
        reduction_dict["size"]["l"] = self.ui.kernel_size_custom_lambda_spinBox.text()
        reduction_dict["type"] = "box" if self.ui.kernel_type_box_radioButton.isChecked() else "gaussian"
        reduction_dict["processes order"] = 'option1' if self.ui.processes_order_option1_radio_button.isChecked() \
            else 'option2'

        self.parent.session_dict["reduction"] = reduction_dict

        self.close()
