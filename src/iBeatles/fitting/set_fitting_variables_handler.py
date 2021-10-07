from qtpy import QtGui, QtCore
from qtpy.QtWidgets import QTableWidgetItem
import numpy as np


class SetFittingVariablesHandler(object):
    colorscale_nbr_row = 15
    colorscale_cell_size = {'width': 75,
                            'height': 30}

    def __init__(self, grand_parent=None):
        self.grand_parent = grand_parent

    def get_variable_selected(self):
        if self.grand_parent.fitting_set_variables_ui.ui.d_spacing_button.isChecked():
            return 'd_spacing'
        elif self.grand_parent.fitting_set_variables_ui.ui.sigma_button.isChecked():
            return 'sigma'
        elif self.grand_parent.fitting_set_variables_ui.ui.alpha_button.isChecked():
            return 'alpha'
        elif self.grand_parent.fitting_set_variables_ui.ui.a1_button.isChecked():
            return 'a1'
        elif self.grand_parent.fitting_set_variables_ui.ui.a2_button.isChecked():
            return 'a2'
        elif self.grand_parent.fitting_set_variables_ui.ui.a5_button.isChecked():
            return 'a5'
        elif self.grand_parent.fitting_set_variables_ui.ui.a6_button.isChecked():
            return 'a6'

    def populate_table_with_variable(self, variable='d_spacing'):
        array_2d_values = self.create_array_of_variable(variable=variable)

        # retrieve min and max values
        if np.isnan(array_2d_values).any():
            min_value = np.NaN
            max_value = np.NaN
            mid_point = np.NaN
        else:
            min_value = np.nanmin(array_2d_values)
            max_value = np.nanmax(array_2d_values)
            mid_point = np.mean([min_value, max_value])

        # define colorscale table
        self.initialize_colorscale_table(min_value=min_value, max_value=max_value)

        [nbr_row, nbr_column] = np.shape(array_2d_values)
        for _row in np.arange(nbr_row):
            for _col in np.arange(nbr_column):
                _value = array_2d_values[_row, _col]
                _color = self.get_color_for_this_value(min_value=min_value,
                                                       max_value=max_value,
                                                       value=_value)
                _item = QTableWidgetItem(str(_value))
                _item.setBackground(_color)

                bin_index = _row + nbr_row * _col
                if self.is_bin_locked(bin_index=bin_index):
                    _gradient = QtGui.QRadialGradient(10, 10, 10, 20, 20)
                    _gradient.setColorAt(1, _color)
                    if self.is_bin_fixed(bin_index=bin_index, variable_name=variable):
                        _gradient.setColorAt(0.5, QtGui.QColor(255, 255, 255))
                    _gradient.setColorAt(0, QtGui.QColor(255, 0, 0, alpha=255))
                    _item.setBackground(QtGui.QBrush(_gradient))
                elif self.is_bin_activated(bin_index=bin_index):
                    _gradient = QtGui.QRadialGradient(10, 10, 10, 20, 20)
                    _gradient.setColorAt(1, _color)
                    if self.is_bin_fixed(bin_index=bin_index, variable_name=variable):
                        _gradient.setColorAt(0.5, QtGui.QColor(255, 255, 255))
                    _gradient.setColorAt(0, QtGui.QColor(0, 0, 255, alpha=255))
                    _item.setBackground(QtGui.QBrush(_gradient))
                else:
                    if self.is_bin_fixed(bin_index=bin_index, variable_name=variable):
                        _gradient = QtGui.QRadialGradient(10, 10, 10, 20, 20)
                        _gradient.setColorAt(1, _color)
                        _gradient.setColorAt(0, QtGui.QColor(255, 255, 255))
                        _item.setBackground(QtGui.QBrush(_gradient))

                if (_value > mid_point):
                    _foreground_color = QtGui.QColor(255, 255, 255, alpha=255)
                    _item.setTextColor(_foreground_color)

                self.grand_parent.fitting_set_variables_ui.ui.variable_table.setItem(_row, _col, _item)

    def is_bin_fixed(self, bin_index=0, variable_name='d_spacing'):
        table_dictionary = self.grand_parent.table_dictionary
        return table_dictionary[str(bin_index)][variable_name]['fixed']

    def is_bin_locked(self, bin_index=0):
        table_dictionary = self.grand_parent.table_dictionary
        return table_dictionary[str(bin_index)]['lock']

    def is_bin_activated(self, bin_index=0):
        table_dictionary = self.grand_parent.table_dictionary
        return table_dictionary[str(bin_index)]['active']

    def clear_colorscale_table(self):
        nbr_row = self.grand_parent.fitting_set_variables_ui.ui.colorscale_table.rowCount()
        for _row in np.arange(nbr_row):
            self.grand_parent.fitting_set_variables_ui.ui.colorscale_table.removeRow(0)

    def initialize_colorscale_table(self, min_value=0, max_value=1):
        self.clear_colorscale_table()

        nbr_row = self.colorscale_nbr_row
        step = (float(max_value) - float(min_value)) / (nbr_row - 1)
        mid_point = np.int(nbr_row / 2)
        _row = 0

        if (min_value == max_value):
            nbr_row = 1

        if np.isnan(step):
            nbr_row = 1

        for _index in np.arange(nbr_row - 1, -1, -1):
            self.grand_parent.fitting_set_variables_ui.ui.colorscale_table.insertRow(_row)
            self.grand_parent.fitting_set_variables_ui.ui.colorscale_table.setRowHeight(_row,
                                                                                  self.colorscale_cell_size['height'])
            self.grand_parent.fitting_set_variables_ui.ui.colorscale_table.setColumnWidth(_row,
                                                                                    self.colorscale_cell_size['width'])
            if np.isnan(step):
                _value = np.NaN
            else:
                _value = min_value + _index * step
            _color = self.get_color_for_this_value(min_value=min_value,
                                                   max_value=max_value,
                                                   value=_value)

            if np.isnan(_value):
                _item = QTableWidgetItem("nan")
            else:
                _item = QTableWidgetItem("{:04.2f}".format(_value))
            _item.setBackground(_color)
            _item.setTextAlignment(QtCore.Qt.AlignRight)
            if (_row < mid_point) and (nbr_row != 1):
                # font should be changed from black to white
                _foreground_color = QtGui.QColor(255, 255, 255, alpha=255)
                _item.setTextColor(_foreground_color)

            self.grand_parent.fitting_set_variables_ui.ui.colorscale_table.setItem(_row, 0, _item)
            _row += 1

    def get_color_for_this_value(self, min_value=0, max_value=1, value=0):
        if np.isnan(value):
            return QtGui.QColor(255, 255, 255, alpha=100)  # white
        elif max_value == min_value:
            return QtGui.QColor(250, 0, 0, alpha=255)  # red

        _ratio = (1 - (float(value) - float(min_value)) / (float(max_value) - float(min_value)))
        return QtGui.QColor(0, _ratio * 255, 0, alpha=255)

    def create_array_of_variable(self, variable='d_spacing'):
        table_dictionary = self.grand_parent.table_dictionary

        _table_selection = self.grand_parent.fitting_selection
        nbr_column = _table_selection['nbr_column']
        nbr_row = _table_selection['nbr_row']

        _array = np.zeros((nbr_row, nbr_column), dtype=float)

        for _entry in table_dictionary.keys():
            row_index = table_dictionary[_entry]['row_index']
            column_index = table_dictionary[_entry]['column_index']
            value = table_dictionary[_entry][variable]['val']
            _array[row_index, column_index] = value

        return _array

    def set_new_value_to_selected_bins(self, selection=[],
                                       variable_name='d_spacing',
                                       variable_value=0,
                                       table_nbr_row=0):

        table_dictionary = self.grand_parent.table_dictionary
        nbr_row = table_nbr_row

        for _select in selection:
            _left_column = _select.leftColumn()
            _right_column = _select.rightColumn()
            _top_row = _select.topRow()
            _bottom_row = _select.bottomRow()
            for _row in np.arange(_top_row, _bottom_row + 1):
                for _col in np.arange(_left_column, _right_column + 1):
                    _index = str(_row + _col * nbr_row)
                    if not table_dictionary[_index]['lock']:
                        table_dictionary[_index][variable_name]['val'] = float(variable_value)
                        table_dictionary[_index][variable_name]['err'] = np.NaN
            self.grand_parent.fitting_set_variables_ui.ui.variable_table.setRangeSelected(_select, False)

        self.grand_parent.table_dictionary = table_dictionary
        self.populate_table_with_variable(variable=variable_name)
