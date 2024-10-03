#!/usr/bin/env python
"""Model for Normalization Settings"""

import logging
from typing import Dict, Any
from ibeatles.core.config import (
    NormalizationConfig,
    KernelType,
    SampleBackground,
    ProcessOrder,
)


class NormalizationSettingsModel:
    """
    Model class for handling normalization settings.

    This class manages the configuration for normalization settings, including
    moving average parameters and sample background. It provides methods to
    update settings, convert between new and old configuration formats, and
    modify individual settings.
    """

    def __init__(self):
        """Initialize the NormalizationSettingsModel with default configuration."""
        self.config = NormalizationConfig()
        self._old_config: Dict[str, Any] = {}

    def update_from_config(self, config: NormalizationConfig):
        """
        Update the model's configuration from a NormalizationConfig object.

        Parameters
        ----------
        config : NormalizationConfig
            The configuration object to update from.
        """
        self.config = config

    def update_from_old_config(self, old_config: Dict[str, Any]):
        """
        Update the model's configuration from the old dictionary-based format.

        Parameters
        ----------
        old_config: Dict[str, Any]
            The old configuration dictionary.
        """
        self._old_config = old_config
        logging.debug(
            "Deprecation warning: Using old configuration method. This will be removed in a future version."
        )

        # Convert old config to new config
        self.config.moving_average.active = old_config.get("activate", True)
        self.config.moving_average.dimension = (
            "3D" if old_config.get("dimension") == "3d" else "2D"
        )
        self.config.moving_average.size = {
            "y": old_config["size"].get("y", 3),
            "x": old_config["size"].get("x", 3),
        }
        if old_config.get("dimension") == "3d":
            self.config.moving_average.size["lambda"] = old_config["size"].get("l", 3)
        self.config.moving_average.type = (
            KernelType.gaussian
            if old_config.get("type") == "gaussian"
            else KernelType.box
        )
        self.config.processing_order = (
            ProcessOrder.moving_average_normalization
            if old_config.get("process_order") == "option1"
            else ProcessOrder.normalization_moving_average
        )

    def get_old_config(self) -> Dict[str, Any]:
        """
        Convert the current configuration to the old dictionary-based format.

        Returns
        -------
        Dict[str, Any]
            The configuration in the old format.
        """
        old_config = {
            "activate": self.config.moving_average.active,
            "dimension": "3d" if self.config.moving_average.dimension == "3D" else "2d",
            "size": {
                "flag": "custom",
                "y": self.config.moving_average.size["y"],
                "x": self.config.moving_average.size["x"],
                "l": self.config.moving_average.size.get("lambda", 3),
            },
            "type": "gaussian"
            if self.config.moving_average.type == KernelType.gaussian
            else "box",
            "process_order": "option1"
            if self.config.processing_order == ProcessOrder.moving_average_normalization
            else "option2",
        }
        return old_config

    def set_moving_average_active(self, active: bool):
        """
        Set the active state of moving average.

        Parameters
        ----------
        active: bool
            True to activate moving average, False to deactivate.
        """
        self.config.moving_average.active = active

    def set_dimension(self, dimension: str):
        """
        Set the dimension for moving average.

        Parameters
        ----------
        dimension: str
            The dimension, either "2D" or "3D".
        """
        self.config.moving_average.dimension = dimension
        if dimension == "2D" and "lambda" in self.config.moving_average.size:
            del self.config.moving_average.size["lambda"]
        elif dimension == "3D" and "lambda" not in self.config.moving_average.size:
            self.config.moving_average.size["lambda"] = 3

    def set_kernel_size(self, size: Dict[str, int]):
        """
        Set the kernel size for moving average.

        Parameters
        ----------
        size: Dict[str, int]
            A dictionary with 'y', 'x', and 'lambda' keys.
        """
        self.config.moving_average.size = size

    def set_kernel_type(self, kernel_type: KernelType):
        """
        Set the kernel type for moving average.

        Parameters
        ----------
        kernel_type: KernelType
            The type of kernel to use.
        """
        self.config.moving_average.type = kernel_type

    def set_processing_order(self, order: ProcessOrder):
        """
        Set the processing order.

        Parameters
        ----------
        order: ProcessOrder
            The order of processing steps.
        """
        self.config.processing_order = order

    def add_sample_background(self, background: SampleBackground):
        """
        Add a sample background to the configuration.

        Parameters
        ----------
        background: SampleBackground
            The sample background to add.
        """
        if self.config.sample_background is None:
            self.config.sample_background = []
        self.config.sample_background.append(background)

    def remove_sample_background(self, index: int):
        """
        Remove a sample background from the configuration.

        Parameters
        ----------
        index: int
            The index of the sample background to remove.
        """
        if self.config.sample_background and 0 <= index < len(
            self.config.sample_background
        ):
            del self.config.sample_background[index]

    def update_sample_background(self, index: int, background: SampleBackground):
        """
        Update a sample background in the configuration.

        Parameters
        ----------
        index: int
            The index of the sample background to update.
        background: SampleBackground
            The new sample background data.
        """
        if self.config.sample_background and 0 <= index < len(
            self.config.sample_background
        ):
            self.config.sample_background[index] = background

    def get_config(self) -> NormalizationConfig:
        """
        Get the current configuration.

        Returns
        -------
        NormalizationConfig
            The current normalization configuration.
        """
        return self.config
