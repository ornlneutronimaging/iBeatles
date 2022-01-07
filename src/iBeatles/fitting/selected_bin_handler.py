import numpy as np
import pyqtgraph as pg

from ..table_dictionary.table_dictionary_handler import TableDictionaryHandler
from ..fitting.fitting_functions import basic_fit, advanced_fit


class SelectedBinsHandler(object):
    selected_color = {'pen': (0, 0, 0, 30),
                      'brush': (0, 255, 0, 150)}

    lock_color = {'pen': (0, 0, 0, 30),
                  'brush': (255, 0, 0, 240)}

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def clear_all_selected_bins(self):
        list_bins = self.parent.list_bins_selected_item
        for _bin_ui in list_bins:
            self.parent.image_view.removeItem(_bin_ui)

    def clear_all_locked_bins(self):
        list_bins = self.parent.list_bins_locked_item
        for _bin_ui in list_bins:
            self.parent.image_view.removeItem(_bin_ui)

    def update_bins_selected(self):
        self.clear_all_selected_bins()
        table_dictionary = self.grand_parent.march_table_dictionary
        list_bins_selected_item = []
        for _index in table_dictionary.keys():
            box = table_dictionary[_index]['selected_item']
            if table_dictionary[_index]['active']:
                self.parent.image_view.addItem(box)
                list_bins_selected_item.append(box)
        self.parent.list_bins_selected_item = list_bins_selected_item

        # self.clear_all_selected_bins()
        # selection = self.parent.ui.value_table.selectedRanges()
        # list_bin_selected = self.retrieve_list_bin_selected(selection)

        # table_dictionary = self.parent.table_dictionary
        # nbr_row = len(table_dictionary)
        # bin_size = self.parent.binning_bin_size

        # list_bins_selected_rect_item = []
        # for _row in np.arange(nbr_row):
        # table_entry = table_dictionary[str(_row)]
        # if _row in list_bin_selected:
        # _coordinates = table_entry['bin_coordinates']
        # table_entry['selected'] = True
        # x0 = _coordinates['x0']
        # x1 = _coordinates['x1']
        # y0 = _coordinates['y0']
        # y1 = _coordinates['y1']
        # box = table_entry['selected_item']
        # self.parent.fitting_ui.image_view.addItem(box)
        # list_bins_selected_rect_item.append(box)
        # else:
        # table_entry['selected'] = False
        # table_dictionary[str(_row)] = table_entry

        # self.parent.table_dictionary = table_dictionary
        # self.parent.fitting_ui.list_bins_selected_item = list_bins_selected_rect_item

    def update_bins_locked(self, all_flag=True):
        self.clear_all_locked_bins()
        table_dictionary = self.grand_parent.march_table_dictionary
        list_bins_locked_item = []
        for _index in table_dictionary.keys():
            box = table_dictionary[_index]['locked_item']
            if table_dictionary[_index]['lock']:
                self.parent.image_view.addItem(box)
                list_bins_locked_item.append(box)
        self.parent.list_bins_locked_item = list_bins_locked_item

        # table_dictionary = self.parent.table_dictionary
        # nbr_row = len(table_dictionary)

        # bin_size = self.parent.binning_bin_size

        # list_bins_locked_item = []
        # for _row in np.arange(nbr_row):
        # table_entry = table_dictionary[str(_row)]
        # _widget_lock = self.parent.fitting_ui.ui.value_table.cellWidget(_row, 0)
        # if _widget_lock.isChecked():
        # _coordinates = table_entry['bin_coordinates']
        # table_entry['lock'] = True
        # x0 = _coordinates['x0']
        # x1 = _coordinates['x1']
        # y0 = _coordinates['y0']
        # y1 = _coordinates['y1']
        # box = table_entry['locked_item']
        # self.parent.fitting_ui.image_view.addItem(box)
        # list_bins_locked_item.append(box)
        # else:
        # table_entry['lock'] = False
        # table_dictionary[str(_row)] = table_entry

        # self.parent.table_dictionary = table_dictionary
        # self.parent.fitting_ui.list_bins_locked_item = list_bins_locked_item

    def retrieve_list_bin_selected(self, flag_name='active'):
        """this is looking at the table_dictionary and the flag of the 'active' or 'lock' key
        item to figure out if the row is checked or not"""

        list_bin_selected = []

        # if self.parent.bragg_edge_active_button_status:
        #     flag_name = 'active'
        # else:
        #     flag_name = 'lock'

        table_dictionary = self.grand_parent.march_table_dictionary
        for _index in table_dictionary:
            if table_dictionary[_index][flag_name]:
                list_bin_selected.append(_index)

        list_bin_selected.sort()
        return list_bin_selected

    def update_bragg_edge_plot(self):
        self.parent.bragg_edge_plot.clear()

        if self.grand_parent.display_active_row_flag:
            flag_name = 'active'
        else:
            flag_name = 'lock'
        list_bin_selected = self.retrieve_list_bin_selected(flag_name=flag_name)

        if list_bin_selected == []:
            return

        table_dictionary = self.grand_parent.march_table_dictionary

        # retrieve image
        data_2d = np.array(self.grand_parent.data_metadata['normalized']['data'])

        # isolate data selected    data[x0:x1, y0:y1] for each bin selected
        bragg_edge_data = []
        # nbr_index_selected = len(list_bin_selected)
        for _bin_selected in list_bin_selected:
            _entry = table_dictionary[str(_bin_selected)]['bin_coordinates']
            x0 = _entry['x0']
            x1 = _entry['x1']
            y0 = _entry['y0']
            y1 = _entry['y1']
            _data = data_2d[:, x0:x1, y0:y1]
            # inter1 = np.sum(_data, axis=1)
            # final = np.sum(inter1, axis=1)
            inter1 = np.nanmean(_data, axis=1)
            final = np.nanmean(inter1, axis=1)
            bragg_edge_data.append(final)
            # if bragg_edge_data == []:
            # bragg_edge_data = final
            # else:
            # bragg_edge_data += final

        bragg_edge_data = np.nanmean(bragg_edge_data, axis=0)
        x_axis = self.grand_parent.normalized_lambda_bragg_edge_x_axis

        # save x and y-axis of bragg edge plot for initialization of a1, a2, a5 and a6
        self.parent.bragg_edge_data['x_axis'] = x_axis
        self.parent.bragg_edge_data['y_axis'] = bragg_edge_data

        self.parent.bragg_edge_plot.plot(x_axis, bragg_edge_data)
        # if self.parent.xaxis_button_ui['normalized']['file_index'].isChecked():
        # self.parent.fitting_ui.bragg_edge_plot.setLabel("bottom", "File Index")
        # elif self.parent.xaxis_button_ui['normalized']['tof'].isChecked():
        # self.parent.fitting_ui.bragg_edge_plot.setLabel("bottom", u"TOF (\u00B5s)")
        # else:
        self.parent.bragg_edge_plot.setLabel("bottom", u'\u03BB (\u212B)')
        self.parent.bragg_edge_plot.setLabel("left", "Average Counts")

        if self.grand_parent.fitting_bragg_edge_linear_selection == []:
            linear_region_left_index = 0
            linear_region_right_index = len(x_axis) - 1
            self.grand_parent.fitting_bragg_edge_linear_selection = [linear_region_left_index,
                                                                     linear_region_right_index]

        else:
            [linear_region_left_index, linear_region_right_index] = \
                self.grand_parent.fitting_bragg_edge_linear_selection

        lr_left = x_axis[linear_region_left_index]
        lr_right = x_axis[linear_region_right_index]

        linear_region_range = [lr_left, lr_right]

        if self.parent.fitting_lr is None:

            lr = pg.LinearRegionItem(values=linear_region_range,
                                     orientation='vertical',
                                     brush=None,
                                     movable=True,
                                     bounds=None)
            lr.setZValue(-10)
            lr.sigRegionChangeFinished.connect(self.parent.bragg_edge_linear_region_changed)
            lr.sigRegionChanged.connect(self.parent.bragg_edge_linear_region_changing)
            self.parent.bragg_edge_plot.addItem(lr)
            self.parent.fitting_lr = lr

        else:

            lr = self.parent.fitting_lr
            lr.setRegion(linear_region_range)
            self.parent.bragg_edge_plot.addItem(lr)

        display_fitting = True
        if display_fitting:

            o_table = TableDictionaryHandler(grand_parent=self.grand_parent,
                                             parent=self.parent)
            parameters = o_table.get_average_parameters_activated()

            _advanced_fitting_mode = self.parent.ui.advanced_table_checkBox.isChecked()

            d_spacing = parameters['d_spacing']
            alpha = parameters['alpha']
            sigma = parameters['sigma']
            a1 = parameters['a1']
            a2 = parameters['a2']
            if _advanced_fitting_mode:
                a5 = parameters['a5']
                a6 = parameters['a6']

            if np.isnan(d_spacing) or np.isnan(alpha) or np.isnan(sigma) or np.isnan(a1) or np.isnan(a2):
                return

            fit_x_axis = np.linspace(lr_left, lr_right, num=100)
            if _advanced_fitting_mode:
                fit_y_axis = [advanced_fit(x, d_spacing, alpha, sigma, a1, a2,
                                           a5,
                                           a6) for x in fit_x_axis]
            else:
                fit_y_axis = [basic_fit(x, d_spacing, alpha, sigma, a1, a2) for x in fit_x_axis]

            # fit_y_axis *= nbr_index_selected #FIXME

            self.parent.bragg_edge_plot.plot(fit_x_axis, fit_y_axis, pen='r')
