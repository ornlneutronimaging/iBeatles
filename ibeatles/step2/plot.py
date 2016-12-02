import numpy as np
import pyqtgraph as pg

from PyQt4 import QtGui, QtCore

from neutronbraggedge.experiment_handler.experiment import Experiment
from ibeatles.utilities.colors import pen_color
from ibeatles.utilities.roi_handler import RoiHandler


class CustomAxis(pg.AxisItem):
    
    def __init__(self, gui_parent, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.parent = gui_parent
        
    def tickStrings(self, values, scale, spacing):
        strings = []

        _distance_source_detector = float(str(self.parent.ui.distance_source_detector.text()))
        _detector_offset_micros = float(str(self.parent.ui.detector_offset.text()))

        tof_s = [float(time)*1e-6 for time in values]

        _exp = Experiment(tof = tof_s,
                          distance_source_detector_m = _distance_source_detector,
                          detector_offset_micros = _detector_offset_micros)
        lambda_array = _exp.lambda_array

        for _lambda in lambda_array:
            strings.append("{:.4f}".format(_lambda*1e10))

        return strings
    
    
class Step2Plot(object):
    
    sample = []
    ob = []
    normalization = []

    def __init__(self, parent=None, sample=[], ob=[], normalized=[]):
        self.parent = parent

        if sample == []:
            sample = self.parent.data_metadata['sample']['data']

        if sample == []:
            return
            
        if ob == []:
            ob = self.parent.data_metadata['ob']['data']
            
        if normalized == []:
            normalized = self.parent.data_metadata['normalized']['data']
        
        if self.parent.data_metadata['normalization']['data'] == []:
            normalization = np.mean(np.array(sample), axis=0)
            self.parent.data_metadata['normalization']['axis'] = normalization
        else:
            normalization = self.parent.data_metadata['normalization']['data']
            
        self.sample = sample
        self.ob = ob
        self.normalization = normalization
        self.normalized = normalized

    def clear_image(self):
        self.parent.step2_ui['image_view'].clear()
        
    def display_image(self):
        _data = self.normalization
        
        if _data == []:
            self.clear_plots()
            self.parent.step2_ui['area'].setVisible(False)
        else:
            self.parent.step2_ui['area'].setVisible(True)
            self.parent.step2_ui['image_view'].setImage(_data)
            
    def display_roi(self):
        list_roi_id = self.parent.list_roi_id['normalization']
        roi = self.parent.list_roi['normalization']

        if list_roi_id == []:
            return
        
        for index, roi_id in enumerate(list_roi_id):
            
            [flag, x0, y0, width, height, not_used] = roi[index]
            
            x1 = x0 + width
            y1 = y0 + height
            
            roi_id.setPos([x0, y0], update=False, finish=False)
            roi_id.setSize([width, height], update=False, finish=False)

    def display_counts_vs_file(self, list_roi=[]):
        _data = self.normalized
        if _data == []: 
            self.clear_counts_vs_file()
            return
        
        if list_roi == []:
            self.clear_counts_vs_file()
            return
        
        _array_sample_vs_file_index = self.calculate_mean_counts(_data, list_roi=list_roi)
            
        self.parent.step2_ui['bragg_edge_plot'].clear()
        self.parent.step2_ui['bragg_edge_plot'].plot(_array_sample_vs_file_index)

    def calculate_mean_counts(self, data, list_roi=[]):
        if data == []:
            return data
        
        data = np.array(data)
        final_array = []
        _first_array_added = True
        nbr_roi = len(list_roi)

        if list_roi == []:
            final_array = np.mean(data, axis=(1,2))
        
        else:
            for _index, _roi in enumerate(list_roi):
                [x0, y0, width, height]= _roi
    
                _x_from = int(x0)
                _x_to = _x_from + int(width) + 1
                
                _y_from = int(y0)
                _y_to = _y_from + int(height) + 1
                
                _mean = np.mean(data[:, _x_from: _x_to, _y_from: _y_to], axis=(1,2))
                if _first_array_added:
                    final_array = _mean
                    _first_array_added = False
                else:
                    final_array += _mean
                    
            final_array /= nbr_roi
                
        return final_array

    def init_roi_table(self):
        if self.sample == []: return

        # clear table
        for _row in np.arange(self.parent.ui.normalization_tableWidget.rowCount()):
            self.parent.ui.normalization_tableWidget.removeRow(0)
        
        list_roi = self.parent.list_roi['normalization']
        for _row, _roi in enumerate(list_roi):
            self.parent.ui.normalization_tableWidget.insertRow(_row)
            self.set_row(_row, _roi)

    def update_roi_table(self):
        if self.sample == []: return
        
        list_roi = self.parent.list_roi['normalization']
        for _row, _roi in enumerate(list_roi):
            self.update_row(_row, _roi)
            
    def get_item(self, text):
        _item = QtGui.QTableWidgetItem(text)
        #_item.setBackground(color)
        return _item

    def set_row(self, row_index, roi_array):
        [status_row, x0, y0, width, height, mean_counts] = roi_array
        
        # button
        _widget = QtGui.QCheckBox()
        _widget.setChecked(status_row)
        QtCore.QObject.connect(_widget, QtCore.SIGNAL("stateChanged(int)"), self.parent.normalization_row_status_changed)
        self.parent.ui.normalization_tableWidget.setCellWidget(row_index, 0, _widget)
        
        # x0
        _item = self.get_item(str(x0))
        self.parent.ui.normalization_tableWidget.setItem(row_index, 1, _item)
        
        # y0
        _item = self.get_item(str(y0))
        self.parent.ui.normalization_tableWidget.setItem(row_index, 2, _item)
        
        # width
        _item = self.get_item(str(width))
        self.parent.ui.normalization_tableWidget.setItem(row_index, 3, _item)
        
        # height
        _item = self.get_item(str(height))
        self.parent.ui.normalization_tableWidget.setItem(row_index, 4, _item)
        
        ## mean counts
        #_item = self.get_item(str(mean_counts))
        #self.parent.ui.normalization_tableWidget.setItem(row_index, 6, _item)
            
    def update_row(self, row_index, roi_array):
        [status_row, x0, y0, width, height, mean_counts] = roi_array

        # button
        _widget = self.parent.ui.normalization_tableWidget.cellWidget(row_index, 0)
        _widget.setChecked(status_row)
        
        # x0
        _item = self.parent.ui.normalization_tableWidget.item(row_index, 1)
        _item.setText(str(x0))
        
        # y0
        _item = self.parent.ui.normalization_tableWidget.item(row_index, 2)
        _item.setText(str(y0))
        
        # width
        _item = self.parent.ui.normalization_tableWidget.item(row_index, 3)
        _item.setText(str(width))
        
        # height
        _item = self.parent.ui.normalization_tableWidget.item(row_index, 4)
        _item.setText(str(height))
        
    def clear_plots(self):
        self.parent.step2_ui['image_view'].clear()
        self.parent.step2_ui['bragg_edge_plot'].clear()
        #self.parent.step2_ui['normalized_profile_plot'].clear()
        
    def clear_counts_vs_file(self):
        self.parent.step2_ui['bragg_edge_plot'].clear()
        