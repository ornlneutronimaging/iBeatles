from PyQt4 import QtGui, QtCore
import pyqtgraph as pg

from ibeatles.step2.gui_handler import Step2GuiHandler


class Step2RoiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def save_table(self):
        list_roi = self.parent.list_roi['normalization']

        for _row, roi in enumerate(list_roi):
            try:
                _row_infos = self.get_row(_row)
            except ValueError:
                return
            
            list_roi[_row] = _row_infos
            
        self.parent.list_roi['normalization'] = list_roi

    def enable_selected_roi(self):
        list_roi = self.parent.list_roi['normalization']
        list_roi_id = self.parent.list_roi_id['normalization']
        
        for index, roi in enumerate(list_roi):
            
            _roi_id = list_roi_id[index]
            is_roi_visible = roi[0]
            if is_roi_visible:
                _roi_id.setVisible(True)
            else:
                _roi_id.setVisible(False)
            
    def get_row(self, row=-1):
        if row == -1:
            return []
        
        # use flag
        _flag_widget = self.parent.ui.normalization_tableWidget.cellWidget(row, 0)
        if _flag_widget is None:
            raise ValueError
        flag = _flag_widget.isChecked()
        
        # x0
        _item = self.parent.ui.normalization_tableWidget.item(row, 1)
        if _item is None:
            raise ValueError
        x0 = str(_item.text())
        
        # y0
        _item = self.parent.ui.normalization_tableWidget.item(row, 2)
        if _item is None:
            raise ValueError
        y0 = str(_item.text())
        
        # width
        _item = self.parent.ui.normalization_tableWidget.item(row, 3)
        if _item is None:
            raise ValueError
        width = str(_item.text())
        
        # height
        _item = self.parent.ui.normalization_tableWidget.item(row, 4)
        if _item is None:
            raise ValueError
        height = str(_item.text())
        
        return [flag, x0, y0, width, height, -1]

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
        
        list_roi = self.parent.list_roi['normalization']
        list_roi_id = self.parent.list_roi_id['normalization']
        new_list_roi = []
        new_list_roi_id = []
        for _index, _roi in enumerate(list_roi):
            if _index == _row_selected:
                continue
            new_list_roi.append(_roi)
            new_list_roi_id.append(list_roi_id[_index])
            
        self.parent.list_roi['normalization'] = new_list_roi
        self.parent.list_roi_id['normalization'] = new_list_roi_id

        o_gui = Step2GuiHandler(parent = self.parent)
        o_gui.check_add_remove_roi_buttons()

    def add_roi_in_image(self):
        roi = pg.ROI([0,0],[1,1])
        roi.addScaleHandle([1,1],[0,0])
        roi.sigRegionChangeFinished.connect(self.parent.normalization_manual_roi_changed)
        self.parent.step2_ui['image_view'].addItem(roi)
        return roi

    def add_roi(self):
        nbr_row_table = self.parent.ui.normalization_tableWidget.rowCount()
        new_roi_id = self.add_roi_in_image()

        self.parent.list_roi['normalization'].append(self.parent.init_array_normalization)
        self.parent.list_roi_id['normalization'].append(new_roi_id)

        self.insert_row(row=nbr_row_table)
        
        o_gui = Step2GuiHandler(parent = self.parent)
        o_gui.check_add_remove_roi_buttons()    
        
    def get_item(self, text):
        _item = QtGui.QTableWidgetItem(text)
        #_item.setBackground(color)
        return _item

    def insert_row(self, row=-1):
        self.parent.ui.normalization_tableWidget.insertRow(row)
       
        init_array = self.parent.list_roi['normalization'][-1]
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
    
