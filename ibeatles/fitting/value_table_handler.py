try:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QApplication 
except:
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QApplication

from ibeatles.fitting.advanced_selection_launcher import AdvancedSelectionLauncher
from ibeatles.fitting.filling_table_handler import FillingTableHandler
from ibeatles.table_dictionary.table_dictionary_handler import TableDictionaryHandler
from ibeatles.fitting.set_fitting_variables_launcher import SetFittingVariablesLauncher


class ValueTableHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def right_click(self, position):
        menu = QtGui.QMenu(self.parent)
        
        if (len(self.parent.fitting_ui.data) == 0) or \
           (self.parent.binning_line_view['pos'] is None):
            status = False
        else:
            status = True

        _select_all = None
        _unselect_all = None

        #_select_all = menu.addAction("Activate All")
        #_select_all.setEnabled(status)
        #_unselect_all = menu.addAction("Deactivate All")
        #_unselect_all.setEnabled(status)
        #menu.addSeparator()
        _advanced_selection = menu.addAction("Bin Selection Tool ...")
        _advanced_selection.setEnabled(status)
        _set_variables = menu.addAction("Set Variables Values ...")
        _set_variables.setEnabled(status)
        menu.addSeparator()
        _reset = menu.addAction("Full Reset")
        _reset.setEnabled(status)
        _reset.setEnabled(False) #remove once implemented
        
        action = menu.exec_(QtGui.QCursor.pos())
        
        if action == _select_all:
            self.select_all()
        elif action == _unselect_all:
            self.unselect_all()
        elif action == _advanced_selection:
            self.advanced_selection()
        elif action == _set_variables:
            self.set_variables()
        elif action == _reset:
            self.reset()
            
    def select_all(self):
        
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        o_table = TableDictionaryHandler(parent=self.parent)
        o_table.select_full_table()
        
        o_fitting = FillingTableHandler(parent=self.parent)
        o_fitting.fill_table()
        
        self.parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)
        
        #if self.parent.advanced_selection_ui:
            #self.parent.advanced_selection_ui.ui.selection_table.blockSignals(True)
        
##        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
##        nbr_column = self.parent.fitting_ui.ui.value_table.columnCount()
##        _selection_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_column-1)
##        self.parent.fitting_ui.ui.value_table.setRangeSelected(_selection_range, True)
        #o_fitting = FillingTableHandler(parent=self.parent)
        #o_fitting.select_full_table()

#        self.parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.ui.selection_table.blockSignals(False)
        
        QApplication.restoreOverrideCursor()
        
    def unselect_all(self):
        
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)        
        
        o_table = TableDictionaryHandler(parent=self.parent)
        o_table.unselect_full_table()
    
        o_fitting = FillingTableHandler(parent=self.parent)
        o_fitting.fill_table()

        self.parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)

        #if self.parent.advanced_selection_ui:
            #self.parent.advanced_selection_ui.ui.selection_table.blockSignals(True)        
        #nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
        #nbr_column = self.parent.fitting_ui.ui.value_table.columnCount()
        #_selection_range = QtGui.QTableWidgetSelectionRange(0, 0, nbr_row-1, nbr_column-1)
        #self.parent.fitting_ui.ui.value_table.setRangeSelected(_selection_range, False)
        #o_fitting = FillingTableHandler(parent=self.parent)
        #o_fitting.unselect_full_table()
        #self.parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)
        #if self.parent.advanced_selection_ui:
            #self.parent.advanced_selection_ui.ui.selection_table.blockSignals(False)

        QApplication.restoreOverrideCursor()

    def advanced_selection(self):
        o_advanced = AdvancedSelectionLauncher(parent=self.parent)
        
    def set_variables(self):
        o_set = SetFittingVariablesLauncher(parent=self.parent)
        
    def reset(self):
        print("reset")
        
