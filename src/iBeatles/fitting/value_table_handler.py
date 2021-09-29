from qtpy.QtWidgets import QMenu, QApplication
from qtpy import QtCore, QtGui
import numpy as np

from ..table_dictionary.table_dictionary_handler import TableDictionaryHandler
from .export_fitting_handler import ExportFittingHandler
from .advanced_selection_launcher import AdvancedSelectionLauncher
from .filling_table_handler import FillingTableHandler
from .set_fitting_variables_launcher import SetFittingVariablesLauncher


class ValueTableHandler(object):
    __advanced_selection = None
    __set_variables = None
    __select_all = None
    __unselect_all = None
    __reset = None
    __fixed = None
    __unfixed = None
    __export = None
    __import = None

    def __init__(self, grand_parent=None, parent=None):
        self.grand_parent = grand_parent
        self.parent = parent

    def right_click(self, position):
        menu = QMenu(self.grand_parent)

        if (len(self.grand_parent.fitting_ui.data) == 0) or \
                (self.grand_parent.binning_line_view['pos'] is None):
            status = False
        else:
            status = True

        self.__select_all = menu.addAction("Select All")
        self.__select_all.setEnabled(status)
        self.__unselect_all = menu.addAction("Unselect All")
        self.__unselect_all.setEnabled(status)
        menu.addSeparator()

        self.__advanced_selection = menu.addAction("Selection/Lock Tool ...")
        self.__advanced_selection.setEnabled(status)

        self.__set_variables = menu.addAction("Variables Advanced Tool ...")
        self.__set_variables.setEnabled(status)

        menu.addSeparator()

        self.__fixed = menu.addAction("Fixed Variables Selected")
        self.__fixed.setEnabled(status)

        self.__unfixed = menu.addAction("Unfixed Variables Selected")
        self.__unfixed.setEnabled(status)

        menu.addSeparator()

        self.__export = menu.addAction("Export Table ...")
        self.__export.setEnabled(False)
        self.__import = menu.addAction("Import Table ...")
        self.__import.setEnabled(False)

        menu.addSeparator()

        self.__export_fitting = menu.addAction("Export Fitting ...")

        # _reset = menu.addAction("Full Reset")
        # _reset.setEnabled(status)
        # _reset.setEnabled(False) #remove once implemented

        action = menu.exec_(QtGui.QCursor.pos())
        if action is None:
            return

        funct = self.select_action(action)
        if funct is not None:
            funct()

    def select_action(self, action):
        '''function to replace the complext if/elif/else statement
        of right_click().'''
        return {
            self.__select_all: self.select_all,
            self.__unselect_all: self.unselect_all,
            self.__advanced_selection: self.advanced_selection,
            self.__set_variables: self.set_variables,
            self.__reset: self.reset,
            self.__unfixed: self.unfixed_variables,
            self.__export: self.export_table,
            self.__import: self.import_table,
            self.__export_fitting: self.export_fitting,
        }.get(action, lambda: None)()

    def export_fitting(self):
        o_export_fitting = ExportFittingHandler(grand_parent=self.grand_parent)
        o_export_fitting.run()

    def export_table(self):
        o_table = TableDictionaryHandler(grand_parent=self.grand_parent)
        o_table.export_table()

    def import_table(self):
        o_table = TableDictionaryHandler(grand_parent=self.grand_parent)
        o_table.import_table()

    def changed_fixed_variables_status(self, status=True):
        selection = self.parent.ui.value_table.selectedRanges()
        nbr_row = self.parent.ui.value_table.rowCount()

        o_fill_table = FillingTableHandler(grand_parent=self.grand_parent)
        row_to_show_status = o_fill_table.get_row_to_show_state()

        table_dictionary = self.grand_parent.table_dictionary

        column_variable_match = {5: 'd_spacing',
                                 7: 'sigma',
                                 9: 'alpha',
                                 11: 'a1',
                                 13: 'a2',
                                 15: 'a5',
                                 17: 'a7',
                                 }

        for _select in selection:
            left_column = _select.leftColumn()
            right_column = _select.rightColumn()
            col_range = np.arange(left_column, right_column + 1)
            for _col in col_range:

                if _col < 5:
                    continue

                # only work with even col number
                if (_col % 2) == 0:
                    continue

                name_variable = column_variable_match.get(_col)

                for _index in np.arange(nbr_row):

                    _entry = table_dictionary[str(_index)]
                    if _entry['lock']:
                        continue

                    if row_to_show_status == 'all':

                        _entry[name_variable]['fixed'] = status
                        table_dictionary[str(_index)] = _entry

                    elif row_to_show_status == 'active':

                        if _entry['active']:
                            _entry[name_variable]['fixed'] = status
                            table_dictionary[str(_index)] = _entry

            self.grand_parent.table_dictionary = table_dictionary

            o_fitting = FillingTableHandler(grand_parent=self.grand_parent)
            o_fitting.fill_table()

    def fixed_variables(self):
        self.changed_fixed_variables_status(status=True)

    def unfixed_variables(self):
        self.changed_fixed_variables_status(status=False)

    def select_all(self):
        # QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        o_table = TableDictionaryHandler(grand_parent=self.grand_parent)
        o_table.select_full_table()

        # o_fitting = FillingTableHandler(grand_parent=self.grand_parent)
        # o_fitting.fill_table()
        #
        # self.grand_parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)
        #
        # # if self.grand_parent.advanced_selection_ui:
        # # self.grand_parent.advanced_selection_ui.ui.selection_table.blockSignals(True)
        #
        # # nbr_row = self.grand_parent.fitting_ui.ui.value_table.rowCount()
        # # nbr_column = self.grand_parent.fitting_ui.ui.value_table.columnCount()
        # # _selection_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_column-1)
        # # self.grand_parent.fitting_ui.ui.value_table.setRangeSelected(_selection_range, True)
        # # o_fitting = FillingTableHandler(grand_parent=self.grand_parent)
        # # o_fitting.select_full_table()
        #
        # #        self.grand_parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)
        # if self.grand_parent.advanced_selection_ui:
        #     self.grand_parent.advanced_selection_ui.ui.selection_table.blockSignals(False)

        # QApplication.restoreOverrideCursor()

    def unselect_all(self):

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        o_table = TableDictionaryHandler(grand_parent=self.grand_parent)
        o_table.unselect_full_table()

        o_fitting = FillingTableHandler(grand_parent=self.grand_parent)
        o_fitting.fill_table()

        self.grand_parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)

        # if self.grand_parent.advanced_selection_ui:
        # self.grand_parent.advanced_selection_ui.ui.selection_table.blockSignals(True)
        # nbr_row = self.grand_parent.fitting_ui.ui.value_table.rowCount()
        # nbr_column = self.grand_parent.fitting_ui.ui.value_table.columnCount()
        # _selection_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_column-1)
        # self.grand_parent.fitting_ui.ui.value_table.setRangeSelected(_selection_range, False)
        # o_fitting = FillingTableHandler(grand_parent=self.grand_parent)
        # o_fitting.unselect_full_table()
        # self.grand_parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)
        # if self.grand_parent.advanced_selection_ui:
        # self.grand_parent.advanced_selection_ui.ui.selection_table.blockSignals(False)

        QApplication.restoreOverrideCursor()

    def advanced_selection(self):
        AdvancedSelectionLauncher(grand_parent=self.grand_parent)

    def set_variables(self):
        SetFittingVariablesLauncher(grand_parent=self.grand_parent)

    def reset(self):
        print("reset")
