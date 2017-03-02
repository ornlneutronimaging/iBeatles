import numpy as np
from PyQt4 import QtGui
import pyqtgraph as pg


class FillingTableHandler(object):
    
    table_dictionary = {}
    advanced_mode_flag = True
    
    def __init__(self, parent=None):
        self.parent = parent
      
    def set_mode(self, advanced_mode=True):
        self.advaanced_mode_flag = advanced_mode
        list_header_table_advanced_columns = [8,9]
        list_value_table_advanced_columns = [13,14,15,16]

        self.parent.fitting_ui.ui.header_table.horizontalHeader().blockSignals(True)
        self.parent.fitting_ui.ui.value_table.horizontalHeader().blockSignals(True)

        # hide column a5 and a6
        for _col_index in list_header_table_advanced_columns:
            self.parent.fitting_ui.ui.header_table.setColumnHidden(_col_index, not advanced_mode)
        for _col_index in list_value_table_advanced_columns:
            self.parent.fitting_ui.ui.value_table.setColumnHidden(_col_index, not advanced_mode)

        self.parent.fitting_ui.ui.header_table.horizontalHeader().blockSignals(False)
        self.parent.fitting_ui.ui.value_table.horizontalHeader().blockSignals(False)
    
        #repopulate table
        self.fill_table()
      
    def fill_table(self):
        self.clear_table_ui()
        table_dictionary = self.parent.table_dictionary

        if table_dictionary is None:
            table_dictionary = self.table_dictionary
        nbr_row = len(table_dictionary)
        
        value_table_ui = self.parent.fitting_ui.ui.value_table
        nbr_column = value_table_ui.columnCount()

        self.parent.fitting_ui.ui.value_table.blockSignals(True)
                
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
            list_value = [_entry['fitting_confidence'],
                          _entry['d_spacing']['val'],
                          _entry['d_spacing']['err'],
                          _entry['sigma']['val'],
                          _entry['sigma']['err'],
                          _entry['intensity']['val'],
                          _entry['intensity']['err'],
                          _entry['alpha']['val'],
                          _entry['alpha']['err'],
                          _entry['a1']['val'],
                          _entry['a1']['err'],
                          _entry['a2']['val'],
                          _entry['a2']['err'],
                          _entry['a5']['val'],
                          _entry['a5']['err'],
                          _entry['a6']['val'],
                          _entry['a6']['err']]              

            for _local_index, _value in enumerate(list_value):
                self.set_item(table_ui = value_table_ui, 
                             row = _index, 
                             col = _local_index+2, 
                             value = _value)
            
            # if row is selected, select it
            if _entry['selected']:
                _selection = QtGui.QTableWidgetSelectionRange(_index, 0,
                                                              _index, nbr_column-1)
                value_table_ui.setRangeSelected(_selection, True)
            
        self.parent.fitting_ui.ui.value_table.blockSignals(False)
            
    def set_item(self, table_ui=None, row=0, col=0, value=""):
        item = QtGui.QTableWidgetItem(value)
        table_ui.setItem(row, col, item)

    def clear_table_ui(self):
        self.parent.fitting_ui.ui.value_table.blockSignals(True)
        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
        for _row in np.arange(nbr_row):
            self.parent.fitting_ui.ui.value_table.removeRow(0)
        self.parent.fitting_ui.ui.value_table.blockSignals(False)

    def clear_table(self):
        self.unselect_full_table()
        self.parent.fitting_ui.ui.value_table.blockSignals(True)
        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
        for _row in np.arange(nbr_row):
            self.parent.fitting_ui.ui.value_table.removeRow(0)
        self.parent.fitting_ui.ui.value_table.blockSignals(False)

        self.parent.fitting_ui.selection_in_value_table_changed()
