#!/usr/bin/env python
"""View for the normalization settings."""

from qtpy.QtWidgets import QDialog
from ibeatles.app.utils.ui_loader import load_ui
from ibeatles.core.config import (
    NormalizationConfig,
    ProcessOrder,
    KernelType,
    KernelSize,
    MovingAverage,
)
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

    def get_settings(self) -> NormalizationConfig:
        """
        Get the current settings from the UI.

        Returns
        -------
        NormalizationConfig
            A NormalizationConfig object containing the current settings.
        """
        is_3d = self.ui.kernel_dimension_3d_radioButton.isChecked()
        size = {
            "y": self.ui.kernel_size_custom_y_spinBox.value(),
            "x": self.ui.kernel_size_custom_x_spinBox.value(),
        }
        if is_3d:
            size["lambda"] = self.ui.kernel_size_custom_lambda_spinBox.value()

        return NormalizationConfig(
            moving_average=MovingAverage(
                active=self.ui.activate_moving_average_checkBox.isChecked(),
                dimension="3D" if is_3d else "2D",
                size=size,
                type=KernelType.gaussian
                if self.ui.kernel_type_gaussian_radioButton.isChecked()
                else KernelType.box,
            ),
            processing_order=ProcessOrder.moving_average_normalization
            if self.ui.processes_order_option1_radio_button.isChecked()
            else ProcessOrder.normalization_moving_average,
        )

    def set_settings(self, config: NormalizationConfig):
        """
        Set the UI elements based on the provided settings.

        Parameters
        ----------
        config : NormalizationConfig
            A NormalizationConfig object containing the settings to apply.
        """
        # Moving Average activation
        self.ui.activate_moving_average_checkBox.setChecked(
            config.moving_average.active
        )

        # Dimension
        is_3d = config.moving_average.dimension == "3D"
        self.ui.kernel_dimension_3d_radioButton.setChecked(is_3d)
        self.ui.kernel_dimension_2d_radioButton.setChecked(not is_3d)

        # Kernel Size
        default_size = KernelSize()
        is_default_size = (
            config.moving_average.size.y == default_size.y
            and config.moving_average.size.x == default_size.x
            and (
                config.moving_average.dimension == "2D"
                or config.moving_average.size.lambda_ == default_size.lambda_
            )
        )

        self.ui.kernel_size_default_radioButton.setChecked(is_default_size)
        self.ui.kernel_size_custom_radioButton.setChecked(not is_default_size)

        self.ui.kernel_size_custom_y_spinBox.setValue(config.moving_average.size.y)
        self.ui.kernel_size_custom_x_spinBox.setValue(config.moving_average.size.x)
        if is_3d:
            self.ui.kernel_size_custom_lambda_spinBox.setValue(
                config.moving_average.size.lambda_
            )

        # Kernel Type
        is_gaussian = config.moving_average.type == KernelType.gaussian
        self.ui.kernel_type_gaussian_radioButton.setChecked(is_gaussian)
        self.ui.kernel_type_box_radioButton.setChecked(not is_gaussian)

        # Processing Order
        is_ma_first = (
            config.processing_order == ProcessOrder.moving_average_normalization
        )
        self.ui.processes_order_option1_radio_button.setChecked(is_ma_first)
        self.ui.processes_order_option2_radio_button.setChecked(not is_ma_first)

        # Update UI state
        self.activate_moving_average_clicked()
        self.dimension_radio_button_clicked()
        self.size_radio_button_clicked()
