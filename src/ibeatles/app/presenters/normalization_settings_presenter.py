#!/usr/bin/env python
"""Presenter for the normalization settings view."""

import logging
from typing import Dict, Any
from ibeatles.core.config import NormalizationConfig
from ibeatles.app.models.normalization_settings_model import NormalizationSettingsModel
from ibeatles.app.ui.normalization_settings_view import NormalizationSettingsView


class NormalizationSettingsPresenter:
    """
    Presenter for the normalization settings.

    This class acts as an intermediary between the NormalizationSettingsModel
    and NormalizationSettingsView, handling user interactions and updating
    the model and view accordingly.

    Parameters
    ----------
    parent : QWidget, optional
        The parent widget for the view.

    Attributes
    ----------
    parent : QWidget
        The parent widget for the view.
    model : NormalizationSettingsModel
        The model containing the normalization settings data.
    view : NormalizationSettingsView
        The view displaying the normalization settings UI.
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.model = NormalizationSettingsModel()
        self.view = NormalizationSettingsView(parent)
        self.connect_signals()

    def connect_signals(self):
        """Connect view signals to their respective slots."""
        self.view.settings_changed.connect(self.update_model_from_view)

    def load_settings(
        self, config: NormalizationConfig = None, old_config: Dict[str, Any] = None
    ):
        """
        Load settings into the model and update the view.

        Parameters
        ----------
        config : NormalizationConfig, optional
            The new configuration to load.
        old_config : Dict[str, Any], optional
            The old configuration format to load.

        Raises
        ------
        ValueError
            If neither config nor old_config is provided.
        """
        if config:
            self.model.update_from_config(config)
        elif old_config:
            self.model.update_from_old_config(old_config)
        else:
            raise ValueError("Either config or old_config must be provided")

        self.update_view_from_model()

    def update_view_from_model(self):
        """Update the view with the current model state."""
        config = self.model.get_config()
        self.view.set_settings(config)

    def update_model_from_view(self):
        """Update the model with the current view state."""
        view_config = self.view.get_settings()
        self.model.update_from_config(view_config)

    def get_config(self) -> NormalizationConfig:
        """
        Get the current configuration from the model.

        Returns
        -------
        NormalizationConfig
            The current normalization configuration.
        """
        self.update_model_from_view()
        return self.model.get_config()

    def get_old_config(self) -> Dict[str, Any]:
        """
        Get the current configuration in the old format.

        Returns
        -------
        Dict[str, Any]
            The current configuration in the old dictionary format.
        """
        self.update_model_from_view()
        return self.model.get_old_config()

    def show_view(self):
        """Display the normalization settings view."""
        if self.view.exec_() == self.view.Accepted:
            self.update_model_from_view()
            if self.parent and hasattr(self.parent, "session_dict"):
                self.parent.session_dict["reduction"] = self.model.get_old_config()
            # logging
            logging.debug("Settings accepted. Current NormalizationConfig:")
            logging.debug(self.model.config.model_dump_json(indent=2))
