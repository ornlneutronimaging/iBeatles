from qtpy.QtWidgets import QTableWidgetSelectionRange, QMainWindow, QApplication
from qtpy import QtCore
import numpy as np

# from iBeatles.py.interfaces.ui_advancedFittingSelection import Ui_MainWindow as UiMainWindow
from iBeatles.fitting.filling_table_handler import FillingTableHandler
from iBeatles import load_ui
from iBeatles.fitting.march_dollase.event_handler import EventHandler


class AdvancedSelectionLauncher(object):

    def __init__(self, grand_parent=None, parent=None):
        self.grand_parent = grand_parent
        self.parent = parent

        if self.grand_parent.advanced_selection_ui is None:
            advanced_window = AdvancedSelectionWindow(grand_parent=grand_parent,
                                                      parent=parent)
            self.grand_parent.advanced_selection_ui = advanced_window
            advanced_window.show()
        else:
            self.grand_parent.advanced_selection_ui.setFocus()
            self.grand_parent.advanced_selection_ui.activateWindow()


class AdvancedSelectionWindow(QMainWindow):

    def __init__(self, grand_parent=None, parent=None):

        self.grand_parent = grand_parent
        self.parent = parent
        QMainWindow.__init__(self, parent=grand_parent)
        self.ui = load_ui('ui_advancedFittingSelection.ui', baseinstance=self)
        self.setWindowTitle("Graphical Selection Tool")

        self.ui.selection_table.blockSignals(True)
        self.ui.lock_table.blockSignals(True)
        self.init_table()
        self.ui.selection_table.blockSignals(False)
        self.ui.lock_table.blockSignals(False)

    def init_table(self):
        fitting_selection = self.grand_parent.fitting_selection
        nbr_row = fitting_selection['nbr_row']
        nbr_column = fitting_selection['nbr_column']

        # selection table
        self.ui.selection_table.setColumnCount(nbr_column)
        self.ui.selection_table.setRowCount(nbr_row)
        self.update_selection_table()

        # lock table
        self.ui.lock_table.setColumnCount(nbr_column)
        self.ui.lock_table.setRowCount(nbr_row)
        self.update_lock_table()

        # set size of cells
        value = np.int(self.ui.advanced_selection_cell_size_slider.value())
        self.selection_cell_size_changed(value)

    def update_selection_table(self):
        self.update_table(state_field='active',
                          table_ui=self.ui.selection_table)

    def update_lock_table(self):
        self.update_table(state_field='lock',
                          table_ui=self.ui.lock_table)

    def update_table(self, state_field='', table_ui=None):
        table_dictionary = self.grand_parent.march_table_dictionary

        for _index in table_dictionary:
            _entry = table_dictionary[_index]
            state = _entry[state_field]
            row_index = _entry['row_index']
            column_index = _entry['column_index']
            _selection = QTableWidgetSelectionRange(row_index, column_index,
                                                    row_index, column_index)
            table_ui.setRangeSelected(_selection, state)

    def selection_cell_size_changed(self, value):
        nbr_row = self.ui.selection_table.rowCount()
        nbr_column = self.ui.selection_table.columnCount()

        for _row in np.arange(nbr_row):
            self.ui.selection_table.setRowHeight(_row, value)
            self.ui.lock_table.setRowHeight(_row, value)

        for _col in np.arange(nbr_column):
            self.ui.selection_table.setColumnWidth(_col, value)
            self.ui.lock_table.setColumnWidth(_col, value)

    def selection_table_selection_changed(self):

        # update table and then update GUI
        selection = self.ui.selection_table.selectedRanges()
        nbr_row = self.ui.selection_table.rowCount()

        table_dictionary = self.grand_parent.march_table_dictionary

        for _entry in table_dictionary.keys():
            table_dictionary[_entry]['active'] = False

        for _select in selection:
            top_row = _select.topRow()
            left_col = _select.leftColumn()
            bottom_row = _select.bottomRow()
            right_col = _select.rightColumn()
            for _row in np.arange(top_row, bottom_row + 1):
                for _col in np.arange(left_col, right_col + 1):
                    fitting_row = _col * nbr_row + _row
                    _entry = table_dictionary[str(fitting_row)]
                    _entry['active'] = True
                    table_dictionary[str(fitting_row)] = _entry

        self.grand_parent.march_table_dictionary = table_dictionary
        o_filling_table = FillingTableHandler(grand_parent=self.grand_parent,
                                              parent=self.parent)

        self.grand_parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.grand_parent.fitting_ui.ui.value_table.blockSignals(False)

        o_event = EventHandler(parent=self.parent,
                               grand_parent=self.grand_parent)
        o_event.update_image_view_selection()

        self.grand_parent.fitting_ui.update_bragg_edge_plot()

    def lock_table_selection_changed(self):
        # update table and then update GUI
        selection = self.ui.lock_table.selectedRanges()
        nbr_row = self.ui.lock_table.rowCount()

        table_dictionary = self.grand_parent.march_table_dictionary

        for _entry in table_dictionary.keys():
            table_dictionary[_entry]['lock'] = False

        for _select in selection:
            top_row = _select.topRow()
            left_col = _select.leftColumn()
            bottom_row = _select.bottomRow()
            right_col = _select.rightColumn()
            for _row in np.arange(top_row, bottom_row + 1):
                for _col in np.arange(left_col, right_col + 1):
                    fitting_row = _col * nbr_row + _row
                    _entry = table_dictionary[str(fitting_row)]
                    _entry['lock'] = True
                    table_dictionary[str(fitting_row)] = _entry

        self.grand_parent.march_table_dictionary = table_dictionary
        o_filling_table = FillingTableHandler(grand_parent=self.grand_parent,
                                              parent=self.parent)

        self.grand_parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.grand_parent.fitting_ui.ui.value_table.blockSignals(False)

        o_event = EventHandler(parent=self.parent,
                               grand_parent=self.grand_parent)
        o_event.update_image_view_lock()

        self.grand_parent.fitting_ui.update_bragg_edge_plot()

        if self.grand_parent.fitting_set_variables_ui:
            self.grand_parent.fitting_set_variables_ui.update_table()

    def closeEvent(self, event=None):
        self.grand_parent.advanced_selection_ui = None

    def apply_button_clicked(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        if self.ui.tabWidget.currentIndex() == 0:
            self.selection_table_selection_changed()
        else:
            self.lock_table_selection_changed()
        QApplication.restoreOverrideCursor()
