try:
    import PyQt4
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QMainWindow
    from PyQt4.QtGui import QApplication     
except:
    import PyQt5
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QApplication
    
import numpy as np

from ibeatles.interfaces.ui_fittingSetVariables import Ui_MainWindow as UiMainWindow
from ibeatles.fitting.set_fitting_variables_handler import SetFittingVariablesHandler
from ibeatles.fitting.filling_table_handler import FillingTableHandler


class SetFittingVariablesLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.fitting_set_variables_ui == None:
            set_variables_window = SetFittingVariablesWindow(parent=parent)
            self.parent.fitting_set_variables_ui = set_variables_window
            set_variables_window.show()
#            set_variables_window.update_table()
        else:
            self.parent.fitting_set_variables_ui.setFocus()
            self.parent.fitting_set_variables_ui.activateWindow()
            
class SetFittingVariablesWindow(QMainWindow):
    
    advanced_mode = True
    nbr_column = -1
    nbr_row = -1
    
    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Check/Set Variables")
        self.installEventFilter(self)
        
        self.init_widgets()
        self.init_table()
        
    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.update_table()
        return False
        
    def init_table(self):
        fitting_selection = self.parent.fitting_selection
        nbr_row = fitting_selection['nbr_row']
        nbr_column = fitting_selection['nbr_column']
    
        self.nbr_column = nbr_column
        self.nbr_row = nbr_row
    
        #selection table
        self.ui.variable_table.setColumnCount(nbr_column)
        self.ui.variable_table.setRowCount(nbr_row)        

        #set size of cells
        value = np.int(self.ui.advanced_selection_cell_size_slider.value())
        self.selection_cell_size_changed(value)        
        
    def init_widgets(self):
        self.advanced_mode = self.parent.fitting_ui.ui.advanced_table_checkBox.isChecked()
        if not self.advanced_mode:
            self.ui.a5_button.setVisible(False)
            self.ui.a6_button.setVisible(False)
            
        self.ui.fixed_label.setStyleSheet("background-color: green")
        self.ui.locked_label.setStyleSheet("background-color: green")
        self.ui.active_label.setStyleSheet("background-color: green")
            
    def selection_cell_size_changed(self, value):
        nbr_row = self.ui.variable_table.rowCount()
        nbr_column = self.ui.variable_table.columnCount()
        
        for _row in np.arange(nbr_row):
            self.ui.variable_table.setRowHeight(_row, value)
            #self.ui.colorscale_table.setRowHeight(_row, value)
        
        for _col in np.arange(nbr_column):
            self.ui.variable_table.setColumnWidth(_col, value)
            #self.ui.colorscale_table.setColumnWidth(_col, value)
        
    def update_table(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        variable_selected = self.get_variable_selected()
        o_handler = SetFittingVariablesHandler(parent=self.parent)
        o_handler.populate_table_with_variable(variable = variable_selected)
        o_filling_table = FillingTableHandler(parent = self.parent)
        self.parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.parent.fitting_ui.ui.value_table.blockSignals(False)        
        QApplication.restoreOverrideCursor()        
        
    def get_variable_selected(self):
        if self.ui.d_spacing_button.isChecked():
            return 'd_spacing'
        elif self.ui.sigma_button.isChecked():
            return 'sigma'
        elif self.ui.alpha_button.isChecked():
            return 'alpha'
        elif self.ui.a1_button.isChecked():
            return 'a1'
        elif self.ui.a2_button.isChecked():
            return 'a2'
        elif self.ui.a5_button.isChecked():
            return 'a5'
        elif self.ui.a6_button.isChecked():
            return 'a6'
    
    def apply_new_value_to_selection(self):
        variable_selected = self.get_variable_selected()
        selection = self.parent.fitting_set_variables_ui.ui.variable_table.selectedRanges()
        o_handler = SetFittingVariablesHandler(parent=self.parent)
        new_variable = np.float(str(self.parent.fitting_set_variables_ui.ui.new_value_text_edit.text()))
        o_handler.set_new_value_to_selected_bins(selection=selection, 
                                                variable_name=variable_selected,
                                                variable_value=new_variable,
                                                table_nbr_row = self.nbr_row)
        self.parent.fitting_set_variables_ui.ui.new_value_text_edit.setText('')
        o_filling_table = FillingTableHandler(parent = self.parent)
        self.parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.parent.fitting_ui.ui.value_table.blockSignals(False)        
    
    def variable_table_right_click(self, position):
        o_variable = VariableTableHandler(parent = self.parent)
        o_variable.right_click(position=position)
        
    def closeEvent(self, event=None):
        self.parent.fitting_set_variables_ui = None
        
            
class VariableTableHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def right_click(self, position=None):
        menu = QtGui.QMenu(self.parent)
        
        _activate = menu.addAction("Activate Selection")
        _deactivate = menu.addAction("Deactivate Selection")
        menu.addSeparator()
        _lock = menu.addAction("Lock Selection")
        _unlock = menu.addAction("Unlock Selection")
        
        action = menu.exec_(QtGui.QCursor.pos())
        
        if action == _lock:
            self.lock_selection()
        elif action == _unlock:
            self.unlock_selection()
        elif action == _activate:
            self.activate_selection()
        elif action == _deactivate:
            self.deactivate_selection()
            
    def activate_selection(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.change_state_of_bins(name='active', state=True)
        self.update_fitting_ui(name='active')
        self.update_advanced_selection_ui(name='active')
        QApplication.restoreOverrideCursor()        
    
    def deactivate_selection(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.change_state_of_bins(name='active', state=False)
        self.update_fitting_ui(name='active')
        self.update_advanced_selection_ui(name='active')
        QApplication.restoreOverrideCursor()        
            
    def lock_selection(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.change_state_of_bins(name='lock', state=True)
        self.update_fitting_ui(name='lock')
        self.update_advanced_selection_ui(name='lock')
        QApplication.restoreOverrideCursor()        
    
    def unlock_selection(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.change_state_of_bins(name='lock', state=False)
        self.update_fitting_ui(name='lock')
        self.update_advanced_selection_ui(name='lock')
        QApplication.restoreOverrideCursor()        

    def change_state_of_bins(self, name='lock', state=True):
        selection = self.parent.fitting_set_variables_ui.ui.variable_table.selectedRanges()
        table_dictionary = self.parent.table_dictionary
        nbr_row = self.parent.fitting_set_variables_ui.nbr_row
        
        for _select in selection:
            _left_column = _select.leftColumn()
            _right_column = _select.rightColumn()
            _top_row = _select.topRow()
            _bottom_row = _select.bottomRow()
            for _row in np.arange(_top_row, _bottom_row+1):
                for _col in np.arange(_left_column, _right_column+1):
                    _index = _row + _col * nbr_row
                    table_dictionary[str(_index)][name] = state
            
            #remove selection markers
            self.parent.fitting_set_variables_ui.ui.variable_table.setRangeSelected(_select, False)
        
        self.parent.table_dictionary = table_dictionary
        self.parent.fitting_set_variables_ui.update_table()        

    def update_fitting_ui(self, name='active'):
        if name == 'lock':
            self.parent.fitting_ui.update_image_view_lock()
        elif name == 'active':
            self.parent.fitting_ui.update_image_view_selection()
    
        o_filling_table = FillingTableHandler(parent = self.parent)
        self.parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.parent.fitting_ui.ui.value_table.blockSignals(False)        
    
    def update_advanced_selection_ui(self, name='active'):
        if self.parent.advanced_selection_ui:
            if name == 'lock':
                self.parent.advanced_selection_ui.update_lock_table()
            elif name == 'active':
                self.parent.advanced_selection_ui.update_selected_table()
