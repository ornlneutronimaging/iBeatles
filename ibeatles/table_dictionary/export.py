from qtpy.QtWidgets import QFileDialog
import logging
import pandas as pd


class Export:

    header = ['x0', 'y0', 'x1', 'y1', 'row_index', 'column_index',
              'lock', 'active',
              'fitting_confidence', 'd_spacing_value', 'd_spacing_err',
              'sigma_value', 'sigma_err',
              'intensity_value', 'intensity_err',
              'alpha_value', 'alpha_err',
              'a1_value', 'a1_err',
              'a2_value', 'a2_err',
              'a5_value', 'a5_err',
              'a6_value', 'a6_err']

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def run(self):
        logging.info("Exporting table")
        default_file_name = str(self.grand_parent.ui.normalized_folder.text()) + '_fitting_table.csv'
        table_file = QFileDialog.getSaveFileName(self.grand_parent,
                                                 'Select or Define Name of File!',
                                                 default_file_name,
                                                 "CSV (*.csv)")

        if table_file[0]:
            table_file = table_file[0]
            logging.info(f" table file selected: {table_file}")
            table_dictionary = self.grand_parent.march_table_dictionary
            o_table_formatted = FormatTableForExport(table=table_dictionary)
            pandas_data_frame = o_table_formatted.pandas_data_frame
            header = self.header
            pandas_data_frame.to_csv(table_file, header=header)
            logging.info(f" Table has been exporting in {table_file}")
        else:
            logging.info(" User canceled exporting table!")


class FormatTableForExport(object):
    pandas_data_frame = []

    def __init__(self, table={}):
        pandas_table = []

        for _key in table:
            _entry = table[_key]

            x0 = _entry['bin_coordinates']['x0']
            y0 = _entry['bin_coordinates']['y0']
            x1 = _entry['bin_coordinates']['x1']
            y1 = _entry['bin_coordinates']['y1']

            row_index = _entry['row_index']
            column_index = _entry['column_index']

            lock = _entry['lock']
            active = _entry['active']

            fitting_confidence = _entry['fitting_confidence']

            [d_spacing_val,
             d_spacing_err] = FormatTableForExport.get_val_err_fixed(_entry['d_spacing'])

            [sigma_val,
             sigma_err] = FormatTableForExport.get_val_err_fixed(_entry['sigma'])

            [intensity_val,
             intensity_err] = FormatTableForExport.get_val_err_fixed(_entry['intensity'])

            [alpha_val,
             alpha_err] = FormatTableForExport.get_val_err_fixed(_entry['alpha'])

            [a1_val,
             a1_err] = FormatTableForExport.get_val_err_fixed(_entry['a1'])

            [a2_val,
             a2_err] = FormatTableForExport.get_val_err_fixed(_entry['a2'])

            [a5_val,
             a5_err] = FormatTableForExport.get_val_err_fixed(_entry['a5'])

            [a6_val,
             a6_err] = FormatTableForExport.get_val_err_fixed(_entry['a6'])

            _row = [x0, x1, y0, y1,
                    row_index, column_index,
                    lock, active,
                    fitting_confidence,
                    d_spacing_val, d_spacing_err,
                    sigma_val, sigma_err,
                    intensity_val, intensity_err,
                    alpha_val, alpha_err,
                    a1_val, a1_err,
                    a2_val, a2_err,
                    a5_val, a5_err,
                    a6_val, a6_err,
                    ]

            pandas_table.append(_row)

        pandas_data_frame = pd.DataFrame.from_dict(pandas_table)
        self.pandas_data_frame = pandas_data_frame

    @staticmethod
    def get_val_err_fixed(item):
        return [item['val'], item['err']]
