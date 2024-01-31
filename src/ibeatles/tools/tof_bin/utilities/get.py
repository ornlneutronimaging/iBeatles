from src.ibeatles.tools.tof_bin import BinAutoMode
from src.ibeatles.tools.tof_bin import StatisticsName

from src.ibeatles.tools.utilities import TimeSpectraKeys
from src.ibeatles.tools.utilities import CombineAlgorithm
from src.ibeatles.tools.tof_bin import BinMode


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def auto_bins_currently_activated(self):
        auto_bin_mode = self.bin_auto_mode()
        if auto_bin_mode == BinAutoMode.linear:
            return self.parent.linear_bins
        elif auto_bin_mode == BinAutoMode.log:
            return self.parent.log_bins
        else:
            raise NotImplementedError("Auto bin mode not implemented!")

    def x_axis_selected(self):
        if self.parent.bin_file_index_radioButton.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.bin_tof_radioButton.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.bin_lambda_radioButton.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError("xaxis not implemented in the bin tab!")

    def bin_auto_mode(self):
        if self.parent.ui.auto_log_radioButton.isChecked():
            return BinAutoMode.log
        elif self.parent.ui.auto_linear_radioButton.isChecked():
            return BinAutoMode.linear
        else:
            raise NotImplementedError("auto bin mode not implemented!")

    def bin_mode(self):
        if self.parent.ui.bin_tabWidget.currentIndex() == 0:
            return BinMode.auto
        elif self.parent.ui.bin_tabWidget.currentIndex() == 1:
            return BinMode.manual
        elif self.parent.ui.bin_tabWidget.currentIndex() == 2:
            return BinMode.settings
        else:
            raise NotImplementedError("bin mode not implemented!")

    def current_bins_activated(self):
        """
        Looking at the active auto or manual tab and linear or log to figure out which bins
        are currently used in the displayed
        :return: dictionary of the bins to use. Can be either self.parent.linear_bins, self.parent.log_bins
        or self.parent.manual_bins
        """
        bin_mode = self.bin_mode()
        if bin_mode == BinMode.manual:
            return self.parent.manual_bins
        elif bin_mode == BinMode.auto:
            bin_auto_mode = self.bin_auto_mode()
            if bin_auto_mode == BinAutoMode.linear:
                return self.parent.linear_bins
            elif bin_auto_mode == BinAutoMode.log:
                return self.parent.log_bins
            else:
                raise NotImplementedError("bin auto mode not implemented")
        else:
            raise NotImplementedError("bin mode not implemented!")

    def auto_log_bin_requested(self):
        if self.parent.ui.bin_auto_log_file_index_radioButton.isChecked():
            return self.parent.ui.auto_log_file_index_spinBox.value()
        elif self.parent.ui.bin_auto_log_tof_radioButton.isChecked():
            return self.parent.ui.auto_log_tof_doubleSpinBox.value()
        elif self.parent.ui.bin_auto_log_lambda_radioButton.isChecked():
            return self.parent.ui.auto_log_lambda_doubleSpinBox.value()
        else:
            raise NotImplementedError(f"auto log bin algorithm not implemented!")

    def bin_add_method(self):
        if self.parent.ui.combine_mean_radioButton.isChecked():
            return CombineAlgorithm.mean
        elif self.parent.ui.combine_median_radioButton.isChecked():
            return CombineAlgorithm.median
        else:
            raise NotImplementedError("Combine algorithm is not implemented!")

    def bin_statistics_plot_requested(self):
        current_index = self.parent.ui.bin_stats_comboBox.currentIndex()
        list_name = [StatisticsName.mean,
                     StatisticsName.median,
                     StatisticsName.std,
                     StatisticsName.min,
                     StatisticsName.max]
        return list_name[current_index]

    def current_bin_tab_working_axis(self):
        bin_mode = self.bin_auto_mode()
        if bin_mode == BinAutoMode.log:
            return self.bin_log_axis()
        elif bin_mode == BinAutoMode.linear:
            return self.bin_linear_axis()
        else:
            raise NotImplementedError(f"type not supported")

    def bin_log_axis(self):
        if self.parent.ui.bin_auto_log_file_index_radioButton.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.ui.bin_auto_log_tof_radioButton.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.ui.bin_auto_log_lambda_radioButton.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError(f"type not supported")

    def bin_linear_axis(self):
        if self.parent.ui.auto_linear_file_index_radioButton.isChecked():
            return TimeSpectraKeys.file_index_array
        elif self.parent.ui.auto_linear_tof_radioButton.isChecked():
            return TimeSpectraKeys.tof_array
        elif self.parent.ui.auto_linear_lambda_radioButton.isChecked():
            return TimeSpectraKeys.lambda_array
        else:
            raise NotImplementedError(f"type not supported")

    def manual_working_row(self, working_item_id=None):
        list_item_id = self.parent.list_of_manual_bins_item
        for _row, item in enumerate(list_item_id):
            if item == working_item_id:
                return _row
        return -1
