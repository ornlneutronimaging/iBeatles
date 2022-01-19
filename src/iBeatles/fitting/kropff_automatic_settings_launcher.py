from qtpy.QtWidgets import QDialog
import logging

from .. import load_ui
from . import KropffThresholdFinder


class KropffAutomaticSettingsLauncher(QDialog):

    def __init__(self, parent=None):
        self.parent = parent
        super(QDialog, self).__init__(parent)
        self.ui = load_ui('ui_automatic_bragg_peak_settings.ui', baseinstance=self)

        self.init_widgets()

    def init_widgets(self):
        threshold_algo = self.parent.kropff_automatic_threshold_finder_algorithm
        if threshold_algo == KropffThresholdFinder.sliding_average:
            self.ui.sliding_average_radioButton.setChecked(True)
        elif threshold_algo == KropffThresholdFinder.error_function:
            self.ui.error_function_radioButton.setChecked(True)
        elif threshold_algo == KropffThresholdFinder.change_point:
            self.ui.change_point_radioButton.setChecked(True)
        else:
            raise NotImplementedError("Algorithm not implemented!")

    def save_algorithm_selected(self):
        if self.ui.sliding_average_radioButton.isChecked():
            algo_selected = KropffThresholdFinder.sliding_average
        elif self.ui.error_function_radioButton.isChecked():
            algo_selected = KropffThresholdFinder.error_function
        elif self.ui.change_point_radioButton.isChecked():
            algo_selected = KropffThresholdFinder.change_point
        else:
            raise NotImplementedError("Algorithm not implemented!")
        self.parent.kropff_automatic_threshold_finder_algorithm = algo_selected

    def ok_clicked(self):
        self.save_algorithm_selected()
        logging.info("Kropff Bragg peak threshold finder will now use the algorithm {"
                     "self.parent.kropff_automatic_threshold_finder_algorithm}")
        self.parent.kropff_automatic_bragg_peak_threshold_finder_changed()
        self.close()
