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


class SetFittingVariablesLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.fitting_set_variables_ui == None:
            set_variables_window = SetFittingVariablesWindow(parent=parent)
            self.parent.fitting_set_variables_ui = set_variables_window
            set_variables_window.show()
            set_variables_window.update_table()
        else:
            self.parent.fitting_set_variables_ui.setFocus()
            self.parent.fitting_set_variables_ui.activateWindow()
     
            
class SetFittingVariablesWindow(QMainWindow):
    
    advanced_mode = True
    
    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Set Variables Tool")
        
        self.init_widgets()
        self.init_table()
        
    def init_table(self):
        fitting_selection = self.parent.fitting_selection
        nbr_row = fitting_selection['nbr_row']
        nbr_column = fitting_selection['nbr_column']
    
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
        
    def closeEvent(self, event=None):
        self.parent.fitting_set_variables_ui = None
    