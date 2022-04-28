from qtpy.QtWidgets import QFileDialog
import numpy as np
import os
import pandas as pd

from ..utilities.table_handler import TableHandler

from ..fitting import fitting_handler
# from ibeatles.py.utilities.math_tools import get_random_value


class ColumnNameIndex:
    activate = 3
    lock = 2


class TableDictionaryHandler:
    selected_color = {'pen': (0, 0, 0, 30),
                      'brush': (0, 255, 0, 150)}

    lock_color = {'pen': (0, 0, 0, 30),
                  'brush': (255, 0, 0, 240)}

    # header = ['x0', 'y0', 'x1', 'y1', 'row_index', 'column_index', 'lock', 'active',
    #           'fitting_confidence', 'd_spacing_value', 'd_spacing_err', 'd_spacing_fixed',
    #           'sigma_value', 'sigma_err', '',
    #           'intensity_value', 'intensity_err', 'intensity_fixed',
    #           'alpha_value', 'alpha_err', 'alpha_fixed',
    #           'a1_value', 'a1_err', 'a1_fixed',
    #           'a2_value', 'a2_err', 'a2_fixed',
    #           'a5_value', 'a5_err', 'a5_fixed',
    #           'a6_value', 'a6_err', 'a6_fixed']

    def __init__(self, grand_parent=None, parent=None):
        self.grand_parent = grand_parent  # iBeatles main
        self.parent = parent   # fitting ui
        self.value_table_ui = self.parent.ui.value_table

    def fill_table_with_variable(self, variable_name='d_spacing', value=np.NaN, list_keys=[], all_keys=False):
        table_dictionary = self.grand_parent.march_table_dictionary
        if all_keys:
            list_keys = table_dictionary.keys()

        for _key in list_keys:
            table_dictionary[_key][variable_name]['val'] = value

        self.grand_parent.march_table_dictionary = table_dictionary

    def populate_table_dictionary_entry(self, index=0, array=[]):
        table_dictionary = self.grand_parent.march_table_dictionary

        table_dictionary[str(index)] = {'bin_coordinates': {'x0': array[0],
                                                            'x1': array[2],
                                                            'y0': array[1],
                                                            'y1': array[3]},
                                        'selected_item': None,
                                        'locked_item': None,
                                        'row_index': array[4],
                                        'column_index': array[5],
                                        'selected': False,
                                        'lock': array[6],
                                        'active': array[7],
                                        'fitting_confidence': array[8],
                                        'd_spacing': {'val': array[9],
                                                      'err': array[10],
                                                      'fixed': array[11]},
                                        'sigma': {'val': array[12],
                                                  'err': array[13],
                                                  'fixed': array[14]},
                                        'intensity': {'val': array[15],
                                                      'err': array[16],
                                                      'fixed': array[17]},
                                        'alpha': {'val': array[18],
                                                  'err': array[19],
                                                  'fixed': array[20]},
                                        'a1': {'val': array[21],
                                               'err': array[22],
                                               'fixed': array[23]},
                                        'a2': {'val': array[24],
                                               'err': array[25],
                                               'fixed': array[26]},
                                        'a5': {'val': array[27],
                                               'err': array[28],
                                               'fixed': array[29]},
                                        'a6': {'val': array[30],
                                               'err': array[31],
                                               'fixed': array[32]},
                                        }

        self.grand_parent.march_table_dictionary = table_dictionary

    # def initialize_parameters_from_session(self):
    #     session_table_dictionary = self.grand_parent.session_dict["fitting"]['march dollase']["table dictionary"]
    #     table_dictionary = self.grand_parent.march_table_dictionary
    #
    #     for _row in session_table_dictionary.keys():
    #         _entry = session_table_dictionary[_row]
    #         table_dictionary[_row]['lock'] = _entry['lock']
    #         table_dictionary[_row]['active'] = _entry['active']
    #         table_dictionary[_row]['fitting_confidence'] = _entry['fitting_confidence']
    #         table_dictionary[_row]['d_spacing'] = _entry['d_spacing']
    #         table_dictionary[_row]['sigma'] = _entry['sigma']
    #         table_dictionary[_row]['alpha'] = _entry['alpha']
    #         table_dictionary[_row]['a1'] = _entry['a1']
    #         table_dictionary[_row]['a2'] = _entry['a2']
    #         table_dictionary[_row]['a5'] = _entry['a5']
    #         table_dictionary[_row]['a6'] = _entry['a6']
    #
    #     lambda_range = self.grand_parent.session_dict["fitting"]["lambda range index"]
    #     if lambda_range:
    #         [lambda_min_index, lambda_max_index] = self.grand_parent.session_dict["fitting"]["lambda range index"]
    #         x_axis = self.grand_parent.session_dict["fitting"]["x_axis"]
    #
    #         lambda_min = x_axis[lambda_min_index]
    #         lambda_max = x_axis[lambda_max_index]
    #
    #         self.parent.ui.lambda_min_lineEdit.setText("{:4.2f}".format(lambda_min))
    #         self.parent.ui.lambda_max_lineEdit.setText("{:4.2f}".format(lambda_max))
    #         self.grand_parent.fitting_bragg_edge_linear_selection = [lambda_min_index, lambda_max_index]
    #
    #     transparency = self.grand_parent.session_dict['fitting']['transparency']
    #     self.parent.ui.slider.setValue(transparency)
    #
    #     self.grand_parent.display_active_row_flag = \
    #         self.grand_parent.session_dict['fitting']['march dollase']['plot active row flag']
    #     self.parent.ui.active_bins_button.setChecked(self.grand_parent.display_active_row_flag)
    #     self.parent.ui.locked_bins_button.setChecked(not self.grand_parent.display_active_row_flag)
    #
    #     self.grand_parent.march_table_dictionary = table_dictionary
    #     self.grand_parent.table_loaded_from_session = None

    def clear_y_axis_and_x_axis_from_kropff_table_dictionary(self):
        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        for _row in kropff_table_dictionary.keys():
            kropff_table_dictionary[_row]['yaxis'] = None
            kropff_table_dictionary[_row]['xaxis'] = None

    # def create_table_dictionary(self):
    #     '''
    #     this will define the corner position and index of each cell
    #     '''
    #     # if len(np.array(self.grand_parent.data_metadata['normalized']['data_live_selection'])) == 0:
    #     #     return
    #     #
    #     # if not self.grand_parent.march_table_dictionary == {}:
    #     #     return
    #
    #     bin_size = self.grand_parent.binning_roi[-1]
    #     pos = self.grand_parent.binning_line_view['pos']
    #
    #     # calculate outside real edges of bins
    #     min_max_xy = get_min_max_xy(pos)
    #
    #     from_x = min_max_xy['x']['min']
    #     to_x = min_max_xy['x']['max']
    #
    #     from_y = min_max_xy['y']['min']
    #     to_y = min_max_xy['y']['max']
    #
    #     march_table_dictionary = {}
    #     kropff_table_dictionary = {}
    #     _index = 0
    #     _index_col = 0
    #     for _x in np.arange(from_x, to_x, bin_size):
    #         _index_row = 0
    #         for _y in np.arange(from_y, to_y, bin_size):
    #             _str_index = str(_index)
    #
    #             kropff_table_dictionary[_str_index] = {'bin_coordinates': {'x0': _x,
    #                                                                        'x1': _x + bin_size,
    #                                                                        'y0': _y,
    #                                                                        'y1': _y + bin_size},
    #                                                    'yaxis': None,
    #                                                    'xaxis': None,
    #                                                    'selected_item': None,
    #                                                    'locked_item': None,
    #                                                    'row_index': _index_row,
    #                                                    'column_index': _index_col,
    #                                                    'selected': False,
    #                                                    'lock': False,
    #                                                    'active': False,
    #                                                    'a0': {'val': np.NaN,
    #                                                           'err': np.NaN},
    #                                                    'b0': {'val': np.NaN,
    #                                                           'err': np.NaN},
    #                                                    'ahkl': {'val': np.NaN,
    #                                                             'err': np.NaN},
    #                                                    'bhkl': {'val': np.NaN,
    #                                                             'err': np.NaN},
    #                                                    'lambda_hkl': {'val': np.NaN,
    #                                                                   'err': np.NaN},
    #                                                    'tau': {'val': np.NaN,
    #                                                            'err': np.NaN},
    #                                                    'sigma': {'val': np.NaN,
    #                                                              'err': np.NaN},
    #                                                    'bragg peak threshold': {'left': np.NaN,
    #                                                                             'right': np.NaN},
    #                                                    }
    #
    #             # create the box to show when bin is selected
    #             selection_box = pg.QtGui.QGraphicsRectItem(_x, _y,
    #                                                        bin_size,
    #                                                        bin_size)
    #             selection_box.setPen(pg.mkPen(self.selected_color['pen']))
    #             selection_box.setBrush(pg.mkBrush(self.selected_color['brush']))
    #             kropff_table_dictionary[_str_index]['selected_item'] = selection_box
    #
    #             march_table_dictionary[_str_index] = {'bin_coordinates': {'x0': _x,
    #                                                                       'x1': _x + bin_size,
    #                                                                       'y0': _y,
    #                                                                       'y1': _y + bin_size},
    #                                                    'selected_item': None,
    #                                                    'locked_item': None,
    #                                                    'row_index': _index_row,
    #                                                    'column_index': _index_col,
    #                                                    'selected': False,
    #                                                    'lock': False,
    #                                                    'active': False,
    #                                                    'fitting_confidence': np.NaN,
    #                                                    'd_spacing': {'val': np.NaN,
    #                                                                  'err': np.NaN,
    #                                                                  'fixed': False},
    #                                                    'sigma': {'val': np.NaN,
    #                                                              'err': np.NaN,
    #                                                              'fixed': False},
    #                                                    'intensity': {'val': np.NaN,
    #                                                                  'err': np.NaN,
    #                                                                  'fixed': False},
    #                                                    'alpha': {'val': np.NaN,
    #                                                              'err': np.NaN,
    #                                                              'fixed': False},
    #                                                    'a1': {'val': np.NaN,
    #                                                           'err': np.NaN,
    #                                                           'fixed': False},
    #                                                    'a2': {'val': np.NaN,
    #                                                           'err': np.NaN,
    #                                                           'fixed': False},
    #                                                    'a5': {'val': np.NaN,
    #                                                           'err': np.NaN,
    #                                                           'fixed': False},
    #                                                    'a6': {'val': np.NaN,
    #                                                           'err': np.NaN,
    #                                                           'fixed': False},
    #                                                   }
    #
    #             # march_table_dictionary[_str_index]['bin_coordinates']['x0'] = _x
    #             # march_table_dictionary[_str_index]['bin_coordinates']['x1'] = _x + bin_size
    #             # march_table_dictionary[_str_index]['bin_coordinates']['y0'] = _y
    #             # march_table_dictionary[_str_index]['bin_coordinates']['y1'] = _y + bin_size
    #
    #             # create the box to show when bin is selected
    #             selection_box = pg.QtGui.QGraphicsRectItem(_x, _y,
    #                                                        bin_size,
    #                                                        bin_size)
    #             selection_box.setPen(pg.mkPen(self.selected_color['pen']))
    #             selection_box.setBrush(pg.mkBrush(self.selected_color['brush']))
    #             march_table_dictionary[_str_index]['selected_item'] = selection_box
    #
    #             # create the box to show when bin is locked
    #             lock_box = pg.QtGui.QGraphicsRectItem(_x, _y,
    #                                                   bin_size,
    #                                                   bin_size)
    #             lock_box.setPen(pg.mkPen(self.lock_color['pen']))
    #             lock_box.setBrush(pg.mkBrush(self.lock_color['brush']))
    #             march_table_dictionary[_str_index]['locked_item'] = lock_box
    #
    #             _index += 1
    #             _index_row += 1
    #
    #         _index_col += 1
    #
    #     self.grand_parent.march_table_dictionary = march_table_dictionary
    #     self.grand_parent.kropff_table_dictionary = kropff_table_dictionary
    #
    #     self.grand_parent.fitting_selection['nbr_row'] = _index_row
    #     self.grand_parent.fitting_selection['nbr_column'] = _index_col

    def full_table_selection_tool(self, status=True):
        o_table = TableHandler(table_ui=self.value_table_ui)
        o_table.select_everything(status)

    def unselect_full_table(self):
        self.full_table_selection_tool(status=False)

    def select_full_table(self):
        self.full_table_selection_tool(status=True)

    # def get_average_parameters_activated(self):
    #     table_dictionary = self.grand_parent.march_table_dictionary
    #
    #     d_spacing = []
    #     alpha = []
    #     sigma = []
    #     a1 = []
    #     a2 = []
    #     a5 = []
    #     a6 = []
    #
    #     for _index in table_dictionary.keys():
    #         _entry = table_dictionary[_index]
    #
    #         if _entry['active']:
    #             _d_spacing = _entry['d_spacing']['val']
    #             _alpha = _entry['alpha']['val']
    #             _sigma = _entry['sigma']['val']
    #             _a1 = _entry['a1']['val']
    #             _a2 = _entry['a2']['val']
    #             _a5 = _entry['a5']['val']
    #             _a6 = _entry['a6']['val']
    #
    #             d_spacing.append(_d_spacing)
    #             alpha.append(_alpha)
    #             sigma.append(_sigma)
    #             a1.append(_a1)
    #             a2.append(_a2)
    #             a5.append(_a5)
    #             a6.append(_a6)
    #
    #     mean_d_spacing = self.get_mean_value(d_spacing)
    #     mean_alpha = self.get_mean_value(alpha)
    #     mean_sigma = self.get_mean_value(sigma)
    #     mean_a1 = self.get_mean_value(a1)
    #     mean_a2 = self.get_mean_value(a2)
    #     mean_a5 = self.get_mean_value(a5)
    #     mean_a6 = self.get_mean_value(a6)
    #
    #     return {'d_spacing': mean_d_spacing,
    #             'alpha': mean_alpha,
    #             'sigma': mean_sigma,
    #             'a1': mean_a1,
    #             'a2': mean_a2,
    #             'a5': mean_a5,
    #             'a6': mean_a6}

    # def get_mean_value(self, array=[]):
    #     if array == []:
    #         return np.NaN
    #     else:
    #         return np.mean(array)

    def import_table(self):
        default_file_name = str(self.grand_parent.ui.normalized_folder.text()) + '_fitting_table.csv'
        table_file = str(QFileDialog.getOpenFileName(self.grand_parent,
                                                     'Define Location and File Name Where to Export the Table!',
                                                     os.path.join(self.grand_parent.normalized_folder, default_file_name)))

        if table_file:
            pandas_data_frame = pd.read_csv(table_file)
            o_table = TableDictionaryHandler(grand_parent=self.grand_parent)

            numpy_table = pandas_data_frame.values
            # loop over each row in the pandas data frame
            for _index, _row_values in enumerate(numpy_table):
                o_table.populate_table_dictionary_entry(index=_index,
                                                        array=_row_values)

            o_fitting = fitting_handler.FittingHandler(grand_parent=self.grand_parent)
            o_fitting.fill_table()

    def is_at_least_one_row_activated(self):
        nbr_row = self.value_table_ui.rowCount()
        for _row in np.arange(nbr_row):
            if self.is_this_row_checked(row=_row, column=ColumnNameIndex.activate):
                return True
        return False

    def is_this_row_checked(self, row=0, column=2):
        widget = self.parent.ui.value_table.cellWidget(row, column)
        return widget.isChecked()
