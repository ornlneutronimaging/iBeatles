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
        nbr_row = len(table_dictionary)
        bin_size = self.parent.binning_bin_size

        list_bins_selected_rect_item = []
        for _row in np.arange(nbr_row):
            table_entry = table_dictionary[str(_row)]
            if _row in list_bin_selected:
                _coordinates = table_entry['bin_coordinates']            
                table_entry['selected'] = True
                x0 = _coordinates['x0']
                x1 = _coordinates['x1']
                y0 = _coordinates['y0']
                y1 = _coordinates['y1']
                box = table_entry['selected_item']
                self.parent.fitting_ui.image_view.addItem(box)
                list_bins_selected_rect_item.append(box)
            else:
                table_entry['selected'] = False
            table_dictionary[str(_row)] = table_entry
        
        self.parent.fitting_ui.table_dictionary = table_dictionary
        self.parent.fitting_ui.list_bins_selected_item = list_bins_selected_rect_item
    
    def update_bins_locked(self):
        table_dictionary = self.parent.fitting_ui.table_dictionary
        nbr_row = len(table_dictionary)
        
        bin_size = self.parent.binning_bin_size

        list_bins_locked_item = []
        for _row in np.arange(nbr_row):
            table_entry = table_dictionary[str(_row)]
            _widget_lock = self.parent.fitting_ui.ui.value_table.cellWidget(_row, 0)
            if _widget_lock.isChecked():
                _coordinates = table_entry['bin_coordinates']            
                table_entry['lock'] = True
                x0 = _coordinates['x0']
                x1 = _coordinates['x1']
                y0 = _coordinates['y0']
                y1 = _coordinates['y1']
                box = table_entry['locked_item']
                self.parent.fitting_ui.image_view.addItem(box)
                list_bins_locked_item.append(box)
            else:
                table_entry['lock'] = False
            table_dictionary[str(_row)] = table_entry
            
        self.parent.fitting_ui.table_dictionary = table_dictionary
        self.parent.fitting_ui.list_bins_locked_item = list_bins_locked_item
    
    def retrieve_list_bin_selected(self, selection):
        list_bin_selected = []
        for _select in selection:
            top_row = _select.topRow()
            bottom_row = _select.bottomRow()
            for _row in np.arange(top_row, bottom_row + 1):
                list_bin_selected.append(_row)
                
        return list_bin_selected
    
    def update_bragg_edge_plot(self):
        selection = self.fitting_ui.ui.value_table.selectedRanges()
        self.parent.fitting_ui.bragg_edge_plot.clear()
        
        list_bin_selected = self.retrieve_list_bin_selected(selection)        
        table_dictionary = self.parent.fitting_ui.table_dictionary
        
        # retrieve image
        data_2d = np.array(self.parent.data_metadata['normalized']['data'])

        # isolate data selected    data[x0:x1, y0:y1] for each bin selected
        bragg_edget_data = []
        for _bin_selected in list_bin_selected:
            _entry = table_dictionary[str(_bin_selected)]['bin_coordinates']
            x0 = _entry['x0']
            x1 = _entry['x1']
            y0 = _entry['y0']
            y1 = _entry['y1']
            _data = data_2d[:, x0:x1, y0:y1]
            inter1 = np.sum(_data, axis=1)
            final = np.sum(inter1, axis=1)
            if bragg_edget_data == []:
                bragg_edget_data = final
            else:
                bragg_edget_data += final
                
        x_axis = self.parent.current_bragg_edge_x_axis['normalized']
        self.parent.fitting_ui.bragg_edge_plot.plot(x_axis, bragg_edget_data)