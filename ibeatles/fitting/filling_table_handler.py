import numpy as np
from PyQt4 import QtGui
import pyqtgraph as pg


class FillingTableHandler(object):
    
    table_dictionary = {}
    
    selected_color = {'pen': (0,0,0,30),
                      'brush': (0,255,0,150)}

    lock_color = {'pen': (0,0,0,30),
                  'brush': (255,0,0,240)}
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def create_table_dictionary(self):
        '''
        this will define the corner position and index of each cell
        '''
        bin_size = self.parent.binning_bin_size
        pos = self.parent.binning_ui.pos
        
        # calculate outside real edges of bins
        min_max_xy = self.get_min_max_xy(pos)
        
        from_x = min_max_xy['x']['min']
        to_x = min_max_xy['x']['max']
        
        from_y = min_max_xy['y']['min']
        to_y = min_max_xy['y']['max']
        
        table_dictionary = {}
        _index = 0
        _index_col = 0
        for _x in np.arange(from_x, to_x, bin_size):
            _index_row = 0
            for _y in np.arange(from_y, to_y, bin_size):
                _str_index = str(_index)
                table_dictionary[_str_index] = {'bin_coordinates': {'x0': -1,
                                                                    'x1': -1,
                                                                    'y0': -1,
                                                                    'y1': -1},
                                                'selected_item': None,
                                                'locked_item': None,
                                                'row_index': _index_row,
                                                'column_index': _index_col,
                                                'selected': False,
                                                'lock': False,
                                                'fitting_confidence': -1,
                                                'd_spacing': {'val': -1, 'err': -1},
                                                'sigma': {'val': -1, 'err': -1},
                                                'intensity': {'val': -1, 'err': -1},
                                                'alpah': {'val': -1, 'err': -1},
                                                'a1': {'val': -1, 'err': -1},
                                                'a2': {'val': -1, 'err': -1},
                                                'a5': {'val': -1, 'err': -1},
                                                'a6': {'val': -1, 'err': -1}}   
                table_dictionary[_str_index]['bin_coordinates']['x0'] = _x
                table_dictionary[_str_index]['bin_coordinates']['x1'] = _x + bin_size
                table_dictionary[_str_index]['bin_coordinates']['y0'] = _y
                table_dictionary[_str_index]['bin_coordinates']['y1'] = _y + bin_size

                # create the box to show when bin is selected
                selection_box = pg.QtGui.QGraphicsRectItem(_x, _y, 
                                                           bin_size,
                                                           bin_size)
                selection_box.setPen(pg.mkPen(self.selected_color['pen']))
                selection_box.setBrush(pg.mkBrush(self.selected_color['brush']))
                table_dictionary[_str_index]['selected_item'] = selection_box

                # create the box to show when bin is locked
                lock_box = pg.QtGui.QGraphicsRectItem(_x, _y, 
                                                           bin_size,
                                                           bin_size)
                lock_box.setPen(pg.mkPen(self.lock_color['pen']))
                lock_box.setBrush(pg.mkBrush(self.lock_color['brush']))
                table_dictionary[_str_index]['locked_item'] = lock_box

                _index += 1
                _index_row += 1
                print("row index: {}".format(_index_row))

            _index_col += 1
                
        
        self.table_dictionary = table_dictionary
        self.parent.fitting_ui.table_dictionary = table_dictionary

        self.parent.fitting_selection['nbr_row'] = _index_row
        self.parent.fitting_selection['nbr_column'] = _index_col

    def fill_table(self):
        self.clear_table()

        table_dictionary = self.table_dictionary
        nbr_row = len(table_dictionary)
        
        value_table_ui = self.parent.fitting_ui.ui.value_table
        nbr_column = value_table_ui.columnCount()
                
        for _index in np.arange(nbr_row):
            _str_index = str(_index)
            _entry = table_dictionary[_str_index]
            
            # add new row
            value_table_ui.insertRow(_index)
            
            # add lock button in first cell (column: 0)
            _lock_button = QtGui.QCheckBox()
            _is_checked = _entry['lock']
            _lock_button.setChecked(_is_checked)
            _lock_button.stateChanged.connect(lambda state=0, 
                                              row=_index: self.parent.fitting_ui.lock_button_state_changed(state, row))
            
            value_table_ui.setCellWidget(_index, 0, _lock_button)
            
            # bin # (column: 1)
            _bin_number = QtGui.QTableWidgetItem("{:02}".format(_index))
            value_table_ui.setItem(_index, 1, _bin_number)
            
            # from column 2 -> nbr_column
            for _col in np.arange(2, nbr_column):
                _item = QtGui.QTableWidgetItem("")
                value_table_ui.setItem(_index, _col, _item)

    def clear_table(self):
        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
        for _row in np.arange(nbr_row):
            self.parent.fitting_ui.ui.value_table.removeRow(0)

    def get_min_max_xy(self, pos_array):
        min_x = 10000
        max_x = -1
        min_y = 10000
        max_y = -1
        
        for xy in pos_array:
            [_x, _y] = xy
            if _x < min_x:
                min_x = _x
            if _x > max_x:
                max_x = _x
            if _y < min_y:
                min_y = _y
            if _y > max_y:
                max_y = _y

        return {'x': {'min': min_x, 
                      'max': max_x},
                'y': {'min': min_y,
                      'max': max_y}
                }

