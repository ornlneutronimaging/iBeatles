from PyQt4 import QtGui, QtCore

from ibeatles.step2.gui_handler import Step2GuiHandler


class Step2RoiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def save_roi(self):
        list_roi_id = self.parent.list_roi_id['normalization']
        list_roi = self.parent.list_roi['normalization']

        sample = self.parent.data_metadata['normalization']['data']
        image_item = self.parent.step2_ui['image_view'].imageItem

        for _index, _roi_id in enumerate(list_roi_id):
            region = _roi_id.getArraySlice(sample, image_item)
            x0 = region[0][0].start
            x1 = region[0][0].stop-1
            y0 = region[0][1].start
            y1 = region[0][1].stop-1

            width = x1-x0
            height = y1-y0
            
            _roi = list_roi[_index]
            _roi[1] = x0
            _roi[2] = y0
            _roi[3] = width
            _roi[4] = height
            
            list_roi[_index] = _roi
            
        self.parent.list_roi['normalization'] = list_roi

    def remove_roi(self):
        selection = self.parent.ui.normalization_tableWidget.selectedRanges()
        if selection == []:
            return
        
        selection = selection[0]
        _row_selected = selection.bottomRow()
        
        self.parent.ui.normalization_tableWidget.removeRow(_row_selected)
        
        o_gui = Step2GuiHandler(parent = self.parent)
        o_gui.check_add_remove_roi_buttons()

    def add_roi(self):
        nbr_row_table = self.parent.ui.normalization_tableWidget.rowCount()
        self.insert_row(row=nbr_row_table)
        
        o_gui = Step2GuiHandler(parent = self.parent)
        o_gui.check_add_remove_roi_buttons()        
        
    def get_item(self, text):
        _item = QtGui.QTableWidgetItem(text)
        #_item.setBackground(color)
        return _item

    def insert_row(self, row=-1):
        self.parent.ui.normalization_tableWidget.insertRow(row)
        
        init_array = self.parent.init_array_normalization
        [flag, x0, y0, width, height, not_used] = init_array
        
        # button
        _widget = QtGui.QCheckBox()
        _widget.setChecked(flag)
        QtCore.QObject.connect(_widget, QtCore.SIGNAL("stateChanged(int)"), self.parent.normalization_row_status_changed)
        self.parent.ui.normalization_tableWidget.setCellWidget(row, 0, _widget)
    
        # x0
        _item = self.get_item(str(x0))
        self.parent.ui.normalization_tableWidget.setItem(row, 1, _item)
    
        # y0
        _item = self.get_item(str(y0))
        self.parent.ui.normalization_tableWidget.setItem(row, 2, _item)
    
        # width
        _item = self.get_item(str(width))
        self.parent.ui.normalization_tableWidget.setItem(row, 3, _item)
    
        # height
        _item = self.get_item(str(height))
        self.parent.ui.normalization_tableWidget.setItem(row, 4, _item)
    
