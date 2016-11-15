from PyQt4 import QtGui, QtCore

from ibeatles.interfaces.ui_roiEditor import Ui_MainWindow as UiMainWindow
from ibeatles.utilities.gui_handler import GuiHandler
from ibeatles.utilities import colors

class RoiEditor(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run(self):
        
        o_gui = GuiHandler(parent = self.parent)
        active_tab = o_gui.get_active_tab()
        
        list_roi_editor_ui = self.parent.roi_editor_ui
        _roi_ui = list_roi_editor_ui[active_tab]
        if _roi_ui is None:
            _interface = RoiEditorInterface(parent = self.parent, title=active_tab)
            _interface.show()

            # save ui id
            list_roi_editor_ui[active_tab] = _interface
            self.parent.roi_editor_ui = list_roi_editor_ui
            
        else:
            _interface = list_roi_editor_ui[active_tab]
            _interface.activateWindow()
    
    
class RoiEditorInterface(QtGui.QMainWindow):
    
    col_width = [150,40,40,40,40]
    
    def __init__(self, parent=None, title='sample'):
        
        self.parent = parent
        self.title = title
        
        QtGui.QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("{} ROI Editor".format(title))

        self.initialize_table()
        self.fill_table()
        
    def initialize_table(self):
        for _index, _width in enumerate(self.col_width):
            self.ui.tableWidget.setColumnWidth(_index, _width)
            
    def get_item(self, text, color):
        _item = QtGui.QTableWidgetItem(text)
        #_item.setBackgroundColor(color)
        _item.setForeground(color)

        return _item

    def fill_table(self):
        list_roi = self.parent.list_roi[self.title]

        # no ROI selected yet
        if list_roi == []:
            return
        
        nbr_groups = len(colors.roi_group_color)
        list_name_groups = ['group {}'.format(index) for index in range(nbr_groups)]

        for _row, _roi in enumerate(list_roi):
            [label, x0, y0, width, height, group] = _roi
            self.ui.tableWidget.insertRow(_row)
            
            _color = colors.roi_group_color[int(group)]
            
            # label
            _item = self.get_item(label, _color)
            self.ui.tableWidget.setItem(_row, 0, _item)
            
            # x0
            _item = self.get_item(x0, _color)
            self.ui.tableWidget.setItem(_row, 1, _item)

            # y0
            _item = self.get_item(y0, _color)
            self.ui.tableWidget.setItem(_row, 2, _item)

            # width
            _item = self.get_item(width, _color)
            self.ui.tableWidget.setItem(_row, 3, _item)

            # height
            _item = self.get_item(height, _color)
            self.ui.tableWidget.setItem(_row, 4, _item)
            
            # group
            _widget = QtGui.QComboBox()
            _widget.addItems(list_name_groups)
            _widget.setCurrentIndex(int(group))
            QtCore.QObject.connect(_widget, QtCore.SIGNAL("currentIndexChanged(int)"), self.changed_group)
            self.ui.tableWidget.setCellWidget(_row, 5, _widget)

    def changed_group(self, _ignore):
        _nbr_row = self.ui.tableWidget.rowCount()
        for _row in range(_nbr_row):
            _group_widget = self.ui.tableWidget.cellWidget(_row, 5)
            _index_selected = _group_widget.currentIndex()
            
            _color = colors.roi_group_color[_index_selected]

            _item = self.ui.tableWidget.item(_row, 0)
            _item.setForeground(_color)
            
            _item = self.ui.tableWidget.item(_row, 1)
            _item.setForeground(_color)

            _item = self.ui.tableWidget.item(_row, 2)
            _item.setForeground(_color)

            _item = self.ui.tableWidget.item(_row, 3)
            _item.setForeground(_color)

            _item = self.ui.tableWidget.item(_row, 4)
            _item.setForeground(_color)

        
    def closeEvent(self, event=None):
        o_gui = GuiHandler(parent = self.parent)
        active_tab = o_gui.get_active_tab()
        self.parent.roi_editor_ui[active_tab] = None

    def add_roi_button_clicked(self):
        pass
    

    def remove_roi_button_clicked(self):
        pass