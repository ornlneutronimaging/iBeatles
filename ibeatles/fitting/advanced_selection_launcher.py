try:
    import PyQt4
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QMainWindow
except:
    import PyQt5
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QMainWindow
import numpy as np

from ibeatles.interfaces.ui_advancedFittingSelection import Ui_MainWindow as UiMainWindow


class AdvancedSelectionLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.advanced_selection_ui == None:
            advanced_window = AdvancedSelectionWindow(parent=parent)
            advanced_window.show()
            self.parent.advanced_selection_ui = advanced_window
        else:
            self.parent.advanced_selection_ui.setFocus()
            self.parent.advanced_selection_ui.activateWindow()
        
class AdvancedSelectionWindow(QMainWindow):
    
    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Graphical Selection Tool")
        
        self.ui.selection_table.blockSignals(True)
        self.ui.lock_table.blockSignals(True)
        self.init_table()
        self.ui.selection_table.blockSignals(False)
        self.ui.lock_table.blockSignals(False)
        
    def init_table(self):
        fitting_selection = self.parent.fitting_selection
        nbr_row = fitting_selection['nbr_row']
        nbr_column = fitting_selection['nbr_column']
        
        #selection table
        self.ui.selection_table.setColumnCount(nbr_column)
        self.ui.selection_table.setRowCount(nbr_row)        
        self.update_selection_table()
        
        #lock table
        self.ui.lock_table.setColumnCount(nbr_column)
        self.ui.lock_table.setRowCount(nbr_row)        
        self.update_lock_table()

        #set size of cells
        value = np.int(self.ui.advanced_selection_cell_size_slider.value())
        self.selection_cell_size_changed(value)

    def update_selection_table(self):
        self.update_table(state_field = 'selected',
                              table_ui = self.ui.selection_table)

    def update_lock_table(self):
        self.update_table(state_field = 'lock',
                          table_ui = self.ui.lock_table)

    def update_table(self, state_field='', table_ui=None):
        table_dictionary = self.parent.fitting_ui.table_dictionary
        
        for _index in table_dictionary:
            _entry = table_dictionary[_index]
            state = _entry[state_field]
            row_index = _entry['row_index']
            column_index = _entry['column_index']
            _selection = QtGui.QTableWidgetSelectionRange(row_index, column_index, 
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
        
        self.parent.fitting_ui.ui.value_table.blockSignals(True)
        
        selection = self.ui.selection_table.selectedRanges()
        nbr_row = self.ui.selection_table.rowCount()

        nbr_row_fitting_table = self.parent.fitting_ui.ui.value_table.rowCount()
        nbr_col_fitting_table = self.parent.fitting_ui.ui.value_table.columnCount()
        
        #clear fitting table
        reset_selection = QtGui.QTableWidgetSelectionRange(0, 0, 
                                                           nbr_row_fitting_table-1,
                                                           nbr_col_fitting_table-1)
        self.parent.fitting_ui.ui.value_table.setRangeSelected(reset_selection, False)

        for _select in selection:
            top_row = _select.topRow()
            left_col = _select.leftColumn()
            bottom_row = _select.bottomRow()
            right_col = _select.rightColumn()
            for _row in np.arange(top_row, bottom_row+1):
                for _col in np.arange(left_col, right_col+1):
                    fitting_row = _col*nbr_row + _row
                    local_selection = QtGui.QTableWidgetSelectionRange(fitting_row, 0, 
                                                                       fitting_row, 
                                                                       nbr_col_fitting_table-1)
                    self.parent.fitting_ui.ui.value_table.setRangeSelected(local_selection, True)

        fitting_ui = self.parent.fitting_ui
        fitting_ui.update_image_view_selection()
    
        self.parent.fitting_ui.ui.value_table.blockSignals(False)

    def lock_table_selection_changed(self):
        pass
        
    def closeEvent(self, event=None):
        self.parent.advanced_selection_ui = None

