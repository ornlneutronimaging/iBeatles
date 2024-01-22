import logging
import pyqtgraph as pg
import numpy as np

from ibeatles.tools.utilities import TimeSpectraKeys
from ibeatles.tools.tof_bin.plot import Plot

from ibeatles.tools.tof_bin.utilities.get import Get
from ibeatles.tools.tof_bin import TO_MICROS_UNITS, TO_ANGSTROMS_UNITS
from ibeatles.utilities.table_handler import TableHandler
from ibeatles.utilities.math_tools import get_value_of_closest_match, get_index_of_closest_match
from ibeatles.utilities.string import format_str

FILE_INDEX_BIN_MARGIN = 0.5
UNSELECTED_BIN = (0, 0, 200, 50)
SELECTED_BIN = (0, 200, 0, 50)


class ManualEventHandler:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger('maverick')

        self.tof_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.tof_array][1] -
                               self.parent.time_spectra[TimeSpectraKeys.tof_array][0]) / 2.

        self.lambda_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.lambda_array][1] -
                                  self.parent.time_spectra[TimeSpectraKeys.lambda_array][0]) / 2

    def refresh_manual_tab(self):
        """refresh the right plot with profile + bin selected when the manual tab is selected"""
        o_plot = Plot(parent=self.parent)
        o_plot.refresh_profile_plot_and_clear_bins()

    # def save_bins_in_all_units(self):
    #
    #     bins = self.parent.manual_bins[time_spectra_x_axis_name]
    #     if not bins:
    #         return
    #
    #     dict_of_bins_item = {}
    #     for _index, _bin in enumerate(bins):
    #         if len(_bin) == 0:
    #             continue
    #
    #         if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
    #             scale_bin = [_bin[0] - FILE_INDEX_BIN_MARGIN, _bin[-1] + FILE_INDEX_BIN_MARGIN]
    #
    #         elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
    #             scale_bin = [_bin[0] - self.tof_bin_margin, _bin[-1] + self.tof_bin_margin]
    #             scale_bin = [_value * TO_MICROS_UNITS for _value in scale_bin]
    #
    #         else:
    #             scale_bin = [
    #                 _bin[0] - self.lambda_bin_margin,
    #                 _bin[-1] + self.lambda_bin_margin,
    #             ]
    #             scale_bin = [_value * TO_ANGSTROMS_UNITS for _value in scale_bin]
    #
    #         item = pg.LinearRegionItem(
    #             values=scale_bin,
    #             orientation="vertical",
    #             brush=UNSELECTED_BIN,
    #             movable=True,
    #             bounds=None,
    #         )
    #         item.setZValue(-10)
    #         self.parent.bin_profile_view.addItem(item)
    #         item.sigRegionChangeFinished.connect(self.parent.bin_manual_region_changed)
    #         item.sigRegionChanged.connect(self.parent.bin_manual_region_changing)
    #         dict_of_bins_item[_index] = item
    #
    #     self.parent.dict_of_bins_item = dict_of_bins_item

    def add_bin(self):

        o_get = Get(parent=self.parent)
        time_spectra_x_axis_name = o_get.x_axis_selected()
        x_axis = self.parent.time_spectra[time_spectra_x_axis_name]

        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        last_row = o_table.row_count()

        if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
            default_bin = [x_axis[0] - FILE_INDEX_BIN_MARGIN,
                           x_axis[0] + FILE_INDEX_BIN_MARGIN]
        elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
            default_bin = [x_axis[0] - self.tof_bin_margin,
                           x_axis[0] + self.tof_bin_margin]
            default_bin = [_value * TO_MICROS_UNITS for _value in default_bin]
        else:
            default_bin = [x_axis[0] - self.lambda_bin_margin,
                           x_axis[0] + self.lambda_bin_margin]
            default_bin = [_value * TO_ANGSTROMS_UNITS for _value in default_bin]

        manual_bins = self.parent.manual_bins
        if manual_bins[TimeSpectraKeys.file_index_array] is None:
            manual_bins[TimeSpectraKeys.file_index_array] = [[x_axis[0]]]
            manual_bins[TimeSpectraKeys.tof_array] = [[self.parent.time_spectra[TimeSpectraKeys.tof_array][0]]]
            manual_bins[TimeSpectraKeys.lambda_array] = [[self.parent.time_spectra[TimeSpectraKeys.lambda_array][0]]]
        else:
            manual_bins[TimeSpectraKeys.file_index_array].append([x_axis[0]])
            manual_bins[TimeSpectraKeys.tof_array].append([self.parent.time_spectra[TimeSpectraKeys.tof_array][0]])
            manual_bins[TimeSpectraKeys.lambda_array].append([self.parent.time_spectra[TimeSpectraKeys.lambda_array][0]])
        self.parent.manual_bins = manual_bins

        item = pg.LinearRegionItem(values=default_bin,
                                   orientation='vertical',
                                   brush=SELECTED_BIN,
                                   movable=True,
                                   bounds=None)
        item.setZValue(-10)
        item.sigRegionChangeFinished.connect(self.parent.bin_manual_region_changed)
        item.sigRegionChanged.connect(self.parent.bin_manual_region_changing)

        self.parent.bin_profile_view.addItem(item)
        # dict_of_bins_item[last_row] = item
        # self.parent.dict_of_bins_item = dict_of_bins_item
        self.parent.list_of_manual_bins_item.append(item)

        # add new entry in table
        o_table.insert_empty_row(last_row)

        o_table.insert_item(row=last_row,
                            column=0,
                            value=f"{last_row}",
                            editable=False)

        _file_index = self.parent.time_spectra[TimeSpectraKeys.file_index_array][0]
        o_table.insert_item(row=last_row,
                            column=1,
                            value=_file_index,
                            editable=False)

        _tof = self.parent.time_spectra[TimeSpectraKeys.tof_array][0] * TO_MICROS_UNITS
        o_table.insert_item(row=last_row,
                            column=2,
                            value=_tof,
                            format_str="{:.2f}",
                            editable=False)

        _lambda = self.parent.time_spectra[TimeSpectraKeys.lambda_array][0] * TO_ANGSTROMS_UNITS
        o_table.insert_item(row=last_row,
                            column=3,
                            value=_lambda,
                            format_str="{:.3f}",
                            editable=False)

    def clear_all_items(self):
        list_of_manually_bins_item = self.parent.list_of_manual_bins_item
        for _item in list_of_manually_bins_item:
            self.parent.bin_profile_view.removeItem(_item)

        self.parent.list_of_manual_bins_item = None

    def display_all_items(self):
        list_of_manually_bins_item = self.parent.list_of_manual_bins_item
        for _item in list_of_manually_bins_item:
            self.parent.bin_profile_view.addItem(_item)

    def populate_table_with_this_table(self, table=None):
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        o_table.remove_all_rows()

        file_index_array = table[TimeSpectraKeys.file_index_array]
        tof_array = table[TimeSpectraKeys.tof_array]
        lambda_array = table[TimeSpectraKeys.lambda_array]

        self.parent.list_of_manual_bins_item = []

        if file_index_array is None:
            return

        _row = 0
        for _index, _bin in enumerate(file_index_array):

            if not _bin:
                continue

            o_table.insert_empty_row(_row)

            o_table.insert_item(row=_row,
                                column=0,
                                value=f"{_row}",
                                editable=False)

            _file_index = _bin
            _file_index_formatted = format_str(_file_index,
                                               format_str="{:d}",
                                               factor=1,
                                               data_type=TimeSpectraKeys.file_index_array)
            o_table.insert_item(row=_row,
                                column=1,
                                format_str=_file_index_formatted,
                                editable=False)

            _tof = tof_array[_index]
            _tof_formatted = format_str(_tof,
                                        format_str="{:.2f}",
                                        factor=TO_MICROS_UNITS,
                                        data_type=TimeSpectraKeys.tof_array)

            o_table.insert_item(row=_row,
                                column=2,
                                format_str=_tof_formatted,
                                editable=False)

            _lambda = lambda_array[_index]
            _lambda_formatted = format_str(_lambda,
                                           format_str="{:.3f}",
                                           factor=TO_ANGSTROMS_UNITS,
                                           data_type=TimeSpectraKeys.lambda_array)
            o_table.insert_item(row=_row,
                                column=3,
                                format_str=_lambda_formatted,
                                editable=False)

            item = self.add_bin_in_plot(row=_row,
                                        file_index_bin=_bin,
                                        tof_bin=_tof,
                                        lambda_bin=_lambda)

            self.parent.list_of_manual_bins_item.append(item)

            _row += 1

        o_table.select_rows([0])

    # def populate_table_with_auto_mode(self):
    #     o_get = Get(parent=self.parent)
    #     bins = o_get.auto_bins_currently_activated()
    #     self.parent.manual_bins = bins
    #     self.populate_table_with_this_table(table=bins)

    def add_bin_in_plot(self, row=0, file_index_bin=None, tof_bin=None, lambda_bin=None):
        o_get = Get(parent=self.parent)
        current_x_axis = o_get.x_axis_selected()
        if current_x_axis == TimeSpectraKeys.file_index_array:
            bin = file_index_bin
            bin_size = [bin[0] - FILE_INDEX_BIN_MARGIN,
                        bin[-1] + FILE_INDEX_BIN_MARGIN]
        elif current_x_axis == TimeSpectraKeys.tof_array:
            bin = tof_bin
            bin_size = [bin[0] - self.tof_bin_margin,
                        bin[-1] + self.tof_bin_margin]
        elif current_x_axis == TimeSpectraKeys.lambda_array:
            bin = lambda_bin
            bin_size = [bin[0] - self.lambda_bin_margin,
                        bin[1] + self.lambda_bin_margin]
        else:
            raise NotImplementedError("x_axis not implemented!")

        if row == 0:
            brush_selection = SELECTED_BIN
        else:
            brush_selection = UNSELECTED_BIN

        item = pg.LinearRegionItem(values=bin_size,
                                   orientation='vertical',
                                   brush=brush_selection,
                                   movable=True,
                                   bounds=None)
        item.setZValue(-10)
        item.sigRegionChangeFinished.connect(self.parent.bin_manual_region_changed)
        self.parent.bin_profile_view.addItem(item)

        return item

    def bin_manually_moved(self, item_id=None):

        self.bin_manually_moving(item_id=item_id)

        # 1. using region selected threshold, and the current axis, find the snapping left and right indexes
        #    and save them into a manual_snapping_indexes_bins = {0: [0, 3], 1: [1, 10], ..}
        self.record_snapping_indexes_bin()

        # 2. using those indexes create the ranges for each bins and for each time axis and save those in
        #    self.parent.manual_bins['file_index_array': [[0, 1, 2, 3], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], ...], ...]
        self.create_all_ranges()

        # 3. update table
        self.update_table()

    def bin_manually_moving(self, item_id=None):
        o_get = Get(parent=self.parent)
        working_row = o_get.manual_working_row(working_item_id=item_id)
        self.select_working_row(working_row=working_row)

    def select_working_row(self, working_row=0):
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        o_table.block_signals(True)
        o_table.select_rows(list_of_rows=[working_row])
        o_table.block_signals(False)

    def update_table(self):

        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        o_table.block_signals(True)

        file_index_array = self.parent.manual_bins[TimeSpectraKeys.file_index_array]
        tof_array = self.parent.manual_bins[TimeSpectraKeys.tof_array]
        lambda_array = self.parent.manual_bins[TimeSpectraKeys.lambda_array]

        for _row, list_runs in enumerate(file_index_array):

            list_runs_formatted = format_str(list_runs,
                                             format_str="{:d}",
                                             factor=1,
                                             data_type=TimeSpectraKeys.file_index_array)
            o_table.set_item_with_str(row=_row, column=1, cell_str=list_runs_formatted)

            list_tof = tof_array[_row]
            list_tof_formatted = format_str(list_tof,
                                            format_str="{:.2f}",
                                            factor=TO_MICROS_UNITS,
                                            data_type=TimeSpectraKeys.tof_array)
            o_table.set_item_with_str(row=_row, column=2, cell_str=list_tof_formatted)

            list_lambda = lambda_array[_row]
            list_lambda_formatted = format_str(list_lambda,
                                               format_str="{:.3f}",
                                               factor=TO_ANGSTROMS_UNITS,
                                               data_type=TimeSpectraKeys.lambda_array)
            o_table.set_item_with_str(row=_row, column=3, cell_str=list_lambda_formatted)

        o_table.block_signals(False)

    # def create_all_ranges(self):
    #     manual_snapping_indexes_bins = self.parent.manual_snapping_indexes_bins
    #
    #     file_index_array = {}
    #     tof_array = {}
    #     lambda_array = {}
    #
    #     for _bin in manual_snapping_indexes_bins.keys():
    #         left_index, right_index = manual_snapping_indexes_bins[_bin]
    #
    #         # tof_array
    #         bins_file_index_array = self.parent.time_spectra[TimeSpectraKeys.file_index_array]
    #         bins_file_index_range = bins_file_index_array[left_index: right_index + 1]
    #         file_index_array[_bin] = bins_file_index_range
    #
    #         # tof_array
    #         bins_tof_array = self.parent.time_spectra[TimeSpectraKeys.tof_array]
    #         bins_tof_range = bins_tof_array[left_index: right_index + 1]
    #         tof_array[_bin] = bins_tof_range
    #
    #         # lambda_array
    #         bins_lambda_array = self.parent.time_spectra[TimeSpectraKeys.lambda_array]
    #         bins_lambda_range = bins_lambda_array[left_index: right_index + 1]
    #         lambda_array[_bin] = bins_lambda_range
    #
    #     self.parent.manual_bins[TimeSpectraKeys.file_index_array] = file_index_array
    #     self.parent.manual_bins[TimeSpectraKeys.tof_array] = tof_array
    #     self.parent.manual_bins[TimeSpectraKeys.lambda_array] = lambda_array

    def create_all_ranges(self):
        manual_snapping_indexes_bins = self.parent.manual_snapping_indexes_bins
    
        file_index_array = []
        tof_array = []
        lambda_array = []

        for _bin in manual_snapping_indexes_bins.keys():
            left_index, right_index = manual_snapping_indexes_bins[_bin]

            # tof_array
            bins_file_index_array = list(self.parent.time_spectra[
                TimeSpectraKeys.file_index_array])
            bins_file_index_range = bins_file_index_array[left_index: right_index + 1]
            file_index_array.append(bins_file_index_range)

            # tof_array
            bins_tof_array = self.parent.time_spectra[TimeSpectraKeys.tof_array]
            bins_tof_range = bins_tof_array[left_index: right_index + 1]
            tof_array.append(bins_tof_range)
    
            # lambda_array
            bins_lambda_array = self.parent.time_spectra[TimeSpectraKeys.lambda_array]
            bins_lambda_range = bins_lambda_array[left_index: right_index + 1]
            lambda_array.append(bins_lambda_range)
    
        self.parent.manual_bins[TimeSpectraKeys.file_index_array] = file_index_array
        self.parent.manual_bins[TimeSpectraKeys.tof_array] = tof_array
        self.parent.manual_bins[TimeSpectraKeys.lambda_array] = lambda_array

    # def update_manual_snapping_indexes_bins(self):
    #     """this will take the manual_bins list, use the x-axis currently selected and replace the
    #     manual_snapping_indexes_bins [[left, right], [left, right]....] of the current xaxis"""
    #     manual_snapping_indexes_bin = {}
    #     for _row, _bin_range in enumerate(self.parent.manual_bins[TimeSpectraKeys.file_index_array]):
    #         print(f"{_bin_range =}")
    #         manual_snapping_indexes_bin[_row] = [_bin_range[0], _bin_range[-1]]
    #     self.parent.manual_snapping_indexes_bins = manual_snapping_indexes_bin
    #     print(f"{self.parent.manual_snapping_indexes_bins =}")

    def update_items_displayed(self):
        """
        this will remove the old item and put the new one with the edges snap to the x-axis
        """
        o_get = Get(parent=self.parent)
        x_axis_type_selected = o_get.x_axis_selected()
        if x_axis_type_selected == TimeSpectraKeys.tof_array:
            factor = TO_MICROS_UNITS
        elif x_axis_type_selected == TimeSpectraKeys.lambda_array:
            factor = TO_ANGSTROMS_UNITS
        else:
            factor = 1

        x_axis = self.parent.manual_bins[x_axis_type_selected]
        if x_axis is None:
            return

        if len(self.parent.list_of_manual_bins_item) == 0:
            return

        list_of_manual_bins_item = []
        for _row, _x in enumerate(x_axis):

            left_value_checked = _x[0] * factor
            right_value_checked = _x[-1] * factor

            _item = self.parent.list_of_manual_bins_item[_row]

            self.parent.bin_profile_view.removeItem(_item)

            item = pg.LinearRegionItem(values=[left_value_checked, right_value_checked],
                                       orientation='vertical',
                                       brush=SELECTED_BIN,
                                       movable=True,
                                       bounds=None)
            item.setZValue(-10)
            item.sigRegionChangeFinished.connect(self.parent.bin_manual_region_changed)
            item.sigRegionChanged.connect(self.parent.bin_manual_region_changing)
            self.parent.bin_profile_view.addItem(item)
            list_of_manual_bins_item.append(item)

        self.parent.list_of_manual_bins_item = list_of_manual_bins_item

    def record_snapping_indexes_bin(self):
        """
        This will check each bin from the manual table and move, if necessary, any of the edges
        to snap to the closet x-axis values
        """
        manual_snapping_indexes_bins = {}
        for _row, _item in enumerate(self.parent.list_of_manual_bins_item):
            [left, right] = _item.getRegion()

            # bring left and right to closest correct values
            left_value_checked, right_value_checked = self.checked_range(left=left, right=right)
            manual_snapping_indexes_bins[_row] = [left_value_checked, right_value_checked]

        print(f"{manual_snapping_indexes_bins =}")
        self.parent.manual_snapping_indexes_bins = manual_snapping_indexes_bins

    def margin(self, axis_type=TimeSpectraKeys.file_index_array):
        if axis_type == TimeSpectraKeys.file_index_array:
            return FILE_INDEX_BIN_MARGIN
        elif axis_type == TimeSpectraKeys.tof_array:
            return self.tof_bin_margin
        elif axis_type == TimeSpectraKeys.lambda_array:
            return self.lambda_bin_margin
        else:
            raise NotImplementedError(f"axis type {axis_type} not implemented!")

    def checked_range(self, left=0, right=0):
        """this method makes sure that the left and right values stay within the maximum range of the data
        for the current axis selected"""
        o_get = Get(parent=self.parent)
        x_axis_type_selected = o_get.x_axis_selected()
        x_axis = self.parent.time_spectra[x_axis_type_selected]

        if x_axis_type_selected == TimeSpectraKeys.tof_array:
            factor = TO_MICROS_UNITS
        elif x_axis_type_selected == TimeSpectraKeys.lambda_array:
            factor = TO_ANGSTROMS_UNITS
        else:
            factor = 1

        left /= factor
        right /= factor

        if left < x_axis[0]:
            left = x_axis[0]

        if right >= x_axis[-1]:
            right = x_axis[-1]

        index_clean_left_value = get_index_of_closest_match(array_to_look_for=x_axis,
                                                            value=left,
                                                            left_margin=True)
        index_clean_right_value = get_index_of_closest_match(array_to_look_for=x_axis,
                                                             value=right,
                                                             left_margin=False)

        return (np.min([index_clean_left_value, index_clean_right_value]),
                np.max([index_clean_left_value, index_clean_right_value]))
