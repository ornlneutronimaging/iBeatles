import logging
import numpy as np
import pyqtgraph as pg
from qtpy.QtWidgets import QCheckBox, QMenu
from qtpy import QtGui

# from .log_bin import LogBin
from ibeatles.session import SessionSubKeys
from ibeatles.utilities.table_handler import TableHandler
from ibeatles.tools.tof_bin import TO_MICROS_UNITS, TO_ANGSTROMS_UNITS

from ibeatles.tools.tof_bin import BinMode
from ibeatles.tools.tof_bin.plot import Plot
from ibeatles.tools.tof_bin.utilities.get import Get
from ibeatles.tools.tof_bin.log_bin import LogBin
# from . import TO_MICROS_UNITS, TO_ANGSTROMS_UNITS
from ibeatles.tools.tof_bin import BinAutoMode
from ibeatles.tools.utilities import TimeSpectraKeys

# from .plot import Plot
# from ..utilities.table_handler import TableHandler
# from ..utilities.status_message_config import StatusMessageStatus, show_status_message
# from .linear_bin import LinearBin

FILE_INDEX_BIN_MARGIN = 0.5
UNSELECTED_BIN = (0, 0, 200, 50)
SELECTED_BIN = (0, 200, 0, 50)


class AutoEventHandler:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger('maverick')

        self.tof_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.tof_array][1] -
                               self.parent.time_spectra[TimeSpectraKeys.tof_array][0]) / 2.

        self.lambda_bin_margin = (self.parent.time_spectra[TimeSpectraKeys.lambda_array][1] -
                                  self.parent.time_spectra[TimeSpectraKeys.lambda_array][0]) / 2

    def refresh_auto_tab(self):
        # refresh the right plot with profile + bin selected when the auto tab is selected
        o_plot = Plot(parent=self.parent)
        o_plot.refresh_profile_plot()

        o_get = Get(parent=self.parent)
        time_spectra_x_axis_name = o_get.x_axis_selected()

        if o_get.bin_auto_mode() == BinAutoMode.linear:
            bins = self.parent.linear_bins[time_spectra_x_axis_name]
            bins_selected = self.parent.linear_bins_selected
        else:
            bins = self.parent.log_bins[time_spectra_x_axis_name]
            bins_selected = self.parent.log_bins_selected

        dict_of_bins_item = {}
        for _index, _bin in enumerate(bins):

            if _bin == []:
                continue

            if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:

                scale_bin = [_bin[0] - FILE_INDEX_BIN_MARGIN,
                             _bin[-1] + FILE_INDEX_BIN_MARGIN]

            elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:

                scale_bin = [_bin[0] - self.tof_bin_margin,
                             _bin[-1] + self.tof_bin_margin]
                scale_bin = [_value * TO_MICROS_UNITS for _value in scale_bin]

            else:

                scale_bin = [_bin[0] - self.lambda_bin_margin,
                             _bin[-1] + self.lambda_bin_margin]
                scale_bin = [_value * TO_ANGSTROMS_UNITS for _value in scale_bin]

            item = pg.LinearRegionItem(values=scale_bin,
                                       orientation='vertical',
                                       brush=UNSELECTED_BIN,
                                       movable=False,
                                       bounds=None)
            item.setZValue(-10)
            self.parent.bin_profile_view.addItem(item)
            dict_of_bins_item[_index] = item

        self.parent.dict_of_bins_item = dict_of_bins_item

        # bring back the row selected
        if bins_selected:
            o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
            o_table.select_rows(bins_selected)

    def auto_linear_radioButton_changed(self):
        file_index_status = False
        tof_status = False
        lambda_status = False
        if self.parent.ui.auto_linear_file_index_radioButton.isChecked():
            file_index_status = True
            source_button = TimeSpectraKeys.file_index_array
        elif self.parent.ui.auto_linear_tof_radioButton.isChecked():
            tof_status = True
            source_button = TimeSpectraKeys.tof_array
        else:
            lambda_status = True
            source_button = TimeSpectraKeys.lambda_array

        self.parent.ui.auto_linear_file_index_spinBox.setEnabled(file_index_status)
        self.parent.ui.auto_linear_tof_doubleSpinBox.setEnabled(tof_status)
        self.parent.ui.bin_auto_linear_tof_units_label.setEnabled(tof_status)
        self.parent.ui.auto_linear_lambda_doubleSpinBox.setEnabled(lambda_status)
        self.parent.ui.bin_auto_linear_lambda_units_label.setEnabled(lambda_status)

        # self.bin_auto_linear_changed(source_radio_button=source_button)

    def auto_log_radioButton_changed(self):

        file_index_status = False
        tof_status = False
        lambda_status = False
        if self.parent.ui.bin_auto_log_file_index_radioButton.isChecked():
            file_index_status = True
            source_button = TimeSpectraKeys.file_index_array
        elif self.parent.ui.bin_auto_log_tof_radioButton.isChecked():
            tof_status = True
            source_button = TimeSpectraKeys.tof_array
        else:
            lambda_status = True
            source_button = TimeSpectraKeys.lambda_array

        self.parent.ui.auto_log_file_index_spinBox.setEnabled(file_index_status)
        self.parent.ui.auto_log_tof_doubleSpinBox.setEnabled(tof_status)
        self.parent.ui.auto_log_lambda_doubleSpinBox.setEnabled(lambda_status)

        self.bin_auto_log_changed(source_radio_button=source_button)

    def bin_auto_radioButton_clicked(self):
        state_auto = self.parent.ui.auto_log_radioButton.isChecked()
        self.parent.ui.auto_linear_radioButton.setChecked(state_auto)
        self.parent.ui.auto_linear_radioButton.setChecked(not state_auto)
        self.parent.ui.bin_auto_log_frame.setEnabled(state_auto)
        self.parent.ui.bin_auto_linear_frame.setEnabled(not state_auto)
        o_get = Get(parent=self.parent)
        if o_get.bin_auto_mode() == BinAutoMode.log:
            self.auto_log_radioButton_changed()
        else:
            self.auto_linear_radioButton_changed()

    def bin_auto_log_changed(self, source_radio_button=TimeSpectraKeys.file_index_array):
        self.logger.info(f"bin auto log changed: radio button changed -> {source_radio_button}")
        o_bin = LogBin(parent=self.parent,
                       source_radio_button=source_radio_button)

        self.parent.ui.auto_log_file_index_spinBox.blockSignals(True)
        self.parent.ui.auto_log_tof_doubleSpinBox.blockSignals(True)
        self.parent.ui.auto_log_lambda_doubleSpinBox.blockSignals(True)

        self.logger.info(f"-> original raw_file_index_array_binned:"
                         f" {self.parent.time_spectra[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> original raw_tof_array_binned: {self.parent.time_spectra[TimeSpectraKeys.tof_array]}")
        self.logger.info(f"-> original raw_lambda_array_binned:"
                         f" {self.parent.time_spectra[TimeSpectraKeys.lambda_array]}")

        o_get = Get(parent=self.parent)
        log_bin_requested = o_get.auto_log_bin_requested()
        self.logger.info(f"--> bin requested: {log_bin_requested}")

        if source_radio_button == TimeSpectraKeys.file_index_array:
            o_bin.create_log_file_index_bin_array(bin_value=log_bin_requested)

        elif source_radio_button == TimeSpectraKeys.tof_array:
            o_bin.create_log_file_index_bin_array(bin_value=log_bin_requested)
            o_bin.create_log_bin_arrays()

        elif source_radio_button == TimeSpectraKeys.lambda_array:
            o_bin.create_log_file_index_bin_array(bin_value=log_bin_requested)
            o_bin.create_log_bin_arrays()

        else:
            raise NotImplementedError("bin auto log algorithm not implemented!")

        self.logger.info(f"-> file_index_array_binned: {o_bin.log_bins[TimeSpectraKeys.file_index_array]}")
        self.logger.info(f"-> tof_array_binned: {o_bin.log_bins[TimeSpectraKeys.tof_array]}")
        self.logger.info(f"-> lambda_array_binned: {o_bin.log_bins[TimeSpectraKeys.lambda_array]}")

        self.parent.log_bins = {TimeSpectraKeys.file_index_array: o_bin.get_log_file_index(),
                                TimeSpectraKeys.tof_array       : o_bin.get_log_tof(),
                                TimeSpectraKeys.lambda_array    : o_bin.get_log_lambda()}

        self.fill_auto_table()
        self.update_auto_table()
        self.refresh_auto_tab()

        self.parent.ui.auto_log_file_index_spinBox.blockSignals(False)
        self.parent.ui.auto_log_tof_doubleSpinBox.blockSignals(False)
        self.parent.ui.auto_log_lambda_doubleSpinBox.blockSignals(False)

    def fill_auto_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
        o_table.remove_all_rows()

        o_get = Get(parent=self.parent)
        bin_auto_mode = o_get.bin_auto_mode()

        if bin_auto_mode == BinAutoMode.linear:
            bins = self.parent.linear_bins
        else:
            bins = self.parent.log_bins

        list_rows = np.arange(len(bins[TimeSpectraKeys.file_index_array]))

        file_index_array_of_bins = bins[TimeSpectraKeys.file_index_array]
        tof_array_of_bins = bins[TimeSpectraKeys.tof_array]
        lambda_array_of_bins = bins[TimeSpectraKeys.lambda_array]

        for _row in np.arange(len(list_rows)):

            file_bin = file_index_array_of_bins[_row]
            tof_bin = tof_array_of_bins[_row]
            lambda_bin = lambda_array_of_bins[_row]

            checkbox_enabled = True
            if not file_bin:
                str_file_index = "N/A"
                str_tof = "N/A"
                str_lambda = "N/A"
                checkbox_enabled = False

            elif len(file_bin) == 1:
                str_file_index = file_bin[0]
                str_tof = f"{tof_bin[0] * TO_MICROS_UNITS: .2f}"
                str_lambda = f"{lambda_bin[0] * TO_ANGSTROMS_UNITS: .3f}"

            elif len(file_bin) == 2:
                str_file_index = f"{file_bin[0]}, {file_bin[1]}"
                str_tof = f"{tof_bin[0] * TO_MICROS_UNITS:.2f}, " \
                          f"{tof_bin[1] * TO_MICROS_UNITS:.2f}"
                str_lambda = f"{lambda_bin[0] * TO_ANGSTROMS_UNITS:.3f}, " \
                             f"{lambda_bin[1] * TO_ANGSTROMS_UNITS:.3f}"

            else:
                str_file_index = f"{file_bin[0]} ... {file_bin[-1]}"
                str_tof = f"{tof_bin[0] * TO_MICROS_UNITS:.2f} ... " \
                          f"{tof_bin[-1] * TO_MICROS_UNITS:.2f}"
                str_lambda = f"{lambda_bin[0] * TO_ANGSTROMS_UNITS:.3f} ... " \
                             f"{lambda_bin[-1] * TO_ANGSTROMS_UNITS:.3f}"

            o_table.insert_empty_row(row=_row)

            # use or not that bin
            if checkbox_enabled:
                checkbox = QCheckBox()
                checkbox.setChecked(True)
                checkbox.stateChanged.connect(lambda state=0,
                                              row=_row: self.parent.auto_table_use_checkbox_changed(state, row))
                o_table.insert_widget(row=_row, column=0, widget=checkbox, centered=True)

            o_table.insert_item(row=_row, column=1, value=_row, editable=False)
            o_table.insert_item(row=_row, column=2, value=str_file_index, editable=False)
            o_table.insert_item(row=_row, column=3, value=str_tof, editable=False)
            o_table.insert_item(row=_row, column=4, value=str_lambda, editable=False)
    #
    # def bin_auto_linear_changed(self, source_radio_button=TimeSpectraKeys.file_index_array):
    #     self.logger.info(f"bin auto linear changed: radio button changed -> {source_radio_button}")
    #     o_bin = LinearBin(parent=self.parent,
    #                       source_array=source_radio_button)
    #     self.parent.ui.auto_linear_file_index_spinBox.blockSignals(True)
    #     self.parent.ui.auto_linear_tof_doubleSpinBox.blockSignals(True)
    #     self.parent.ui.auto_linear_lambda_doubleSpinBox.blockSignals(True)
    #
    #     self.logger.info(f"-> raw_file_index_array_binned: {self.parent.time_spectra[TimeSpectraKeys.file_index_array]}")
    #     self.logger.info(f"-> raw_tof_array_binned: {self.parent.time_spectra[TimeSpectraKeys.tof_array]}")
    #     self.logger.info(f"-> raw_lambda_array_binned: {self.parent.time_spectra[TimeSpectraKeys.lambda_array]}")
    #
    #     if source_radio_button == TimeSpectraKeys.file_index_array:
    #         file_index_value = self.parent.ui.auto_linear_file_index_spinBox.value()
    #         self.logger.info(f"--> bin requested: {file_index_value}")
    #         o_bin.create_linear_file_index_bin_array(bin_value=file_index_value)
    #         o_bin.create_linear_bin_arrays()
    #
    #     elif source_radio_button == TimeSpectraKeys.tof_array:
    #         tof_value = self.parent.ui.auto_linear_tof_doubleSpinBox.value()
    #         self.logger.info(f"--> bin requested: {tof_value}")
    #         o_bin.create_linear_file_index_bin_array(bin_value=tof_value * 1e-6)   # to switch to seconds
    #         o_bin.create_linear_bin_arrays()
    #
    #     elif source_radio_button == TimeSpectraKeys.lambda_array:
    #         lambda_value = self.parent.ui.auto_linear_lambda_doubleSpinBox.value()
    #         self.logger.info(f"--> bin requested: {lambda_value}")
    #         o_bin.create_linear_file_index_bin_array(bin_value=lambda_value * 1e-10)   # to switch to seconds
    #         o_bin.create_linear_bin_arrays()
    #
    #     else:
    #         raise NotImplementedError("bin auto linear algorithm not implemented!")
    #
    #     self.logger.info(f"-> file_index_array_binned: {o_bin.linear_bins[TimeSpectraKeys.file_index_array]}")
    #     self.logger.info(f"-> tof_array_binned: {o_bin.linear_bins[TimeSpectraKeys.tof_array]}")
    #     self.logger.info(f"-> lambda_array_binned: {o_bin.linear_bins[TimeSpectraKeys.lambda_array]}")
    #
    #     self.parent.linear_bins = {TimeSpectraKeys.file_index_array: o_bin.get_linear_file_index(),
    #                                TimeSpectraKeys.tof_array: o_bin.get_linear_tof(),
    #                                TimeSpectraKeys.lambda_array: o_bin.get_linear_lambda()}
    #
    #     self.fill_auto_table()
    #     self.refresh_auto_tab()
    #
    #     show_status_message(parent=self.parent,
    #                         message=f"New {source_radio_button} bin size selected!",
    #                         status=StatusMessageStatus.ready,
    #                         duration_s=5)
    #
    #     self.parent.ui.auto_linear_file_index_spinBox.blockSignals(False)
    #     self.parent.ui.auto_linear_tof_doubleSpinBox.blockSignals(False)
    #     self.parent.ui.auto_linear_lambda_doubleSpinBox.blockSignals(False)

    def update_auto_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
        nbr_rows = o_table.row_count()

        if self.parent.ui.bin_auto_hide_empty_bins_checkBox.isChecked():
            for _row in np.arange(nbr_rows):
                item = o_table.get_item_str_from_cell(row=_row,
                                                      column=2)
                if item == "N/A":
                    o_table.set_row_hidden(_row, True)

        else:
            for _row in np.arange(nbr_rows):
                o_table.set_row_hidden(_row, False)

    # def use_auto_bin_state_changed(self, row=0, state=True):
    #     """
    #     user change the state of any of the bin checkbox
    #     :param row:
    #     :param state: True or False
    #     """
    #     o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
    #     rows_selected = o_table.get_rows_of_table_selected()
    #
    #     if row in rows_selected:
    #
    #         for _row in rows_selected:
    #             item = self.parent.dict_of_bins_item.get(_row, None)
    #             if item:
    #
    #                 if state:
    #                     self.parent.bin_profile_view.addItem(item)
    #                 else:
    #                     self.parent.bin_profile_view.removeItem(item)
    #
    #                 widget = o_table.get_widget(row=_row, column=0)
    #                 if widget:
    #                     checkbox = widget.children()[1]
    #                     if state:
    #                         checkbox.setChecked(2)
    #                     else:
    #                         checkbox.setChecked(0)
    #
    #     else:
    #
    #         item = self.parent.dict_of_bins_item.get(row, None)
    #         if item:
    #
    #             if state:
    #                 self.parent.bin_profile_view.addItem(item)
    #             else:
    #                 self.parent.bin_profile_view.removeItem(item)
    #
    # def auto_table_right_click(self, position=None):
    #     menu = QMenu(self.parent)
    #
    #     select_all = menu.addAction("Select all bins")
    #     unselect_all = menu.addAction("Unselect all bins")
    #
    #     action = menu.exec_(QtGui.QCursor.pos())
    #     if action == select_all:
    #         self.all_auto_bins_checkbox(state=True)
    #     elif action == unselect_all:
    #         self.all_auto_bins_checkbox(state=False)
    #     else:
    #         pass
    #
    # def all_auto_bins_checkbox(self, state=True):
    #     o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
    #     nbr_rows = o_table.row_count()
    #     for _row in np.arange(nbr_rows):
    #         widget = o_table.get_widget(row=_row, column=0)
    #         if widget:
    #             checkbox = widget.children()[1]
    #             checkbox.setChecked(state)
    #             self.use_auto_bin_state_changed(row=_row, state=state)
    #
    # def use_this_bin(self, row=0):
    #     o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
    #     widget = o_table.get_widget(row=row, column=0)
    #     if widget:
    #         checkbox = widget.children()[1]
    #         return checkbox.isChecked()
    #     else:
    #         return False
    #
    # def auto_table_selection_changed(self):
    #     o_get = Get(parent=self.parent)
    #     if o_get.bin_auto_mode() == BinAutoMode.linear:
    #         previous_rows_highlighted = self.parent.linear_bins_selected
    #     else:
    #         previous_rows_highlighted = self.parent.log_bins_selected
    #
    #     if previous_rows_highlighted:
    #         for _row in previous_rows_highlighted:
    #             previous_item = self.parent.dict_of_bins_item.get(_row, None)
    #             if previous_item:
    #                 self.parent.bin_profile_view.removeItem(previous_item)
    #                 previous_item.setBrush(pg.mkBrush(UNSELECTED_BIN))
    #                 if self.use_this_bin(row=_row):
    #                     self.parent.bin_profile_view.addItem(previous_item)
    #
    #     o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
    #     new_rows_to_highlight = o_table.get_rows_of_table_selected()
    #     clean_list_of_new_rows_to_highlight = []  # removing rows that can not be selected (empty bins)
    #     for _row in new_rows_to_highlight:
    #         new_item = self.parent.dict_of_bins_item.get(_row, None)
    #         if new_item:
    #             self.parent.bin_profile_view.removeItem(new_item)
    #             new_item.setBrush(pg.mkBrush(SELECTED_BIN))
    #             self.parent.bin_profile_view.addItem(new_item)
    #             clean_list_of_new_rows_to_highlight.append(_row)
    #
    #     self.parent.current_auto_bin_rows_highlighted = clean_list_of_new_rows_to_highlight
    #
    #     if o_get.bin_auto_mode() == BinAutoMode.linear:
    #         self.parent.linear_bins_selected = clean_list_of_new_rows_to_highlight
    #     else:
    #         self.parent.log_bins_selected = clean_list_of_new_rows_to_highlight
    #
    # def clear_selection(self, auto_mode=BinAutoMode.linear):
    #     if auto_mode == BinAutoMode.linear:
    #         self.parent.linear_bins_selected = None
    #     else:
    #         self.parent.log_bins_selected = None
    #     o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
    #     o_table.select_everything(False)
