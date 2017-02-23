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
        self.setWindowTitle("Advanced Selection Tool")
        
    def closeEvent(self, event=None):
        self.parent.advanced_selection_ui = None
     