import numpy as np

try:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
except:
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore


class SetFittingVariablesHandler(object):
    
    colorscale_nbr_row = 15
    colorscale_cell_size = {'width': 75,
                            'height': 30}
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def populate_table_with_variable(self, variable='d_spacing'):
        array_2d_values = self.create_array_of_variable(variable=variable)
        
        # retrieve min and max values
        min_value = np.nanmin(array_2d_values)
        max_value = np.nanmax(array_2d_values)
        
        # define colorscale table
        self.initialize_colorscale_table(min_value=min_value, max_value=max_value)
        
        [nbr_row, nbr_column] = np.shape(array_2d_values)
        for _row in np.arange(nbr_row):
            for _col in np.arange(nbr_column):
                _value = array_2d_values[_row, _col]
                _color = self.get_color_for_this_value(min_value = min_value,
                                                       max_value = max_value,
                                                       value = _value)
                _item = QtGui.QTableWidgetItem(str(_value))
                _item.setBackgroundColor(_color)
                self.parent.fitting_set_variables_ui.ui.variable_table.setItem(_row, _col, _item)

    def clear_colorscale_table(self):
        nbr_row = self.parent.fitting_set_variables_ui.ui.colorscale_table.rowCount()
        for _row in np.arange(nbr_row):
            self.parent.fitting_set_variables_ui.ui.colorscale_table.removeRow(0)

    def initialize_colorscale_table(self, min_value=0, max_value=1):
        self.clear_colorscale_table()

        nbr_row = self.colorscale_nbr_row
        step = (float(max_value) - float(min_value))/(nbr_row)
        mid_point = np.int(nbr_row / 2)
        _row = 0
        
        if (min_value == max_value) and (min_value == -1):
            nbr_row = 1
        
        for _index in np.arange(nbr_row-1, -1, -1):
            self.parent.fitting_set_variables_ui.ui.colorscale_table.insertRow(_row)
            self.parent.fitting_set_variables_ui.ui.colorscale_table.setRowHeight(_row, 
                                                                                     self.colorscale_cell_size['height'])
            self.parent.fitting_set_variables_ui.ui.colorscale_table.setColumnWidth(_row, 
                                                                                    self.colorscale_cell_size['width'])
            _value = min_value + _index * step
            _color = self.get_color_for_this_value(min_value=min_value,
                                                   max_value=max_value,
                                                   value = _value)
            _item = QtGui.QTableWidgetItem("{:04.2f}".format(_value))
            _item.setBackgroundColor(_color)
            if (_row < mid_point) and (nbr_row != 1):
                #font should be changed from back to white
                _foreground_color = QtGui.QColor(255, 255, 255, alpha=255)
                _item.setTextColor(_foreground_color)
            
            self.parent.fitting_set_variables_ui.ui.colorscale_table.setItem(_row, 0, _item)
            _row += 1
            
        
    def get_color_for_this_value(self, min_value=0, max_value=1, value=0):
        if value == -1:
            return QtGui.QColor(255,  255, 255, alpha=100) #white
        elif max_value == min_value:
            return QtGui.QColor(250, 0, 0, alpha=255) #red
        
        _ratio = (1-(float(value) - float(min_value)) / (float(max_value) - float(min_value)))
        return QtGui.QColor(0,  _ratio*255, 0, alpha=255)
        
    def create_array_of_variable(self, variable='d_spacing'):
        table_dictionary = self.parent.table_dictionary
        
        _table_selection = self.parent.fitting_selection
        nbr_column = _table_selection['nbr_column']
        nbr_row = _table_selection['nbr_row']
        
        _array = np.zeros((nbr_row, nbr_column), dtype=float)
        
        print(np.shape(_array))
        print("nbr_column: {}".format(nbr_column))
        print("nbr_row: {}".format(nbr_row))
        
        for _entry in table_dictionary.keys():
            row_index = table_dictionary[_entry]['row_index']
            column_index = table_dictionary[_entry]['column_index']
            value = table_dictionary[_entry][variable]['val']
            _array[row_index, column_index] = value
            
        return _array