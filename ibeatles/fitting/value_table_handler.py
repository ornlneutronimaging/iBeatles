try:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QApplication 
except:
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QApplication
import numpy as np
    
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
        _reset = None
        _fixed = None
        _unfixed = None
        
        #_select_all = menu.addAction("Activate All")
        #_select_all.setEnabled(status)
        #_unselect_all = menu.addAction("Deactivate All")
        #_unselect_all.setEnabled(status)
        #menu.addSeparator()
        _advanced_selection = menu.addAction("Selection/Lock Tool ...")
        _advanced_selection.setEnabled(status)
        _set_variables = menu.addAction("Selection/Lock - Check/Set Variables ...")
        _set_variables.setEnabled(status)
        menu.addSeparator()
        _fixed = menu.addAction("Fixed Variables Selected")
        _fixed.setEnabled(status)
        _unfixed = menu.addAction("Unfixed Variables Selected")
        _unfixed.setEnabled(status)
        
        #_reset = menu.addAction("Full Reset")
        #_reset.setEnabled(status)
        #_reset.setEnabled(False) #remove once implemented
        
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
        elif action == _fixed:
            self.fixed_variables()
        elif action == _unfixed:
            self.unfixed_variables()
            
    def changed_fixed_variables_status(self, status=True):
        selection = self.parent.fitting_ui.ui.value_table.selectedRanges()
        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
        
        o_fill_table = FillingTableHandler(parent=self.parent)
        row_to_show_status = o_fill_table.get_row_to_show_state()
        
        table_dictionary = self.parent.table_dictionary
        
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
            col_range = np.arange(left_column, right_column+1)
            for _col in col_range:
                
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
                            
            self.parent.table_dictionary = table_dictionary
            
            o_fitting = FillingTableHandler(parent=self.parent)
            o_fitting.fill_table()

    def fixed_variables(self):
        self.changed_fixed_variables_status(status=True)
            
    def unfixed_variables(self):
        self.changed_fixed_variables_status(status=False)
        
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
        
