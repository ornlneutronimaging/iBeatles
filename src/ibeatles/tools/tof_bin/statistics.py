import numpy as np
from qtpy.QtWidgets import QApplication

from src.ibeatles.utilities import TO_MICROS_UNITS, TO_ANGSTROMS_UNITS
from src.ibeatles.utilities.table_handler import TableHandler


from src.ibeatles.tools.tof_bin import BinMode, BinAutoMode, BinAlgorithm
from src.ibeatles.tools.tof_bin import StatisticsName, StatisticsRegion
from src.ibeatles.tools.utilities import TimeSpectraKeys
from src.ibeatles.tools.tof_bin.utilities.get import Get
from src.ibeatles.tools.tof_bin.utilities.string import format_str


class Statistics:
    def __init__(self, parent=None):
        self.parent = parent

    def update(self):
        o_get = Get(parent=self.parent)

        # check if we are looking for the auto or the manual bins
        bin_mode = o_get.bin_mode()

        if bin_mode == BinMode.auto:
            bin_auto_mode = o_get.bin_auto_mode()
            if bin_auto_mode == BinAutoMode.linear:
                list_bins = self.parent.linear_bins
            else:
                list_bins = self.parent.log_bins

        else:
            list_bins = self.parent.manual_bins

        o_table = TableHandler(table_ui=self.parent.ui.statistics_tableWidget)
        o_table.remove_all_rows()

        # if no bins to display, stop here
        if list_bins[TimeSpectraKeys.file_index_array] is None:
            return

        file_index_bins = list_bins[TimeSpectraKeys.file_index_array]
        tof_bins = list_bins[TimeSpectraKeys.tof_array]
        lambda_bins = list_bins[TimeSpectraKeys.lambda_array]

        mean_array_full = []
        median_array_full = []
        std_array_full = []
        min_array_full = []
        max_array_full = []

        mean_array_roi = []
        median_array_roi = []
        std_array_roi = []
        min_array_roi = []
        max_array_roi = []

        _row = 0
        for _bin_index, _bin in enumerate(file_index_bins):
            o_table.insert_empty_row(row=_row)

            o_table.insert_item(row=_row, column=0, value=str(_row), editable=False)

            if not _bin:
                mean_array_full.append(np.nan)
                median_array_full.append(np.nan)
                std_array_full.append(np.nan)
                min_array_full.append(np.nan)
                max_array_full.append(np.nan)

                mean_array_roi.append(np.nan)
                median_array_roi.append(np.nan)
                std_array_roi.append(np.nan)
                min_array_roi.append(np.nan)
                max_array_roi.append(np.nan)

                list_runs_formatted = "N/A"
                list_tof_formatted = "N/A"
                list_lambda_formatted = "N/A"
                str_mean = "N/A"
                str_median = "N/A"
                str_std = "N/A"
                str_min = "N/A"
                str_max = "N/A"

            else:
                list_runs = file_index_bins[_bin_index]

                list_runs_formatted = format_str(
                    list_runs,
                    format_str="{:d}",
                    factor=1,
                    data_type=TimeSpectraKeys.file_index_array,
                )

                list_tof = tof_bins[_bin_index]
                list_tof_formatted = format_str(
                    list_tof,
                    format_str="{:.2f}",
                    factor=TO_MICROS_UNITS,
                    data_type=TimeSpectraKeys.tof_array,
                )

                list_lambda = lambda_bins[_bin_index]
                list_lambda_formatted = format_str(
                    list_lambda,
                    format_str="{:.3f}",
                    factor=TO_ANGSTROMS_UNITS,
                    data_type=TimeSpectraKeys.lambda_array,
                )

                # calculate statistics
                _data_dict = self.extract_data_for_this_bin(list_runs=list_runs)

                full_image = _data_dict["full_image"]
                roi_of_image = _data_dict["roi_of_image"]

                # mean
                full_mean = np.mean(full_image)
                roi_mean = np.mean(roi_of_image)
                mean_array_full.append(full_mean)
                mean_array_roi.append(roi_mean)
                str_mean = f"{full_mean:.3f} ({roi_mean:.3f})"

                # median
                full_median = np.median(full_image)
                roi_median = np.median(roi_of_image)
                median_array_full.append(full_median)
                median_array_roi.append(roi_median)
                str_median = f"{full_median:.3f} ({roi_median:.3f})"

                # std
                full_std = np.std(full_image)
                roi_std = np.std(roi_of_image)
                std_array_full.append(full_std)
                std_array_roi.append(roi_std)
                str_std = f"{full_std:.3f} ({roi_std:.3f})"

                # min
                full_min = np.min(full_image)
                roi_min = np.min(roi_of_image)
                min_array_full.append(full_min)
                min_array_roi.append(roi_min)
                str_min = f"{full_min:.3f} ({roi_min:.3f})"

                # max
                full_max = np.max(full_image)
                roi_max = np.max(roi_of_image)
                max_array_full.append(full_max)
                max_array_roi.append(roi_max)
                str_max = f"{full_max:.3f} ({roi_max:.3f})"

            o_table.insert_item(
                row=_row, column=1, value=list_runs_formatted, editable=False
            )

            o_table.insert_item(
                row=_row, column=2, value=list_tof_formatted, editable=False
            )

            o_table.insert_item(
                row=_row, column=3, value=list_lambda_formatted, editable=False
            )

            o_table.insert_item(row=_row, column=4, value=str_mean, editable=False)

            o_table.insert_item(row=_row, column=5, value=str_median, editable=False)

            o_table.insert_item(row=_row, column=6, value=str_std, editable=False)

            o_table.insert_item(row=_row, column=7, value=str_min, editable=False)

            o_table.insert_item(row=_row, column=8, value=str_max, editable=False)

            _row += 1

        self.parent.current_stats[bin_mode] = {
            StatisticsName.mean: {
                StatisticsRegion.full: mean_array_full,
                StatisticsRegion.roi: mean_array_roi,
            },
            StatisticsName.median: {
                StatisticsRegion.full: median_array_full,
                StatisticsRegion.roi: median_array_roi,
            },
            StatisticsName.std: {
                StatisticsRegion.full: std_array_full,
                StatisticsRegion.roi: std_array_roi,
            },
            StatisticsName.min: {
                StatisticsRegion.full: min_array_full,
                StatisticsRegion.roi: min_array_roi,
            },
            StatisticsName.max: {
                StatisticsRegion.full: max_array_full,
                StatisticsRegion.roi: max_array_roi,
            },
        }

    def extract_data_for_this_bin(self, list_runs=None):
        """
        this method calculate the mean or median of full image and ROI selected of all the runs that
        belongs to that bin (list_runs are the run of that particular bin)

        :param list_runs:
        :return:
        """
        # retrieve statistics
        bin_roi = self.parent.bin_roi
        x0 = bin_roi["x0"]
        y0 = bin_roi["y0"]
        width = bin_roi["width"]
        height = bin_roi["height"]

        data_to_work_with = []
        for _run_index in list_runs:
            data_to_work_with.append(self.parent.images_array[_run_index])

        region_to_work_with = [
            _data[y0 : y0 + height, x0 : x0 + width] for _data in data_to_work_with
        ]

        # how to add images
        o_get = Get(parent=self.parent)
        bin_method = o_get.bin_add_method()
        if bin_method == BinAlgorithm.mean:
            full_image_to_work_with = np.mean(data_to_work_with, axis=0)
            roi_image_to_work_with = np.mean(region_to_work_with, axis=0)
        elif bin_method == BinAlgorithm.median:
            full_image_to_work_with = np.median(data_to_work_with, axis=0)
            roi_image_to_work_with = np.median(region_to_work_with, axis=0)
        else:
            raise NotImplementedError(
                "this method of adding the binned images is not supported!"
            )

        return {
            "full_image": full_image_to_work_with,
            "roi_of_image": roi_image_to_work_with,
        }

    def plot_statistics(self):
        o_get = Get(parent=self.parent)
        bin_mode = o_get.bin_mode()

        if bin_mode == BinMode.auto:
            bin_auto_mode = o_get.bin_auto_mode()
            if bin_auto_mode == BinAutoMode.linear:
                list_bins = self.parent.linear_bins
            else:
                list_bins = self.parent.log_bins

        else:
            list_bins = self.parent.manual_bins

        # if no bins to display, stop here
        if list_bins[TimeSpectraKeys.file_index_array] is None:
            self.parent.statistics_plot.ax1.clear()
            QApplication.processEvents()
            return

        stats_requested = o_get.bin_statistics_plot_requested()

        stat_data_dict = self.parent.current_stats[bin_mode][stats_requested]

        full_array = stat_data_dict[StatisticsRegion.full]
        roi_array = stat_data_dict[StatisticsRegion.roi]

        self.parent.statistics_plot.ax1.clear()
        self.parent.statistics_plot.ax1.plot(full_array, ".", label="full image")
        self.parent.statistics_plot.ax1.plot(roi_array, "+", label="roi only")

        self.parent.statistics_plot.ax1.set_xlabel("Bin #")
        self.parent.statistics_plot.ax1.set_ylabel(stats_requested)
        self.parent.statistics_plot.ax1.legend(loc="upper right")

        self.parent.statistics_plot.draw()
