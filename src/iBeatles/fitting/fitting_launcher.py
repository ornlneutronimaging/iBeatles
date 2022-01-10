from qtpy.QtWidgets import QMainWindow, QApplication, QTableWidgetSelectionRange
from qtpy import QtCore
import numpy as np
import logging

from ..utilities.table_handler import TableHandler
from .. import load_ui
from .. import DataType

from .fitting_handler import FittingHandler
from .value_table_handler import ValueTableHandler
from .selected_bin_handler import SelectedBinsHandler
from ..table_dictionary.table_dictionary_handler import TableDictionaryHandler
from .filling_table_handler import FillingTableHandler
from .fitting_initialization_handler import FittingInitializationHandler
from .create_fitting_story_launcher import CreateFittingStoryLauncher
from .initialization import Initialization
from .event_handler import EventHandler


class FittingLauncher(object):

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.fitting_ui is None:
            fitting_window = FittingWindow(parent=parent)
            fitting_window.show()
            self.parent.fitting_ui = fitting_window
            o_fitting = FittingHandler(grand_parent=self.parent,
                                       parent=self.parent.fitting_ui)
            o_fitting.display_image()
            o_fitting.display_roi()
            o_fitting.fill_table()
            fitting_window.check_advanced_table_status()
        else:
            self.parent.fitting_ui.setFocus()
            self.parent.fitting_ui.activateWindow()


