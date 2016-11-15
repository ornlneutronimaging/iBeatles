from PyQt4 import QtGui

from ibeatles.interfaces.ui_roiEditor import Ui_MainWindow as UiMainWindow
from ibeatles.utilities.gui_handler import GuiHandler


class RoiEditor(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run(self):
        
        o_gui = GuiHandler(parent = self.parent)
        active_tab = o_gui.get_active_tab()
        
        list_roi_editor_ui = self.parent.roi_editor_ui
        _roi_ui = list_roi_editor_ui[active_tab]
        if _roi_ui is None:
            _interface = RoiEditorInterface(parent = self.parent)
            _interface.show()
            list_roi_editor_ui[active_tab] = _interface
            self.parent.roi_editor_ui = list_roi_editor_ui
        else:
            _interface = list_roi_editor_ui[active_tab]
            _interface.activateWindow()
    
    
class RoiEditorInterface(QtGui.QMainWindow):
    
    def __init__(self, parent=None, title='sample'):
        
        self.parent = parent
        
        QtGui.QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        
    def closeEvent(self, event=None):
        o_gui = GuiHandler(parent = self.parent)
        active_tab = o_gui.get_active_tab()
        self.parent.roi_editor_ui[active_tab] = None

        