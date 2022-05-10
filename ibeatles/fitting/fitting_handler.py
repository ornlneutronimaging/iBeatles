import numpy as np
import pyqtgraph as pg
import copy

from ..utilities import colors
from ..fitting.filling_table_handler import FillingTableHandler
from .selected_bin_handler import SelectedBinsHandler
from ..utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities
from .. import DataType
from . import FittingTabSelected, KropffTabSelected
from ..utilities.array_utilities import get_min_max_xy
from ibeatles.fitting import selected_color, lock_color


class FittingHandler:

    kropff_table_dictionary_template = {'yaxis': None,
                                        'xaxis': None,
                                        'fitted': {KropffTabSelected.high_tof: {'xaxis': None,
                                                                                'yaxis': None},
                                                   KropffTabSelected.low_tof: {'xaxis': None,
                                                                               'yaxis': None},
                                                   KropffTabSelected.bragg_peak: {'xaxis': None,
                                                                                  'yaxis': None}},
                                        'locked_item': None,
                                        'selected': False,
                                        'lock': False,
                                        'active': False,
                                        'a0': {'val': np.NaN,
                                               'err': np.NaN},
                                        'b0': {'val': np.NaN,
                                               'err': np.NaN},
                                        'ahkl': {'val': np.NaN,
                                                 'err': np.NaN},
                                        'bhkl': {'val': np.NaN,
                                                 'err': np.NaN},
                                        'lambda_hkl': {'val': np.NaN,
                                                       'err': np.NaN},
                                        'tau': {'val': np.NaN,
                                                'err': np.NaN},
                                        'sigma': {'val': np.NaN,
                                                  'err': np.NaN},
                                        'bragg peak threshold': {'left': None,
                                                                 'right': None},
                                        }

    def __init__(self, grand_parent=None, parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def display_image(self, data=[]):
        o_pyqt = PyqtgraphUtilities(parent=self.grand_parent,
                                    image_view=self.grand_parent.image_view,
                                    data_type=DataType.normalized)
        _state = o_pyqt.get_state()
        o_pyqt.save_histogram_level()

        if not (data == []):
            self.parent.data = data
            self.parent.image_view.setImage(data)
        else:
            if not self.grand_parent.data_metadata['normalized']['data_live_selection'] == []:
                data = np.array(self.grand_parent.data_metadata['normalized']['data_live_selection'])
                if len(data) == 0:
                    return
                else:
                    self.parent.image_view.setImage(data)
                    self.parent.data = data

        o_pyqt.set_state(_state)
        o_pyqt.reload_histogram_level()

    def display_roi(self):
        if len(np.array(self.grand_parent.data_metadata['normalized']['data_live_selection'])) == 0:
            return

        pos = self.grand_parent.binning_line_view['pos']
        adj = self.grand_parent.binning_line_view['adj']
        lines = self.grand_parent.binning_line_view['pen']

        if pos is None:
            return

        self.grand_parent.there_is_a_roi = True

        # define new transparency of roi
        transparency = self.parent.slider.value()
        self.grand_parent.fitting_transparency_slider_value = transparency
        lines = colors.set_alpha_value(lines=lines, transparency=transparency)

        if self.parent.line_view_fitting:
            self.parent.image_view.removeItem(self.parent.line_view_fitting)

        line_view_fitting = pg.GraphItem()
        self.parent.line_view_fitting = line_view_fitting
        self.parent.image_view.addItem(line_view_fitting)
        self.parent.line_view = line_view_fitting

        self.parent.line_view.setData(pos=pos,
                                      adj=adj,
                                      pen=lines,
                                      symbol=None,
                                      pxMode=False)

    def fill_table(self):
        if len(np.array(self.grand_parent.data_metadata['normalized']['data_live_selection'])) == 0:
            return

        if not self.grand_parent.there_is_a_roi:
            return

        self.create_table_dictionary()

        if self.grand_parent.table_loaded_from_session:
            self.initialize_parameters_from_session()

        o_fill_table = FillingTableHandler(grand_parent=self.grand_parent,
                                           parent=self.parent)
        o_fill_table.fill_table()

        if self.grand_parent.table_loaded_from_session:
            self.display_locked_active_bins()

    def display_locked_active_bins(self):
        o_bin_handler = SelectedBinsHandler(parent=self.parent,
                                            grand_parent=self.grand_parent)
        o_bin_handler.update_bins_locked()
        o_bin_handler.update_bins_selected()
        o_bin_handler.update_bragg_edge_plot()
        self.parent.min_or_max_lambda_manually_changed()
        self.parent.check_status_widgets()

    def initialize_parameters_from_session(self):
        self.initialize_marche_dollase_parameters_from_session()
        self.initialize_kropff_parameters_from_session()

    def initialize_kropff_parameters_from_session(self):
        session_table_dictionary = \
            self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff]["table dictionary"]
        table_dictionary = self.grand_parent.kropff_table_dictionary

        for _row in session_table_dictionary.keys():
            _entry = session_table_dictionary[_row]

            table_dictionary[_row]["bragg peak threshold"] = _entry["bragg_peak_threshold"]
            table_dictionary[_row]["a0"] = _entry["a0"]
            table_dictionary[_row]["b0"] = _entry["b0"]
            table_dictionary[_row]["ahkl"] = _entry["ahkl"]
            table_dictionary[_row]["bhkl"] = _entry["bhkl"]
            table_dictionary[_row]["lambda_hkl"] = _entry["lambda_hkl"]
            table_dictionary[_row]["tau"] = _entry["tau"]
            table_dictionary[_row]["sigma"] = _entry["sigma"]

        self.grand_parent.kropff_table_dictionary = table_dictionary

    def initialize_marche_dollase_parameters_from_session(self):
        session_table_dictionary = self.grand_parent.session_dict["fitting"]['march dollase']["table dictionary"]
        table_dictionary = self.grand_parent.march_table_dictionary

        for _row in session_table_dictionary.keys():
            _entry = session_table_dictionary[_row]
            table_dictionary[_row]['lock'] = _entry['lock']
            table_dictionary[_row]['active'] = _entry['active']
            table_dictionary[_row]['fitting_confidence'] = _entry['fitting_confidence']
            table_dictionary[_row]['d_spacing'] = _entry['d_spacing']
            table_dictionary[_row]['sigma'] = _entry['sigma']
            table_dictionary[_row]['alpha'] = _entry['alpha']
            table_dictionary[_row]['a1'] = _entry['a1']
            table_dictionary[_row]['a2'] = _entry['a2']
            table_dictionary[_row]['a5'] = _entry['a5']
            table_dictionary[_row]['a6'] = _entry['a6']

        lambda_range = self.grand_parent.session_dict["fitting"]["lambda range index"]
        if lambda_range:
            [lambda_min_index, lambda_max_index] = self.grand_parent.session_dict["fitting"]["lambda range index"]
            x_axis = self.grand_parent.session_dict["fitting"]["x_axis"]

            lambda_min = x_axis[lambda_min_index]
            lambda_max = x_axis[lambda_max_index]

            self.parent.ui.lambda_min_lineEdit.setText("{:4.2f}".format(lambda_min))
            self.parent.ui.lambda_max_lineEdit.setText("{:4.2f}".format(lambda_max))
            self.grand_parent.fitting_bragg_edge_linear_selection = [lambda_min_index, lambda_max_index]

        transparency = self.grand_parent.session_dict['fitting']['transparency']
        self.parent.ui.slider.setValue(transparency)

        self.grand_parent.display_active_row_flag = \
            self.grand_parent.session_dict['fitting']['march dollase']['plot active row flag']
        self.parent.ui.active_bins_button.setChecked(self.grand_parent.display_active_row_flag)
        self.parent.ui.locked_bins_button.setChecked(not self.grand_parent.display_active_row_flag)

        self.grand_parent.march_table_dictionary = table_dictionary
        self.grand_parent.table_loaded_from_session = None

    def create_table_dictionary(self):
        '''
        this will define the corner position and index of each cell
        '''
        # if len(np.array(self.grand_parent.data_metadata['normalized']['data_live_selection'])) == 0:
        #     return
        #
        # if not self.grand_parent.march_table_dictionary == {}:
        #     return

        bin_size = self.grand_parent.binning_roi[-1]
        pos = self.grand_parent.binning_line_view['pos']

        # calculate outside real edges of bins
        min_max_xy = get_min_max_xy(pos)

        from_x = min_max_xy['x']['min']
        to_x = min_max_xy['x']['max']

        from_y = min_max_xy['y']['min']
        to_y = min_max_xy['y']['max']

        march_table_dictionary = {}
        kropff_table_dictionary = {}
        _index = 0
        _index_col = 0
        for _x in np.arange(from_x, to_x, bin_size):
            _index_row = 0
            for _y in np.arange(from_y, to_y, bin_size):
                _str_index = str(_index)

                kropff_table_dictionary[_str_index] = copy.deepcopy(self.kropff_table_dictionary_template)
                kropff_table_dictionary[_str_index]['bin_coordinates'] = {'x0': _x,
                                                                          'x1': _x + bin_size,
                                                                          'y0': _y,
                                                                          'y1': _y + bin_size}
                kropff_table_dictionary[_str_index]['row_index'] = _index_row
                kropff_table_dictionary[_str_index]['column_index'] = _index_col
                kropff_table_dictionary[_str_index]['selected_item'] = None
                kropff_table_dictionary[_str_index]['lock'] = False

                # create the box to show when bin is selected
                selection_box = pg.QtGui.QGraphicsRectItem(_x, _y,
                                                           bin_size,
                                                           bin_size)
                selection_box.setPen(pg.mkPen(selected_color['pen']))
                selection_box.setBrush(pg.mkBrush(selected_color['brush']))
                kropff_table_dictionary[_str_index]['selected_item'] = selection_box

                march_table_dictionary[_str_index] = {'bin_coordinates': {'x0': _x,
                                                                          'x1': _x + bin_size,
                                                                          'y0': _y,
                                                                          'y1': _y + bin_size},
                                                       'selected_item': None,
                                                       'locked_item': None,
                                                       'row_index': _index_row,
                                                       'column_index': _index_col,
                                                       'selected': False,
                                                       'lock': False,
                                                       'active': False,
                                                       'fitting_confidence': np.NaN,
                                                       'd_spacing': {'val': np.NaN,
                                                                     'err': np.NaN,
                                                                     'fixed': False},
                                                       'sigma': {'val': np.NaN,
                                                                 'err': np.NaN,
                                                                 'fixed': False},
                                                       'intensity': {'val': np.NaN,
                                                                     'err': np.NaN,
                                                                     'fixed': False},
                                                       'alpha': {'val': np.NaN,
                                                                 'err': np.NaN,
                                                                 'fixed': False},
                                                       'a1': {'val': np.NaN,
                                                              'err': np.NaN,
                                                              'fixed': False},
                                                       'a2': {'val': np.NaN,
                                                              'err': np.NaN,
                                                              'fixed': False},
                                                       'a5': {'val': np.NaN,
                                                              'err': np.NaN,
                                                              'fixed': False},
                                                       'a6': {'val': np.NaN,
                                                              'err': np.NaN,
                                                              'fixed': False},
                                                      }

                # march_table_dictionary[_str_index]['bin_coordinates']['x0'] = _x
                # march_table_dictionary[_str_index]['bin_coordinates']['x1'] = _x + bin_size
                # march_table_dictionary[_str_index]['bin_coordinates']['y0'] = _y
                # march_table_dictionary[_str_index]['bin_coordinates']['y1'] = _y + bin_size

                # create the box to show when bin is selected
                selection_box = pg.QtGui.QGraphicsRectItem(_x, _y,
                                                           bin_size,
                                                           bin_size)
                selection_box.setPen(pg.mkPen(selected_color['pen']))
                selection_box.setBrush(pg.mkBrush(selected_color['brush']))
                march_table_dictionary[_str_index]['selected_item'] = selection_box

                # create the box to show when bin is locked
                lock_box = pg.QtGui.QGraphicsRectItem(_x, _y,
                                                      bin_size,
                                                      bin_size)
                lock_box.setPen(pg.mkPen(lock_color['pen']))
                lock_box.setBrush(pg.mkBrush(lock_color['brush']))
                march_table_dictionary[_str_index]['locked_item'] = lock_box

                _index += 1
                _index_row += 1

            _index_col += 1

        self.grand_parent.march_table_dictionary = march_table_dictionary
        self.grand_parent.kropff_table_dictionary = kropff_table_dictionary

        self.grand_parent.fitting_selection['nbr_row'] = _index_row
        self.grand_parent.fitting_selection['nbr_column'] = _index_col
