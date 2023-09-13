from qtpy.QtWidgets import QDialog

from ibeatles import load_ui
from ibeatles import DataType
from ibeatles.fitting.kropff import KropffThresholdFinder
from ibeatles.session import SessionSubKeys
from ibeatles.fitting.kropff import SessionSubKeys as KropffSessionSubKeys
from ibeatles.fitting import FittingTabSelected

class KropffAutomaticSettingsLauncher(QDialog):

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        super(QDialog, self).__init__(parent)
        self.ui = load_ui('ui_automatic_bragg_peak_settings.ui', baseinstance=self)
        self.init_widgets()

    def init_widgets(self):
        threshold_algo = self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][
            KropffSessionSubKeys.automatic_bragg_peak_threshold_algorithm]

        if threshold_algo == KropffThresholdFinder.sliding_average:
            self.ui.sliding_average_radioButton.setChecked(True)
        elif threshold_algo == KropffThresholdFinder.error_function:
            self.ui.error_function_radioButton.setChecked(True)
        elif threshold_algo == KropffThresholdFinder.change_point:
            self.ui.change_point_radioButton.setChecked(True)
        else:
            raise NotImplementedError("Algorithm not implemented!")

        # init threshold width
        fitting_width = self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][
            KropffSessionSubKeys.automatic_fitting_threshold_width]
        self.ui.kropff_threshold_width_slider.setValue(fitting_width)

    def save_algorithm_selected(self):
        if self.ui.sliding_average_radioButton.isChecked():
            algo_selected = KropffThresholdFinder.sliding_average
        elif self.ui.error_function_radioButton.isChecked():
            algo_selected = KropffThresholdFinder.error_function
        elif self.ui.change_point_radioButton.isChecked():
            algo_selected = KropffThresholdFinder.change_point
        else:
            raise NotImplementedError("Algorithm not implemented!")
        # self.parent.kropff_automatic_threshold_finder_algorithm = algo_selected
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][
            KropffSessionSubKeys.automatic_bragg_peak_threshold_algorithm] = algo_selected

    def save_slider_value(self):
        self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff][
            KropffSessionSubKeys.automatic_fitting_threshold_width] = self.ui.kropff_threshold_width_slider.value()

    def slider_moved(self, _):
        self.slider_clicked()

    def slider_clicked(self):
        slider_value = self.ui.kropff_threshold_width_slider.value()
        self.ui.kropff_threshold_width_value.setText(str(slider_value))

    def slider_changed(self, _):
        self.slider_clicked()

    def ok_clicked(self):
        self.save_algorithm_selected()
        self.save_slider_value()
        self.close()