class FittingWindow(QMainWindow):

    fitting_lr = None
    is_ready_to_fit = False

    data = []
    # there_is_a_roi = False
    bragg_edge_active_button_status = True  # to make sure active/lock button worked correctly

    list_bins_selected_item = []
    list_bins_locked_item = []

    image_view = None
    bragg_edge_plot = None
    line_view = None

    line_view_fitting = None  # roi selected in binning window
    all_bins_button = None
    indi_bins_button = None

    header_value_tables_match = {0: [0],
                                 1: [1],
                                 2: [2],
                                 3: [3],
                                 4: [4],
                                 5: [5, 6],
                                 6: [7, 8],
                                 7: [9, 10],
                                 8: [11, 12],
                                 9: [13, 14],
                                 10: [15, 16],
                                 11: [17, 18],
                                 12: [19, 20]}

    para_cell_width = 130
    header_table_columns_width = [30, 30, 50, 50, 100,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width]
    fitting_table_columns_width = [header_table_columns_width[0],
                                   header_table_columns_width[1],
                                   header_table_columns_width[2],
                                   header_table_columns_width[3],
                                   header_table_columns_width[4],
                                   np.int(header_table_columns_width[5] / 2),
                                   np.int(header_table_columns_width[5] / 2),
                                   np.int(header_table_columns_width[6] / 2),
                                   np.int(header_table_columns_width[6] / 2),
                                   np.int(header_table_columns_width[7] / 2),
                                   np.int(header_table_columns_width[7] / 2),
                                   np.int(header_table_columns_width[8] / 2),
                                   np.int(header_table_columns_width[8] / 2),
                                   np.int(header_table_columns_width[9] / 2),
                                   np.int(header_table_columns_width[9] / 2),
                                   np.int(header_table_columns_width[10] / 2),
                                   np.int(header_table_columns_width[10] / 2),
                                   np.int(header_table_columns_width[11] / 2),
                                   np.int(header_table_columns_width[11] / 2),
                                   np.int(header_table_columns_width[12] / 2),
                                   np.int(header_table_columns_width[12] / 2)]

    # status of alpha and sigma initialization
    sigma_alpha_initialized = False
    initialization_table = {'d_spacing': np.NaN,
                            'alpha': np.NaN,
                            'sigma': np.NaN,
                            'a1': np.NaN,
                            'a2': np.NaN,
                            'a5': np.NaN,
                            'a6': np.NaN}

    bragg_edge_data = {'x_axis': [],
                       'y_axis': []}

    def __init__(self, parent=None):

        logging.info("Launching fitting tab!")
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_fittingWindow.ui', baseinstance=self)
        self.setWindowTitle("5. Fitting")

        o_init = Initialization(parent=self,
                                grand_parent=self.parent)
        o_init.run_all()

        self.check_status_widgets()
        self.parent.data_metadata[DataType.fitting]['ui_accessed'] = True

    def re_fill_table(self):
        o_fitting = FittingHandler(parent=self,
                                   grand_parent=self.parent)
        o_fitting.fill_table()

    def column_value_table_clicked(self, column):
        '''
        to make sure that if the val or err column is selected, or unselected, the other
        column behave the same
        '''
        if column < 5:
            return

        _item0 = self.parent.fitting_ui.ui.value_table.item(0, column)
        state_column_clicked = self.parent.fitting_ui.ui.value_table.isItemSelected(_item0)

        if column % 2 == 0:
            col1 = column - 1
            col2 = column
        else:
            col1 = column
            col2 = column + 1

        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
        range_selected = QTableWidgetSelectionRange(0, col1, nbr_row - 1, col2)
        self.parent.fitting_ui.ui.value_table.setRangeSelected(range_selected,
                                                               state_column_clicked)

    def column_header_table_clicked(self, column):
        _value_table_column = self.header_value_tables_match.get(column, -1)
        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()

        # if both col already selected, unselect them
        col_already_selected = False
        _item1 = self.parent.fitting_ui.ui.value_table.item(0, _value_table_column[0])
        _item2 = self.parent.fitting_ui.ui.value_table.item(0, _value_table_column[-1])

        if _item1.isSelected() and _item2.isSelected():

        # if self.parent.fitting_ui.ui.value_table.isItemSelected(_item1) and \
        #         self.parent.fitting_ui.ui.value_table.isItemSelected(_item2):
            col_already_selected = True

        if column in [2, 3]:
            selection = self.parent.fitting_ui.ui.value_table.selectedRanges()
            col_already_selected = False
            for _select in selection:
                if column in [_select.leftColumn(), _select.rightColumn()]:
                    col_already_selected = True
                    break

        from_col = _value_table_column[0]
        to_col = _value_table_column[-1]

        range_selected = QTableWidgetSelectionRange(0, from_col,
                                                    nbr_row - 1, to_col)
        self.parent.fitting_ui.ui.value_table.setRangeSelected(range_selected,
                                                               not col_already_selected)

    def resizing_header_table(self, index_column, old_size, new_size):
        if index_column < 5:
            self.ui.value_table.setColumnWidth(index_column, new_size)
        else:
            new_half_size = np.int(new_size / 2)
            index1 = (index_column - 5) * 2 + 5
            index2 = index1 + 1
            self.ui.value_table.setColumnWidth(index1, new_half_size)
            self.ui.value_table.setColumnWidth(index2, new_half_size)

    def resizing_value_table(self, index_column, old_size, new_size):
        if index_column < 5:
            self.ui.header_table.setColumnWidth(index_column, new_size)
        else:
            if (index_column % 2) == 1:
                right_new_size = self.ui.value_table.columnWidth(index_column + 1)
                index_header = np.int(index_column - 5) / 2 + 5
                self.ui.header_table.setColumnWidth(index_header, new_size + right_new_size)

            else:
                left_new_size = self.ui.value_table.columnWidth(index_column - 1)
                index_header = np.int(index_column - 6) / 2 + 5
                self.ui.header_table.setColumnWidth(index_header, new_size + left_new_size)

    def active_button_pressed(self):
        self.parent.display_active_row_flag = True
        self.update_bragg_edge_plot()

    def lock_button_pressed(self):
        self.parent.display_active_row_flag = False
        self.update_bragg_edge_plot()

    def mouse_moved_in_image_view(self):
        self.image_view.setFocus(True)

    def hkl_list_changed(self, hkl):
        bragg_edges_array = self.parent.selected_element_bragg_edges_array
        if bragg_edges_array:
            if str(hkl) == '':
                value = "N/A"
            else:
                hkl_array = self.parent.selected_element_hkl_array
                str_hkl_list = ["{},{},{}".format(_hkl[0], _hkl[1], _hkl[2]) for _hkl in hkl_array]
                hkl_bragg_edges = dict(zip(str_hkl_list, bragg_edges_array))
                value = "{:04.3f}".format(hkl_bragg_edges[str(hkl)])
        else:
            value = "N/A"
        self.ui.bragg_edge_calculated.setText(value)

    def slider_changed(self):
        o_fitting_handler = FittingHandler(parent=self,
                                           grand_parent=self.parent)
        o_fitting_handler.display_roi()

    def check_status_widgets(self):
        self.check_state_of_step3_button()
        self.check_state_of_step4_button()

    def check_state_of_step3_button(self):
        """The step1 button should be enabled if at least one row of the big table
        is activated and display in the 1D plot"""
        o_table = TableDictionaryHandler(parent=self,
                                         grand_parent=self.parent)
        is_at_least_one_row_activated = o_table.is_at_least_one_row_activated()
        self.ui.step3_button.setEnabled(is_at_least_one_row_activated)
        self.ui.step2_instruction_label.setEnabled(is_at_least_one_row_activated)

    def check_state_of_step4_button(self):
        self.ui.step4_button.setEnabled(self.is_ready_to_fit)

    def active_button_state_changed(self, status, row_clicked):
        '''
        status: 0: off
                2: on
        '''
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        update_lock_flag = False
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.ui.selection_table.blockSignals(True)

        # if status == 0:
        #     status = False
        # else:
        #     status = True

        self.mirror_state_of_widgets(column=3, row_clicked=row_clicked)
        self.check_state_of_step3_button()

        # # perform same status on all rows
        # _selection = self.ui.value_table.selectedRanges()
        # _this_column_is_selected = False
        # for _select in _selection:
        #     if 3 in [_select.leftColumn(), _select.rightColumn()]:
        #         _this_column_is_selected = True
        #         break

        # table_dictionary = self.parent.table_dictionary
        # if _this_column_is_selected:
        #     # update_selection_flag = True  # we change the state so we need to update the selection
        #     for _index in table_dictionary:
        #         table_dictionary[_index]['active'] = status
        #         _widget_lock = self.ui.value_table.cellWidget(int(_index), 3)
        #         _widget_lock.blockSignals(True)
        #         _widget_lock.setChecked(status)
        #         _widget_lock.blockSignals(False)
        #         if status:
        #             _widget = self.ui.value_table.cellWidget(int(_index), 2)
        #             if _widget.isChecked():  # because we can not be active and locked at the same time
        #                 table_dictionary[_index]['lock'] = False
        #                 _widget.blockSignals(True)
        #                 _widget.setChecked(False)
        #                 _widget.blockSignals(False)
        # else:
        #     table_dictionary[str(row_clicked)]['active'] = status
        #     if status:
        #         _widget = self.ui.value_table.cellWidget(row_clicked, 2)
        #         if _widget.isChecked():
        #             table_dictionary[str(row_clicked)]['lock'] = False
        #             _widget.blockSignals(True)
        #             _widget.setChecked(False)
        #             _widget.blockSignals(False)
        #             update_lock_flag = True
        #     self.parent.table_dictionary = table_dictionary

        # hide this row if status is False and user only wants to see locked items
        o_filling_handler = FillingTableHandler(grand_parent=self.parent,
                                                parent=self)
        # if (status is False) and (o_filling_handler.get_row_to_show_state() == 'active'):
        #     self.parent.fitting_ui.ui.value_table.hideRow(row_clicked)

        o_bin_handler = SelectedBinsHandler(parent=self,
                                            grand_parent=self.parent)
        o_bin_handler.update_bins_selected()
        self.update_bragg_edge_plot()
        o_bin_handler.update_bins_locked()

        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.update_selection_table()
            if update_lock_flag:
                self.parent.advanced_selection_ui.update_lock_table()
            self.parent.advanced_selection_ui.ui.selection_table.blockSignals(False)

        QApplication.restoreOverrideCursor()

    def mirror_state_of_widgets(self, column=2, row_clicked=0):
        # perform same status on all rows and save it in table_dictionary
        label_column = 'active' if column == 3 else 'lock'

        o_table = TableHandler(table_ui=self.ui.value_table)
        o_table.add_this_row_to_selection(row=row_clicked)
        list_row_selected = o_table.get_rows_of_table_selected()

        o_table_handler = TableDictionaryHandler(grand_parent=self.parent,
                                                 parent=self)
        is_this_row_checked = o_table_handler.is_this_row_checked(row=row_clicked,
                                                                  column=column)

        for _row in list_row_selected:
            self.parent.march_table_dictionary[str(_row)][label_column] = is_this_row_checked
            if _row == row_clicked:
                continue
            _widget = o_table.get_widget(row=_row,
                                         column=column)
            _widget.blockSignals(True)
            _widget.setChecked(is_this_row_checked)
            _widget.blockSignals(False)

    def lock_button_state_changed(self, status, row_clicked):
        """
        All the row selected should mirror the state of this button

        status: 0: off
                2: on
        """
        update_selection_flag = False

        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.ui.lock_table.blockSignals(True)

        if status == 0:
            status = False
        else:
            status = True

        self.mirror_state_of_widgets(column=2, row_clicked=row_clicked)

        # hide this row if status is False and user only wants to see locked items
        o_filling_handler = FillingTableHandler(grand_parent=self.parent,
                                                parent=self)
        if (status is False) and (o_filling_handler.get_row_to_show_state() == 'lock'):
            self.parent.fitting_ui.ui.value_table.hideRow(row_clicked)

        o_bin_handler = SelectedBinsHandler(parent=self,
                                            grand_parent=self.parent)
        o_bin_handler.update_bins_locked()
        self.update_bragg_edge_plot()
        o_bin_handler.update_bins_selected()

        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.update_lock_table()
            if update_selection_flag:
                self.parent.advanced_selection_ui.update_selection_table()
            self.parent.advanced_selection_ui.ui.lock_table.blockSignals(False)

    def value_table_right_click(self, position):
        o_table_handler = ValueTableHandler(grand_parent=self.parent, parent=self)
        o_table_handler.right_click(position=position)

    def update_image_view_selection(self):
        o_bin_handler = SelectedBinsHandler(parent=self, grand_parent=self.parent)
        o_bin_handler.update_bins_selected()

    def update_image_view_lock(self):
        o_bin_handler = SelectedBinsHandler(parent=self, grand_parent=self.parent)
        o_bin_handler.update_bins_locked()

    def update_bragg_edge_plot(self, update_selection=True):
        o_bin_handler = SelectedBinsHandler(parent=self, grand_parent=self.parent)
        o_bin_handler.update_bragg_edge_plot()
        if update_selection:
            self.bragg_edge_linear_region_changing()
        self.check_state_of_step3_button()

    def selection_in_value_table_of_rows_cell_clicked(self, row, column):
        pass
        # # make sure the selection is right (val and err selected at the same time)
        # if column > 4:
        #     _item0 = self.ui.value_table.item(0, column)
        #     _is_selected = self.ui.value_table.isItemSelected(_item0)
        #     if (column % 2) == 0:
        #         left_column = column - 1
        #         right_column = column
        #     else:
        #         left_column = column
        #         right_column = column + 1
        #     nbr_row = self.ui.value_table.rowCount()
        #     _selection = QTableWidgetSelectionRange(0, left_column,
        #                                             nbr_row - 1, right_column)
        #     self.ui.value_table.setRangeSelected(_selection, _is_selected)
        #
        # self.update_bragg_edge_plot()

    def selection_in_value_table_changed(self):
        self.selection_in_value_table_of_rows_cell_clicked(-1, -1)

    def bragg_edge_linear_region_changing(self):
        self.is_ready_to_fit = False
        self.bragg_edge_linear_region_changed()
        self.check_status_widgets()

    def bragg_edge_linear_region_changed(self):
        self.is_ready_to_fit = False
        o_event = EventHandler(parent=self,
                               grand_parent=self.parent)
        o_event.bragg_edge_region_changed()
        self.check_status_widgets()

    def check_advanced_table_status(self):
        self.is_ready_to_fit = False
        button_status = self.ui.advanced_table_checkBox.isChecked()
        self.advanced_table_clicked(button_status)
        self.check_status_widgets()

    def advanced_table_clicked(self, status):
        self.is_ready_to_fit = False
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        o_table_handler = FillingTableHandler(grand_parent=self.parent,
                                              parent=self)
        o_table_handler.set_mode(advanced_mode=status)
        self.check_status_widgets()
        QApplication.restoreOverrideCursor()

    def update_table(self):
        o_filling_table = FillingTableHandler(grand_parent=self.parent,
                                              parent=self)
        self.parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.parent.fitting_ui.ui.value_table.blockSignals(False)

    def min_or_max_lambda_manually_changed(self):
        o_event = EventHandler(parent=self,
                               grand_parent=self.parent)
        o_event.min_or_max_lambda_manually_changed()

    def initialize_all_parameters_button_clicked(self):
        o_initialization = FittingInitializationHandler(parent=self,
                                                        grand_parent=self.parent)
        # o_initialization.make_all_active()
        o_initialization.run()

    def initialize_all_parameters_step2(self):
        o_initialization = FittingInitializationHandler(parent=self,
                                                        grand_parent=self.parent)
        o_initialization.finished_up_initialization()

        # activate or not step4 (yes if we were able to initialize correctly all variables)
        self.ui.step4_button.setEnabled(o_initialization.all_variables_initialized)
        self.ui.step4_label.setEnabled(o_initialization.all_variables_initialized)

        self.update_bragg_edge_plot()

    def create_fitting_story_checked(self):
        CreateFittingStoryLauncher(parent=self,
                                   grand_parent=self.parent)

    # kropff
    def kropff_parameters_changed(self):
        a0 = self.ui.kropff_high_lda_a0_init.text()
        b0 = self.ui.kropff_high_lda_b0_init.text()
        high_tof_graph = 'a0' if self.ui.kropff_a0_radioButton.isChecked() else 'b0'

        ahkl = self.ui.kropff_low_lda_ahkl_init.text()
        bhkl = self.ui.kropff_low_lda_bhkl_init.text()
        low_tof_graph = 'ahkl' if self.ui.kropff_ahkl_radioButton.isChecked() else 'bhkl'

        lambda_hkl = self.ui.kropff_bragg_peak_ldahkl_init.text()
        tau = self.ui.kropff_bragg_peak_tau_init.text()
        sigma = self.ui.kropff_bragg_peak_sigma_comboBox.currentText()
        if self.ui.kropff_lda_hkl_radioButton.isChecked():
            bragg_peak_graph = 'lambda_hkl'
        elif self.ui.kropff_tau_radioButton.isChecked():
            bragg_peak_graph = 'tau'
        else:
            bragg_peak_graph = 'sigma'
        if self.ui.kropff_bragg_peak_single_selection.isChecked():
            bragg_peak_table_selection = 'single'
        else:
            bragg_peak_table_selection = 'multi'

        self.parent.session_dict[DataType.fitting]['kropff']['high tof']['a0'] = a0
        self.parent.session_dict[DataType.fitting]['kropff']['high tof']['b0'] = b0
        self.parent.session_dict[DataType.fitting]['kropff']['high tof']['graph'] = high_tof_graph

        self.parent.session_dict[DataType.fitting]['kropff']['low tof']['ahkl'] = ahkl
        self.parent.session_dict[DataType.fitting]['kropff']['low tof']['bhkl'] = bhkl
        self.parent.session_dict[DataType.fitting]['kropff']['low tof']['graph'] = low_tof_graph

        self.parent.session_dict[DataType.fitting]['kropff']['bragg peak']['lambda_hkl'] = lambda_hkl
        self.parent.session_dict[DataType.fitting]['kropff']['bragg peak']['tau'] = tau
        self.parent.session_dict[DataType.fitting]['kropff']['bragg peak']['sigma'] = sigma
        self.parent.session_dict[DataType.fitting]['kropff']['bragg peak']['graph'] = bragg_peak_graph
        self.parent.session_dict[DataType.fitting]['kropff']['bragg peak']['table selection'] = \
            bragg_peak_table_selection

    def kropff_bragg_peak_selection_mode_changed(self):
        if self.ui.kropff_bragg_peak_single_selection.isChecked():
            self.ui.bragg_edge_tableWidget.setSelectionMode(1)
        else:
            self.ui.bragg_edge_tableWidget.setSelectionMode(2)
        self.update_kropff_fitting_plot()

    def update_kropff_fitting_plot(self):
        pass

    def kropff_parameters_changed_with_string(self, string):
        self.kropff_parameters_changed()

    def windows_settings(self):
        self.parent.session_dict[DataType.fitting]['ui']['splitter_2'] = self.ui.splitter_2.sizes()
        self.parent.session_dict[DataType.fitting]['ui']['splitter'] = self.ui.splitter.sizes()
        self.parent.session_dict[DataType.fitting]['ui']['splitter_3'] = self.ui.splitter_3.sizes()

    def save_all_parameters(self):
        self.kropff_parameters_changed()
        self.windows_settings()

    def closeEvent(self, event=None):
        self.save_all_parameters()
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.close()
        if self.parent.fitting_set_variables_ui:
            self.parent.fitting_set_variables_ui.close()
        self.parent.fitting_ui = None
