import numpy as np

try:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
except:
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore


class SetFittingVariablesHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def populate_table_with_variable(self, variable='d_spacing'):
        array_2d_values = self.create_array_of_variable(variable=variable)
        
        # retrieve min and max values
        min_value = np.nanmin(array_2d_values)
        max_value = np.nanmax(array_2d_values)
        
        [nbr_row, nbr_column] = np.shape(array_2d_values)
        for _row in np.arange(nbr_row):
            for _col in np.arange(nbr_column):
                _value = array_2d_values[_row, _col]
                print("value is {}".format(_value))
                _color = self.get_color_for_this_value(min_value = min_value,
                                                       max_value = max_value,
                                                       value = _value)
                _item = QtGui.QTableWidgetItem()
                _item.setBackgroundColor(_color)
                self.parent.fitting_set_variables_ui.ui.variable_table.setItem(_row, _col, _item)
        
    def get_color_for_this_value(self, min_value=0, max_value=1, value=0):
        if value == -1:
            return QtGui.QColor(255,  255, 255, alpha=100)
        elif max_value == min_value:
            return QtGui.QColor(250, 0, 0, alpha=255)
        
        _ratio = (float(value) - float(min_value)) / (float(max_value) - float(min_value))
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