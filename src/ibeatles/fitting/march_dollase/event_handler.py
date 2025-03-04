from qtpy.QtWidgets import QTableWidgetSelectionRange, QApplication
from qtpy import QtCore

from src.ibeatles.table_dictionary.table_dictionary_handler import (
    TableDictionaryHandler,
)
from src.ibeatles.fitting.selected_bin_handler import SelectedBinsHandler
from src.ibeatles.utilities.table_handler import TableHandler
from src.ibeatles.fitting.filling_table_handler import FillingTableHandler


class EventHandler:
    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def column_value_table_clicked(self, column):
        """
        to make sure that if the val or err column is selected, or unselected, the other
        column behave the same
        """
        if column < 5:
            return

        _item0 = self.grand_parent.fitting_ui.ui.value_table.item(0, column)
        state_column_clicked = (
            self.grand_parent.fitting_ui.ui.value_table.isItemSelected(_item0)
        )

        if column % 2 == 0:
            col1 = column - 1
            col2 = column
        else:
            col1 = column
            col2 = column + 1

        nbr_row = self.grand_parent.fitting_ui.ui.value_table.rowCount()
        range_selected = QTableWidgetSelectionRange(0, col1, nbr_row - 1, col2)
        self.grand_parent.fitting_ui.ui.value_table.setRangeSelected(
            range_selected, state_column_clicked
        )

    def column_header_table_clicked(self, column):
        _value_table_column = self.parent.header_value_tables_match.get(column, -1)
        nbr_row = self.grand_parent.fitting_ui.ui.value_table.rowCount()

        # if both col already selected, unselect them
        col_already_selected = False
        _item1 = self.grand_parent.fitting_ui.ui.value_table.item(
            0, _value_table_column[0]
        )
        _item2 = self.grand_parent.fitting_ui.ui.value_table.item(
            0, _value_table_column[-1]
        )

        if _item1.isSelected() and _item2.isSelected():
            col_already_selected = True

        if column in [2, 3]:
            selection = self.grand_parent.fitting_ui.ui.value_table.selectedRanges()
            col_already_selected = False
            for _select in selection:
                if column in [_select.leftColumn(), _select.rightColumn()]:
                    col_already_selected = True
                    break

        from_col = _value_table_column[0]
        to_col = _value_table_column[-1]

        range_selected = QTableWidgetSelectionRange(0, from_col, nbr_row - 1, to_col)
        self.grand_parent.fitting_ui.ui.value_table.setRangeSelected(
            range_selected, not col_already_selected
        )

    def resizing_header_table(self, index_column, new_size):
        if index_column < 5:
            self.parent.ui.value_table.setColumnWidth(index_column, new_size)
        else:
            new_half_size = int(new_size / 2)
            index1 = (index_column - 5) * 2 + 5
            index2 = index1 + 1
            self.parent.ui.value_table.setColumnWidth(index1, new_half_size)
            self.parent.ui.value_table.setColumnWidth(index2, new_half_size)

    def resizing_value_table(self, index_column, new_size):
        if index_column < 5:
            self.parent.ui.header_table.setColumnWidth(index_column, new_size)
        else:
            if (index_column % 2) == 1:
                right_new_size = self.parent.ui.value_table.columnWidth(
                    index_column + 1
                )
                index_header = int(index_column - 5) / 2 + 5
                self.parent.ui.header_table.setColumnWidth(
                    index_header, new_size + right_new_size
                )

            else:
                left_new_size = self.parent.ui.value_table.columnWidth(index_column - 1)
                index_header = int(index_column - 6) / 2 + 5
                self.parent.ui.header_table.setColumnWidth(
                    index_header, new_size + left_new_size
                )

    def check_state_of_step3_button(self):
        """The step1 button should be enabled if at least one row of the big table
        is activated and display in the 1D plot"""
        o_table = TableDictionaryHandler(
            parent=self.parent, grand_parent=self.grand_parent
        )
        is_at_least_one_row_activated = o_table.is_at_least_one_row_activated()
        self.parent.ui.step3_button.setEnabled(is_at_least_one_row_activated)
        self.parent.ui.step2_instruction_label.setEnabled(is_at_least_one_row_activated)

    def check_state_of_step4_button(self):
        self.parent.ui.step4_button.setEnabled(self.parent.is_ready_to_fit)

    def active_button_state_changed(self, row_clicked):
        """
        status: 0: off
                2: on
        """
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        update_lock_flag = False
        if self.grand_parent.advanced_selection_ui:
            self.grand_parent.advanced_selection_ui.ui.selection_table.blockSignals(
                True
            )

        self.parent.mirror_state_of_widgets(column=3, row_clicked=row_clicked)
        self.check_state_of_step3_button()

        o_bin_handler = SelectedBinsHandler(
            parent=self.parent, grand_parent=self.grand_parent
        )
        o_bin_handler.update_bins_selected()
        self.parent.update_bragg_edge_plot()
        o_bin_handler.update_bins_locked()

        if self.grand_parent.advanced_selection_ui:
            self.grand_parent.advanced_selection_ui.update_selection_table()
            if update_lock_flag:
                self.grand_parent.advanced_selection_ui.update_lock_table()
            self.grand_parent.advanced_selection_ui.ui.selection_table.blockSignals(
                False
            )

        QApplication.restoreOverrideCursor()

    def mirror_state_of_widgets(self, column=2, row_clicked=0):
        # perform same status on all rows and save it in table_dictionary
        label_column = "active" if column == 3 else "lock"

        o_table = TableHandler(table_ui=self.parent.ui.value_table)
        o_table.add_this_row_to_selection(row=row_clicked)
        list_row_selected = o_table.get_rows_of_table_selected()

        o_table_handler = TableDictionaryHandler(
            grand_parent=self.grand_parent, parent=self.parent
        )
        is_this_row_checked = o_table_handler.is_this_row_checked(
            row=row_clicked, column=column
        )

        for _row in list_row_selected:
            self.grand_parent.march_table_dictionary[str(_row)][label_column] = (
                is_this_row_checked
            )
            if _row == row_clicked:
                continue
            _widget = o_table.get_widget(row=_row, column=column)
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

        if self.grand_parent.advanced_selection_ui:
            self.grand_parent.advanced_selection_ui.ui.lock_table.blockSignals(True)

        if status == 0:
            status = False
        else:
            status = True

        self.mirror_state_of_widgets(column=2, row_clicked=row_clicked)

        # hide this row if status is False and user only wants to see locked items
        o_filling_handler = FillingTableHandler(
            grand_parent=self.grand_parent, parent=self.parent
        )
        if (status is False) and (o_filling_handler.get_row_to_show_state() == "lock"):
            self.grand_parent.fitting_ui.ui.value_table.hideRow(row_clicked)

        o_bin_handler = SelectedBinsHandler(
            parent=self.parent, grand_parent=self.grand_parent
        )
        o_bin_handler.update_bins_locked()
        self.parent.update_bragg_edge_plot()
        o_bin_handler.update_bins_selected()

        if self.grand_parent.advanced_selection_ui:
            self.grand_parent.advanced_selection_ui.update_lock_table()
            if update_selection_flag:
                self.grand_parent.advanced_selection_ui.update_selection_table()
            self.grand_parent.advanced_selection_ui.ui.lock_table.blockSignals(False)

    def update_image_view_selection(self):
        o_bin_handler = SelectedBinsHandler(
            parent=self.parent, grand_parent=self.grand_parent
        )
        o_bin_handler.update_bins_selected()

    def update_image_view_lock(self):
        o_bin_handler = SelectedBinsHandler(
            parent=self.parent, grand_parent=self.grand_parent
        )
        o_bin_handler.update_bins_locked()
