from PyQt4 import QtGui

from ibeatles.fitting.advanced_selection_launcher import AdvancedSelectionLauncher
from ibeatles.fitting.filling_table_handler import FillingTableHandler


class ValueTableHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def right_click(self, position):
        menu = QtGui.QMenu(self.parent)
        
        _select_all = menu.addAction("Select All")
        _unselect_all = menu.addAction("Unselect All")
        menu.addSeparator()
        _advanced_selection = menu.addAction("Graphical Selection ...")
        menu.addSeparator()
        _reset = menu.addAction("Full Reset")
        
        action = menu.exec_(QtGui.QCursor.pos())
        
        if action == _select_all:
            self.select_all()
        elif action == _unselect_all:
            self.unselect_all()
        elif action == _advanced_selection:
            self.advanced_selection()
        elif action == _reset:
            self.reset()
            
    def select_all(self):
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.ui.selection_table.blockSignals(True)
        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
        nbr_column = self.parent.fitting_ui.ui.value_table.columnCount()
        _selection_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_column-1)
        self.parent.fitting_ui.ui.value_table.setRangeSelected(_selection_range, True)
        o_fitting = FillingTableHandler(parent=self.parent)
        o_fitting.select_full_table()
        self.parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.ui.selection_table.blockSignals(False)
        
    def unselect_all(self):
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.ui.selection_table.blockSignals(True)        
        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
        nbr_column = self.parent.fitting_ui.ui.value_table.columnCount()
        _selection_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_column-1)
        self.parent.fitting_ui.ui.value_table.setRangeSelected(_selection_range, False)
        o_fitting = FillingTableHandler(parent=self.parent)
        o_fitting.unselect_full_table()
        self.parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.ui.selection_table.blockSignals(False)
        
    def advanced_selection(self):
        o_advanced = AdvancedSelectionLauncher(parent=self.parent)
        
    def reset(self):
        print("reset")
        
