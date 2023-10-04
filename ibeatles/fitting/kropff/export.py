from qtpy.QtWidgets import QFileDialog
import os
import logging

from ibeatles import DataType
from ibeatles.step6 import ParametersToDisplay
from ibeatles.fitting.kropff.get import Get as KropffGet
from ibeatles.utilities.file_handler import FileHandler, create_full_export_file_name
from ibeatles.fitting import FittingKeys
from ibeatles.utilities.array_utilities import from_nparray_to_list
from ibeatles.fitting.kropff import SessionSubKeys


class FileType:
    ascii = "txt"
    json = 'json'


class Export:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        self.working_dir = os.path.dirname(os.path.abspath((self.grand_parent.data_metadata[DataType.normalized][
            'folder'])))

    @staticmethod
    def _make_image_base_name(normalized_folder, ext='tiff', parameters=ParametersToDisplay.d):
        base_file_name = os.path.basename(normalized_folder) + "_" + parameters + f".{ext}"
        return base_file_name

    def ascii(self):
        self.export_table(file_type=FileType.ascii)

    def json(self):
        self.export_table(file_type=FileType.json)

    def export_table(self, file_type: FileType = FileType.ascii):
        output_folder = str(QFileDialog.getExistingDirectory(self.grand_parent,
                                                             f"Select where to export the table as an {file_type} file",
                                                             self.working_dir))

        if output_folder:
            self.export_with_specified_file_type(file_type=file_type,
                                                 output_folder=output_folder)

    def export_with_specified_file_type(self,
                                        file_type: FileType = FileType.ascii,
                                        output_folder: str = None):

        # create output file  name
        output_folder = os.path.abspath(output_folder)
        # output_file_name = os.path.join(output_folder, "strain_mapping_table.txt")
        output_file_name = create_full_export_file_name(os.path.join(output_folder, "strain_mapping_table"),
                                                        file_type)

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary

        o_get = KropffGet(parent=self.parent,
                          grand_parent=self.grand_parent)
        strain_mapping_dict = o_get.strain_mapping_dictionary()

        if file_type == FileType.ascii:
            formatted_table = Export.format_kropff_table(table=kropff_table_dictionary,
                                                         d_dict=self.parent.d_dict,
                                                         strain_dict=strain_mapping_dict)
            FileHandler.make_ascii_file(data=formatted_table,
                                        output_file_name=output_file_name)
        else:
            formatted_dict = Export.format_kropff_dict(table=kropff_table_dictionary,
                                                       d_dict=self.parent.d_dict,
                                                       strain_dict=strain_mapping_dict)
            FileHandler.make_json_file(data_dict=formatted_dict,
                                       output_file_name=output_file_name)

        logging.info(f"Exported {file_type} strain mapping table: {output_file_name}")

    @staticmethod
    def format_kropff_dict(table: dict = None, d_dict: dict = None, strain_dict: dict = None):

        cleaned_table = {}
        for _row in table.keys():

            cleaned_table[_row] = {}
            cleaned_table[_row][FittingKeys.y_axis] = from_nparray_to_list(table[_row][FittingKeys.y_axis])
            cleaned_table[_row][FittingKeys.x_axis] = from_nparray_to_list(table[_row][FittingKeys.x_axis])

            cleaned_table[_row][SessionSubKeys.fitted] = {}

            cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof] = {}
            cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof][FittingKeys.x_axis] = \
                from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof][FittingKeys.x_axis])
            cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof][FittingKeys.y_axis] = \
                from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof][FittingKeys.y_axis])

            cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof] = {}
            cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof][FittingKeys.x_axis] = \
                from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof][FittingKeys.x_axis])
            cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof][FittingKeys.y_axis] = \
                from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof][FittingKeys.y_axis])

            cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak] = {}
            cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak][FittingKeys.x_axis] = \
                from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak][FittingKeys.x_axis])
            cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak][FittingKeys.y_axis] = \
                from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak][FittingKeys.y_axis])

            cleaned_table[_row]['strain'] = {'val': strain_dict[_row]['val'],
                                             'err': strain_dict[_row]['err']}
            cleaned_table[_row]['d'] = {'val': d_dict[_row]['val'],
                                        'err': d_dict[_row]['err']}

            cleaned_table[_row]['a0'] = table[_row]['a0']
            cleaned_table[_row]['b0'] = table[_row]['b0']
            cleaned_table[_row]['ahkl'] = table[_row]['ahkl']
            cleaned_table[_row]['bhkl'] = table[_row]['bhkl']
            cleaned_table[_row]['tau'] = table[_row]['tau']
            cleaned_table[_row]['sigma'] = table[_row]['sigma']
            cleaned_table[_row]['lambda_hkl'] = table[_row]['lambda_hkl']

            cleaned_table[_row]['bragg peak threshold'] = table[_row]['bragg peak threshold']

        return cleaned_table

    @staticmethod
    def format_kropff_table(table: dict = None, d_dict: dict = None, strain_dict: dict = None):
        formatted_table = ["#index, " +
                           "bin x0, bin y0, bin x1, bin y1, " +
                           "lambda hkl val, lambda hkl err, " +
                           "d value, d err, strain, strain error"]
        for _row in table.keys():
            _entry = table[_row]

            _row_index = _row
            _bin_x0 = _entry['bin_coordinates']['x0']
            _bin_y0 = _entry['bin_coordinates']['y0']
            _bin_x1 = _entry['bin_coordinates']['x1']
            _bin_y1 = _entry['bin_coordinates']['y1']

            _lambda_hkl_val = _entry['lambda_hkl']['val']
            _lambda_hkl_err = _entry['lambda_hkl']['err']

            _d_value = d_dict[_row]['val']
            _d_err = d_dict[_row]['err']

            _strain_value = strain_dict[_row]['val']
            _strain_value_err = strain_dict[_row]['err']

            line = [_row_index,
                    _bin_x0, _bin_y0, _bin_y0, _bin_y1,
                    _lambda_hkl_val, _lambda_hkl_err,
                    _d_value, _d_err,
                    _strain_value, _strain_value_err]
            line = [str(_value) for _value in line]

            formatted_table.append(", ".join(line))

        return formatted_table
