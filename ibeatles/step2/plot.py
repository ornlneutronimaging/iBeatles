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

    def __init__(self, parent=None, sample=[], ob=[]):
        self.parent = parent
        sample = self.parent.data_metadata['sample']['data']
        ob = self.parent.data_metadata['ob']['data']
        
        if self.parent.data_metadata['normalization']['data'] == []:
            normalizaton = np.mean(np.array(sample), axis=0)
            self.parent.data_metadata['normalization']['axis'] = normalizaton
        else:
            normalization = self.parent.data_metadata['normalization']['data']
            
        self.sample = sample
        self.ob = ob
        self.normalization = normalization
        
    def display_image(self):
        _data = self.normalization
        
        if _data == []:
            self.clear_plots()
            self.parent.step2_ui['area'].setVisible(False)
        else:
            self.parent.step2_ui['area'].setVisible(True)
            self.parent.step2_ui['image_view'].setImage(_data)
            
    def display_counts_vs_file(self):
        _sample = self.sample
        if _sample == []: return
        
        list_roi = self.parent.list_roi['normalization']
        
        array_sample_vs_file_index = self.calculate_mean_counts(_sample)
        array_ob_vs_file_index = self.calculate_mean_counts(self.ob)
        
        if array_ob_vs_file_index == []:
            _array = array_sample_vs_file_index
        else:
            _array = array_sample_vs_file_index / array_ob_vs_file_index
            
        self.parent.step2_ui['bragg_edge_plot'].clear()
        self.parent.step2_ui['bragg_edge_plot'].plot(_array)

    def calculate_mean_counts(self, data):
        if data == []:
            return data
        
        data = np.array(data)
        list_roi = self.parent.list_roi['normalization']
        final_array = []
        for _index, _roi in enumerate(list_roi):
            [flag, x0, y0, width, height, value] = _roi
            _mean = np.mean(data[:, x0:x0+width, y0:y0+height], axis=1)
            if _index == 0:
                final_array = _mean
            else:
                final_array += _mean
                
        return np.mean(final_array, axis=1)

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
        