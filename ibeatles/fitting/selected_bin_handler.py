import numpy as np
import pyqtgraph as pg


class SelectedBinsHandler(object):
    
    selected_color = {'pen': (0,0,0,30),
                      'brush': (0,255,0,150)}
    
    lock_color = {'pen': (0,0,0,30),
                  'brush': (255,0,0,240)}
    
    def __init__(self, parent=None):
        self.parent = parent
        self.fitting_ui = self.parent.fitting_ui
        
    def clear_all_selected_bins(self):
        list_bins = self.parent.fitting_ui.list_bins_selected_item
        for _bin_ui in list_bins:
            self.parent.fitting_ui.image_view.removeItem(_bin_ui)
                
        list_bins = self.parent.fitting_ui.list_bins_locked_item
        for _bin_ui in list_bins:
            self.parent.fitting_ui.image_view.removeItem(_bin_ui)

    def update_bins_selected(self):
        self.clear_all_selected_bins()
        selection = self.fitting_ui.ui.value_table.selectedRanges()
        list_bin_selected = self.retrieve_list_bin_selected(selection)        
    
        table_dictionary = self.parent.fitting_ui.table_dictionary

        list_bins_selected_rect_item = []
        for _bin in list_bin_selected:
            _coordinates = table_dictionary[str(_bin)]['bin_coordinates']            
            x0 = _coordinates['x0']
            x1 = _coordinates['x1']
            y0 = _coordinates['y0']
            y1 = _coordinates['y1']
            box = pg.QtGui.QGraphicsRectItem(x0, y0, 
                                             self.parent.binning_bin_size, 
                                             self.parent.binning_bin_size)
            box.setPen(pg.mkPen(self.selected_color['pen']))
            box.setBrush(pg.mkBrush(self.selected_color['brush']))
            self.parent.fitting_ui.image_view.addItem(box)
            list_bins_selected_rect_item.append(box)
            
        self.parent.fitting_ui.list_bins_selected_item = list_bins_selected_rect_item
    
    def update_bins_locked(self):
        table_dictionary = self.parent.fitting_ui.table_dictionary
        nbr_row = len(table_dictionary)

        list_bins_locked_item = []
        for _row in np.arange(nbr_row):
            _widget_lock = self.parent.fitting_ui.ui.value_table.cellWidget(_row, 0)
            if _widget_lock.isChecked():
                _coordinates = table_dictionary[str(_row)]['bin_coordinates']            
                x0 = _coordinates['x0']
                x1 = _coordinates['x1']
                y0 = _coordinates['y0']
                y1 = _coordinates['y1']
                box = pg.QtGui.QGraphicsRectItem(x0, y0, 
                                                 self.parent.binning_bin_size, 
                                                 self.parent.binning_bin_size)
                box.setPen(pg.mkPen(self.lock_color['pen']))
                box.setBrush(pg.mkBrush(self.lock_color['brush']))
                self.parent.fitting_ui.image_view.addItem(box)
                list_bins_locked_item.append(box)
            
        self.parent.fitting_ui.list_bins_locked_item = list_bins_locked_item
    
    def retrieve_list_bin_selected(self, selection):
        list_bin_selected = []
        for _select in selection:
            top_row = _select.topRow()
            bottom_row = _select.bottomRow()
            for _row in np.arange(top_row, bottom_row + 1):
                list_bin_selected.append(_row)
                
        return list_bin_selected