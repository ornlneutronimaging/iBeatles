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
            self.parent.advanced_selection_ui.acivateWindow()
        
class AdvancedSelectionWindow(QMainWindow):
    
    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Graphical Selection Tool")
        
        self.init_table()
        
    def init_table(self):
        fitting_selection = self.parent.fitting_selection
        nbr_row = fitting_selection['nbr_row']
        nbr_column = fitting_selection['nbr_column']
        
        self.ui.selection_table.setColumnCount(nbr_column)
        self.ui.selection_table.setRowCount(nbr_row)        
        
        value = np.int(self.ui.advanced_selection_cell_size_slider.value())
        self.selection_cell_size_changed(value)
        
    def selection_cell_size_changed(self, value):
        nbr_row = self.ui.selection_table.rowCount()
        nbr_column = self.ui.selection_table.columnCount()
        
        for _row in np.arange(nbr_row):
            self.ui.selection_table.setRowHeight(_row, value)
        
        for _col in np.arange(nbr_column):
            self.ui.selection_table.setColumnWidth(_col, value)
        
    def closeEvent(self, event=None):
        self.parent.advanced_selection_ui = None

