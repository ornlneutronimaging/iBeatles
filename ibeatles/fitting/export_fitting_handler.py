import numpy as np
from qtpy.QtWidgets import QFileDialog, QApplication
from qtpy import QtCore
import os
import shutil

from ibeatles.fitting.fitting_functions import basic_fit, advanced_fit
from ibeatles.utilities.file_handler import FileHandler


class ExportFittingHandler(object):
    table = []
    x_axis = []

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):

        output_folder_name = self.select_and_create_output_folder()
        if output_folder_name == '':
            return

        # hourglass cursor
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        # load table
        self.load_table()

        # retrieve x-axis range selected
        x_axis = self.retrieve_x_axis()

        # loop over all bins
        for _key in self.table:
            _entry = self.table[_key]

            # create file name
            row_index = _entry['row_index']
            column_index = _entry['column_index']
            full_entry_file_name = self.build_entry_file_name(output_folder_name=output_folder_name,
                                                              row_index=row_index,
                                                              column_index=column_index)

            # retrieve exp y_axis
            exp_y_axis = self.retrieve_y_axis(_entry)

            # retrieve fitted y_axis
            d_spacing = _entry['d_spacing']['val']
            sigma = _entry['sigma']['val']
            alpha = _entry['alpha']['val']
            a1 = _entry['a1']['val']
            a2 = _entry['a2']['val']

            if self.parent.fitting_ui.ui.advanced_table_checkBox.isChecked():
                a5 = _entry['a5']['val']
                a6 = _entry['a6']['val']
            else:
                a5 = 'N/A'
                a6 = 'N/A'

            fit_y_axis = []
            for _x in x_axis:
                if self.parent.fitting_ui.ui.advanced_table_checkBox.isChecked():
                    _y = advanced_fit(_x, d_spacing, alpha, sigma, a1, a2, a5, a6)
                else:
                    _y = basic_fit(_x, d_spacing, alpha, sigma, a1, a2)
                fit_y_axis.append(_y)

            # export file
            metadata = ['# bin parameters']
            metadata.append('#   x0: {}'.format(self.xy_parameters['x0']))
            metadata.append('#   x1: {}'.format(self.xy_parameters['x1']))
            metadata.append('#   y0: {}'.format(self.xy_parameters['y0']))
            metadata.append('#   y1: {}'.format(self.xy_parameters['y1']))
            metadata.append('# fitting parameters')
            metadata.append('#   d_spacing: {}'.format(d_spacing))
            metadata.append('#   sigma: {}'.format(sigma))
            metadata.append('#   alpha: {}'.format(alpha))
            metadata.append('#   a1: {}'.format(a1))
            metadata.append('#   a2: {}'.format(a2))
            metadata.append('#   a5: {}'.format(a5))
            metadata.append('#   a6: {}'.format(a6))
            metadata.append('#')
            metadata.append('# lambda(Angstroms), experimental, fitting')

            data = list(zip(x_axis, exp_y_axis, fit_y_axis))

            FileHandler.make_ascii_file(metadata=metadata,
                                        data=data,
                                        output_file_name=full_entry_file_name)

        QApplication.restoreOverrideCursor()

    def build_entry_file_name(self, output_folder_name='', row_index=0, column_index=0):
        '''built the entry (bin number) file name'''
        return os.path.join(output_folder_name, 'bin_row' + str(row_index) + '_col' + str(column_index) + '.txt')

    def retrieve_y_axis(self, _entry):
        x0 = _entry['bin_coordinates']['x0']
        x1 = _entry['bin_coordinates']['x1']
        y0 = _entry['bin_coordinates']['y0']
        y1 = _entry['bin_coordinates']['y1']

        self.xy_parameters = {'x0': x0,
                              'y0': y0,
                              'x1': x1,
                              'y1': y1}

        data_2d = np.array(self.parent.data_metadata['normalized']['data'])
        _data = data_2d[:, x0:x1, y0:y1]
        inter1 = np.nanmean(_data, axis=1)
        bragg_edge = np.nanmean(inter1, axis=1)

        [left_index, right_index] = self.parent.fitting_bragg_edge_linear_selection

        return bragg_edge[left_index: right_index]

    def retrieve_x_axis(self):
        # index of selection in bragg edge plot
        [left_index, right_index] = self.parent.fitting_bragg_edge_linear_selection

        # retrieve image
        # data_2d = np.array(self.parent.data_metadata['normalized']['data'])
        full_x_axis = self.parent.fitting_ui.bragg_edge_data['x_axis']
        x_axis = np.array(full_x_axis[left_index: right_index], dtype=float)

        return x_axis

    def load_table(self):
        self.table = self.parent.table_dictionary

    def select_and_create_output_folder(self):
        '''select where to create the output fitting folder'''
        output_folder = self.parent.normalized_folder
        new_output_folder = str(QFileDialog.getExistingDirectory(self.parent,
                                                                 "Select Where to Create all the Fitted Bin Files....",
                                                                 output_folder))
        if new_output_folder:

            # define name of output folder
            default_folder_name = str(self.parent.ui.normalized_folder.text()) + '_bins_fit'
            full_folder_name = os.path.join(new_output_folder, default_folder_name)
            if os.path.exists(full_folder_name):
                shutil.rmtree(full_folder_name)
            else:
                os.mkdir(full_folder_name)

            return new_output_folder

        return ''
