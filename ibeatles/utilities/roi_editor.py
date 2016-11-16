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
            
        nbr_groups = len(colors.roi_group_color)
        self.list_name_groups = ['group {}'.format(index) for index in range(nbr_groups)]
                       
            
    def get_item(self, text, color):
        _item = QtGui.QTableWidgetItem(text)
        _item.setForeground(color)

        return _item

    def fill_table(self):
        list_roi = self.parent.list_roi[self.title]

        # no ROI already define
        if list_roi == []:
            return
        
        self.ui.remove_roi_button.setEnabled(True)
        

        for _row, _roi in enumerate(list_roi):
            [label, x0, y0, width, height, group] = _roi
            self.ui.tableWidget.insertRow(_row)
            _color = colors.roi_group_color[int(group)]
            self.set_row(_row, label, x0, y0, width, height, int(group))

    def set_row(self, _row, label, x0, y0, width, height, group):

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
        _widget.addItems(self.list_name_groups)
        _widget.setCurrentIndex(int(group))
        QtCore.QObject.connect(_widget, QtCore.SIGNAL("currentIndexChanged(int)"), self.changed_group)
        self.ui.tableWidget.setCellWidget(_row, 5, _widget)

    def get_row(self, row=0):

        # label
        _item = self.ui.tableWidget.item(row, 0)
        if _item is None:
            raise ValueError
        label = str(_item.text())
        
        # x0
        _item = self.ui.tableWidget.item(row, 1)
        if _item is None:
            raise ValueError
        x0 = str(_item.text())

        # y0
        _item = self.ui.tableWidget.item(row, 2)
        if _item is None:
            raise ValueError
        y0 = str(_item.text())

        # width
        _item = self.ui.tableWidget.item(row, 3)
        if _item is None:
            raise ValueError
        width = str(_item.text())

        # height
        _item = self.ui.tableWidget.item(row, 4)
        if _item is None:
            raise ValueError
        height = str(_item.text())
        
        # group
        _group_widget = self.ui.tableWidget.cellWidget(row, 5)
        if _group_widget is None:
            raise ValueError
        _index_selected = _group_widget.currentIndex()
        group = str(_index_selected)
        
        return [label, x0, y0, width, height, group]

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
        _row_selected = self.get_row_selected()
        if _row_selected == -1:
            _new_row_index = 0
        else:
            _new_row_index = _row_selected
        
        self.ui.tableWidget.insertRow(_new_row_index)
        
        list_roi = self.parent.list_roi[self.title]
        _nbr_row = len(list_roi)

        init_roi = ['label_name', '0', '0', '1', '1', '0']
        [label, x0, y0, width, height, group] = init_roi

        new_list_roi = []
        _index_list_roi = 0
        for _index in range(_nbr_row ):
            if _index == _new_row_index:
                new_list_roi.append(init_roi)

            new_list_roi.append(list_roi[_index])
        
        self.parent.list_roi[self.title] = new_list_roi
        nbr_groups = len(colors.roi_group_color)
        
        list_name_groups = ['group {}'.format(index) for index in range(nbr_groups)]

        _color = colors.roi_group_color[0]
        _row = _new_row_index
        
        self.set_row(_row, label, x0, y0, width, height, int(group))
        
        self.ui.remove_roi_button.setEnabled(True)
        
    def remove_roi_button_clicked(self):
        _row_selected = self.get_row_selected()
        if _row_selected == -1:
            return
        
        self.ui.tableWidget.removeRow(_row_selected)
        
        list_roi = self.parent.list_roi[self.title]
        new_list_roi = []
        for _index, _array in enumerate(list_roi):
            if _index == _row_selected:
                continue
            new_list_roi.append(_array)

        if new_list_roi == []:
            self.ui.remove_roi_button.setEnabled(False)
            
        self.parent.list_roi[self.title] = new_list_roi

    def get_row_selected(self):
        try:
            _row_selected = self.ui.tableWidget.selectedRanges()[0].bottomRow()
        except IndexError:
            _row_selected = -1

        return _row_selected
        
    def refresh(self, row=0):
        
        [label, x0, y0, width, height, group] = self.parent.list_roi[self.title][row]
        self.set_row(row, label, x0, y0, width, height, group)
    
    def roi_editor_table_changed(self, row, column):
        _row = row
        try:
            row_variables = self.get_row(row = _row)
        except ValueError:
            return
        
        list_roi = self.parent.list_roi[self.title]
        list_roi[_row] = row_variables
        
        self.parent.list_roi[self.title] = list_roi