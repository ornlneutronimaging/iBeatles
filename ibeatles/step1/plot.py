import numpy as np
import pyqtgraph as pg

import ibeatles.step1.utilities as utilities
from ibeatles.step1.time_spectra_handler import TimeSpectraHandler
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


class Step1Plot(object):
    
    data = []
    
    def __init__(self, parent=None, data_type='sample', data=[]):
        self.parent = parent
        self.data_type = data_type
        if data == []:
            data = self.parent.data_metadata[data_type]['data']
        self.data = data
        
    def all_plots(self):
        self.display_image()
        self.display_bragg_edge()

    def display_image(self):
        _data = self.data
        self.parent.live_data = _data
    
        if _data == []:
            self.clear_plots(data_type = self.data_type)
        else:
            if self.data_type == 'sample':
                self.parent.ui.area.setVisible(True)
                self.parent.ui.image_view.setImage(_data)       
            elif self.data_type == 'ob':
                self.parent.ui.ob_area.setVisible(True)
                self.parent.ui.ob_image_view.setImage(_data)
            elif self.data_type == 'normalized':
                self.parent.ui.normalized_area.setVisible(True)
                self.parent.ui.normalized_image_view.setImage(_data)

    def refresh_roi(self):
        pass


    def clear_plots(self, data_type = 'sample'):
        if data_type == 'sample':
            self.parent.ui.image_view.clear()
            self.parent.ui.bragg_edge_plot.clear()
        elif data_type == 'ob':
            self.parent.ui.ob_image_view.clear()
            self.parent.ui.ob_bragg_edge_plot.clear()
        elif data_type == 'normalized':
            self.parent.ui.normalized_image_view.clear()
            self.parent.ui.normalized_bragg_edge_plot.clear()
        
    def display_general_bragg_edge(self):
        data_type = utilities.get_tab_selected(parent=self.parent)
        self.data_type = data_type
        data = self.parent.data_metadata[data_type]['data']
        self.data = data
        self.display_bragg_edge()
        
    def save_roi(self, label, x0, y0, x1, y1, group, data_type, index):
        
        _width = x1-x0
        _height = np.abs(y1-y0)

        _list_roi = self.parent.list_roi[data_type]
        if _list_roi == []:
            _label = "roi_label"
            _group = "0"
            _list_roi = [_label, str(x0), str(y0), str(_width), str(_height), _group]
            self.parent.list_roi[data_type] = [_list_roi]
        else:
            _label = label
            _group = group
            _list_roi = [_label, str(x0), str(y0), str(_width), str(_height), _group]
            self.parent.list_roi[data_type][index] = _list_roi
        
    def update_roi_editor(self, index):
        
        o_roi_editor = self.parent.roi_editor_ui[self.data_type]
        o_roi_editor.refresh(row=index)
        
        #o_roi = RoiHandler(parent=self.parent, data_type=self.data_type)
        #row_to_activate = o_roi.get_roi_index_that_changed()
        #o_roi_editor.activate_row(row_to_activate)
        
    def extract_data(self, list_data_group, data):
        list_data = {'0': [],
                     '1': [],
                     '2': [],
                     '3': []}
        
        for _group in list_data_group.keys():
            _list_roi = list_data_group[_group]
            if _list_roi == []:
                list_data[_group] = []
            else:
                for _data in data:
                    nbr_roi = len(_list_roi)
                    _tmp_data = []
                    for _roi in _list_roi:  
                        [x0, x1, y0, y1] = _roi
                        
                        if self.parent.ui.roi_add_button.isChecked():
                            _tmp_data.append(np.sum(_data[y0:y1, x0:x1]))
                        else:
                            _tmp_data.append(np.mean(_data[y0:y1, x0:x1]))

                    if self.parent.ui.roi_add_button.isChecked():
                        list_data[_group].append(np.sum(_tmp_data))
                    else:
                        list_data[_group].append(np.mean(_tmp_data, axis=0))        
                                     
        return list_data

    def get_row_parameters(self, roi_editor_ui, row):
        
        ## label
        _item = roi_editor_ui.tableWidget.item(row, 0)
        if _item is None:
            raise ValueError
        label = str(_item.text())
        
        # x0
        _item = roi_editor_ui.tableWidget.item(row, 1)
        if _item is None:
            raise ValueError
        x0 = int(str(_item.text()))

        # y0
        _item = roi_editor_ui.tableWidget.item(row, 2)
        if _item is None:
            raise ValueError
        y0 = int(str(_item.text()))

        # width
        _item = roi_editor_ui.tableWidget.item(row, 3)
        if _item is None:
            raise ValueError
        width = int(str(_item.text()))

        # height
        _item = roi_editor_ui.tableWidget.item(row, 4)
        if _item is None:
            raise ValueError
        height = int(str(_item.text()))

        # group
        _group_widget = roi_editor_ui.tableWidget.cellWidget(row, 5)
        if _group_widget is None:
            raise ValueError
        _index_selected = _group_widget.currentIndex()
        group = str(_index_selected)
        
        return [label, x0, y0, width, height, group]        

    def display_bragg_edge(self, mouse_selection=True):

        _data = self.data
        if _data == []: #clear data if no data
            if self.data_type == 'sample':
                self.parent.ui.bragg_edge_plot.clear()
            elif self.data_type == 'ob':
                self.parent.ui.ob_bragg_edge_plot.clear()
            elif self.data_type == 'normalized':
                self.parent.ui.normalized_bragg_edge_plot.clear()
        else: #retrieve dictionaries of roi_id and roi data (label, x, y, w, h, group)
            list_roi_id = self.parent.list_roi_id[self.data_type]
            list_roi = self.parent.list_roi[self.data_type]
            roi_editor_ui = self.parent.roi_editor_ui[self.data_type]
            if self.data_type == 'sample':
                _image_view_item = self.parent.ui.image_view.imageItem
            elif self.data_type == 'ob':
                _image_view_item = self.parent.ui.ob_image_view.imageItem
            elif self.data_type == 'normalized':
                _image_view_item = self.parent.ui.normalized_image_view.imageItem
            
            # used here to group rois into their group for Bragg Edge plot    
            list_data_group = {'0': [],
                               '1': [],
                               '2': [],
                               '3': []}
            
            for _index, roi in enumerate(list_roi_id):

                if mouse_selection:
                    region = roi.getArraySlice(self.parent.live_data, 
                                               _image_view_item)

                    label = list_roi[_index][0]
                    x0 = region[0][0].start
                    x1 = region[0][0].stop-1
                    y0 = region[0][1].start
                    y1 = region[0][1].stop-1
                    group = list_roi[_index][-1]
               
                else: 
                    if roi_editor_ui is None:
                        return
                    try:
                        [label, x0, y0, w, h, group] = self.get_row_parameters(roi_editor_ui.ui, 
                                                                        _index)
                    except ValueError:
                        return
                    x1 = x0 + w
                    y1 = y0 + h
                    roi.setPos([x0, y0], update=False, finish=False)
                    roi.setSize([w, h], update=False, finish=False)

                roi.setPen(pen_color[group])
                
                list_data_group[group].append([x0, x1, y0, y1])
                
                self.save_roi(label, x0, y0, x1, y1, group, self.data_type, _index)
                
                if mouse_selection:
                    if not (roi_editor_ui is None):
                        roi_editor_ui.ui.tableWidget.blockSignals(True)
                        self.update_roi_editor(_index)
                        roi_editor_ui.ui.tableWidget.blockSignals(False)

            # work over groups
            data = self.parent.data_metadata[self.data_type]['data']
            bragg_edges = self.extract_data(list_data_group,
                                          data)

            #check if xaxis can be in lambda, or tof
            o_time_handler = TimeSpectraHandler(parent = self.parent)
            o_time_handler.load()
            tof_array = o_time_handler.tof_array
                
            list_files_selected = self.parent.list_file_selected[self.data_type]
            linear_region_left = list_files_selected[0]
            linear_region_right = list_files_selected[-1]

            if self.data_type == 'sample':
                self.parent.ui.bragg_edge_plot.clear()
                
                if tof_array == []:
                    self.parent.ui.bragg_edge_plot.setLabel('bottom', 'File Index')

                    for _key in bragg_edges.keys():
                        _bragg_edge = bragg_edges[_key]
                        if _bragg_edge == []:
                            continue
                        self.parent.ui.bragg_edge_plot.plot(_bragg_edge, pen=pen_color[_key])
                        tof_array = np.arange(len(_bragg_edge))
                        
                else:
                    
                    for _key in bragg_edges.keys():
                        _bragg_edge = bragg_edges[_key]
                        if _bragg_edge == []:
                            continue
                        self.parent.ui.bragg_edge_plot.plot(tof_array, _bragg_edge, pen=pen_color[_key])

                    linear_region_left = tof_array[linear_region_left]
                    linear_region_right = tof_array[linear_region_right]

                    self.parent.ui.bragg_edge_plot.setLabel('bottom', u'TOF (\u00B5s)')

                    #lambda axis
                    p1 = self.parent.ui.bragg_edge_plot.plotItem
                    caxis = CustomAxis(gui_parent = self.parent, orientation = 'top', parent=p1)
                    caxis.setLabel(u"\u03BB (\u212B)")
                    caxis.linkToView(p1.vb)
                    p1.layout.removeItem(self.parent.ui.caxis)
                    p1.layout.addItem(caxis, 1, 1)
                    self.parent.ui.caxis = caxis
                    
            elif self.data_type == 'ob':
                self.parent.ui.ob_bragg_edge_plot.clear()
                
                if tof_array == []:
                    self.parent.ui.ob_bragg_edge_plot.setLabel('bottom', 'File Index')

                    for _key in bragg_edges.keys():
                        _bragg_edge = bragg_edges[_key]
                        if _bragg_edge == []:
                            continue
                        self.parent.ui.ob_bragg_edge_plot.plot(_bragg_edge, pen=pen_color[_key])
                        tof_array = np.arange(len(_bragg_edge))

                else:

                    for _key in bragg_edges.keys():
                        _bragg_edge = bragg_edges[_key]
                        if _bragg_edge == []:
                            continue
                        self.parent.ui.ob_bragg_edge_plot.plot(tof_array, _bragg_edge, pen=pen_color[_key])

                    linear_region_left = tof_array[linear_region_left]
                    Linear_region_right = tof_array[linear_region_right]

                    self.parent.ui.ob_bragg_edge_plot.setLabel('bottom', u'TOF (\u00B5s)')

                    #lambda axis
                    p1 = self.parent.ui.ob_bragg_edge_plot.plotItem
                    caxis = CustomAxis(gui_parent = self.parent, orientation = 'top', parent=p1)
                    caxis.setLabel(u"\u03BB (\u212B)")
                    caxis.linkToView(p1.vb)
                    p1.layout.removeItem(self.parent.ui.ob_caxis)
                    p1.layout.addItem(caxis, 1, 1)
                    self.parent.ui.ob_caxis = caxis


            elif self.data_type == 'normalized':
                self.parent.ui.normalized_bragg_edge_plot.clear()

                if tof_array == []:
                    self.parent.ui.normalized_bragg_edge_plot.setLabel('bottom', 'File Index')

                    for _key in bragg_edges.keys():
                        _bragg_edge = bragg_edges[_key]
                        if _bragg_edge == []:
                            continue
                        self.parent.ui.normalized_bragg_edge_plot.plot(_bragg_edge, pen=pen_color[_key])
                        tof_array = np.arange(len(_bragg_edge))

                else:
                    for _key in bragg_edges.keys():
                        _bragg_edge = bragg_edges[_key]
                        if _bragg_edge == []:
                            continue
                        self.parent.ui.normalized_bragg_edge_plot.plot(tof_array, _bragg_edge, pen=pen_color[_key])
                        
                    linear_region_left = tof_array[linear_region_left]
                    Linear_region_right = tof_array[linear_region_right]

                    self.parent.ui.normalized_bragg_edge_plot.setLabel('bottom', u'TOF (\u00B5s)')

                    #lambda axis
                    p1 = self.parent.ui.normalized_bragg_edge_plot.plotItem
                    caxis = CustomAxis(gui_parent = self.parent, orientation = 'top', parent=p1)
                    caxis.setLabel(u"\u03BB (\u212B)")
                    caxis.linkToView(p1.vb)
                    p1.layout.removeItem(self.parent.ui.normalized_caxis)
                    p1.layout.addItem(caxis, 1, 1)
                    self.parent.ui.normalized_caxis = caxis

            lr = pg.LinearRegionItem([linear_region_left, linear_region_right])
            lr.setZValue(-10)

            if self.data_type == 'sample':
                self.parent.ui.bragg_edge_plot.addItem(lr)
            elif self.data_type == 'ob':
                self.parent.ui.ob_bragg_edge_plot.addItem(lr)
            else:
                self.parent.ui.normalized_bragg_edge_plot.addItem(lr)
                
            lr.sigRegionChangeFinished.connect(self.parent.bragg_edge_selection_changed)
            self.parent.list_bragg_edge_selection_id[self.data_type] = lr
            self.parent.current_bragg_edge_x_axis[self.data_type] = tof_array
