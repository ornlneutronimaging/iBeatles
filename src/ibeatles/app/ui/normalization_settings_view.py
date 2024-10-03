#!/usr/bin/env python
"""View for the normalization settings."""

from qtpy.QtWidgets import QDialog
from ibeatles.app.utils.ui_loader import load_ui
from qtpy.QtCore import Signal


class NormalizationSettingsView(QDialog):
    """
    View class for the normalization settings dialog.

    This class represents the GUI for normalization settings, allowing users to
    configure moving average parameters, processing order, and sample backgrounds.
    """

    settings_changed = Signal()

    default_kernel_size = {"x": 3, "y": 3, "l": 3}
    default_kernel_size_label = {
        "3d": "y:{}  x:{}  λ:{}".format(
            default_kernel_size["y"], default_kernel_size["x"], default_kernel_size["l"]
        ),
        "2d": f"y:{default_kernel_size['y']}  x:{default_kernel_size['x']}",
    }

    def __init__(self, parent=None):
        """
        Initialize the NormalizationSettingsView.

        Parameters
        ----------
        parent : QWidget, optional
            The parent widget.
        """
        super().__init__(parent)
        self.ui = load_ui("normalization_settings_view.ui", baseinstance=self)
        self.setWindowTitle("Normalization Settings")

    def ok_clicked(self):
        """Handle the OK button click."""
        self.settings_changed.emit()
        self.accept()

    def activate_moving_average_clicked(self):
        """Handle activation/deactivation of moving average."""
        state = self.ui.activate_moving_average_checkBox.isChecked()
        self.ui.dimension_groupBox.setEnabled(state)
        self.ui.size_groupBox.setEnabled(state)
        self.ui.type_groupBox.setEnabled(state)
        self.ui.processing_order_groupBox.setEnabled(state)
        self.settings_changed.emit()

    def dimension_radio_button_clicked(self):
        """Handle changes in kernel dimension selection."""
        is_3d_clicked = self.ui.kernel_dimension_3d_radioButton.isChecked()
        kernel_size = "3d" if is_3d_clicked else "2d"
        self.ui.kernel_size_default_label.setText(
            self.default_kernel_size_label[kernel_size]
        )
        self.ui.kernel_size_custom_lambda_label.setVisible(is_3d_clicked)
        self.ui.kernel_size_custom_lambda_spinBox.setVisible(is_3d_clicked)
        self.settings_changed.emit()

    def size_radio_button_clicked(self):
        """Handle changes in kernel size selection."""
        is_default_clicked = self.ui.kernel_size_default_radioButton.isChecked()
        self.ui.kernel_size_default_label.setEnabled(is_default_clicked)
        self.ui.kernel_size_custom_y_label.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_y_spinBox.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_x_label.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_x_spinBox.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_lambda_label.setEnabled(not is_default_clicked)
        self.ui.kernel_size_custom_lambda_spinBox.setEnabled(not is_default_clicked)
        self.settings_changed.emit()

    def get_settings(self):
        """
        Get the current settings from the UI.

        Returns
        -------
        dict
            A dictionary containing the current settings.
        """
        return {
            "activate": self.ui.activate_moving_average_checkBox.isChecked(),
            "dimension": "3d"
            if self.ui.kernel_dimension_3d_radioButton.isChecked()
            else "2d",
            "size": {
                "flag": "default"
                if self.ui.kernel_size_default_radioButton.isChecked()
                else "custom",
                "y": self.ui.kernel_size_custom_y_spinBox.value(),
                "x": self.ui.kernel_size_custom_x_spinBox.value(),
                "l": self.ui.kernel_size_custom_lambda_spinBox.value(),
            },
            "type": "gaussian"
            if self.ui.kernel_type_gaussian_radioButton.isChecked()
            else "box",
            "process order": "option1"
            if self.ui.processes_order_option1_radio_button.isChecked()
            else "option2",
        }

    def set_settings(self, settings):
        """
        Set the UI elements based on the provided settings.

        Parameters
        ----------
        settings : dict
            A dictionary containing the settings to apply.
        """
        self.ui.activate_moving_average_checkBox.setChecked(settings["activate"])
        self.ui.kernel_dimension_3d_radioButton.setChecked(
            settings["dimension"] == "3d"
        )
        self.ui.kernel_dimension_2d_radioButton.setChecked(
            settings["dimension"] == "2d"
        )
        self.ui.kernel_size_default_radioButton.setChecked(
            settings["size"]["flag"] == "default"
        )
        self.ui.kernel_size_custom_radioButton.setChecked(
            settings["size"]["flag"] == "custom"
        )
        self.ui.kernel_size_custom_y_spinBox.setValue(settings["size"]["y"])
        self.ui.kernel_size_custom_x_spinBox.setValue(settings["size"]["x"])
        self.ui.kernel_size_custom_lambda_spinBox.setValue(settings["size"]["l"])
        self.ui.kernel_type_gaussian_radioButton.setChecked(
            settings["type"] == "gaussian"
        )
        self.ui.kernel_type_box_radioButton.setChecked(settings["type"] == "box")
        self.ui.processes_order_option1_radio_button.setChecked(
            settings["process order"] == "option1"
        )
        self.ui.processes_order_option2_radio_button.setChecked(
            settings["process order"] == "option2"
        )

        self.activate_moving_average_clicked()
        self.dimension_radio_button_clicked()
        self.size_radio_button_clicked()
