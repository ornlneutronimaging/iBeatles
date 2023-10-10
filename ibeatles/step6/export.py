from qtpy.QtWidgets import QFileDialog
import os
import logging

from NeuNorm.normalization import Normalization

from ibeatles import DataType, FileType
from ibeatles.step6 import ParametersToDisplay
from ibeatles.step6.get import Get
from ibeatles.utilities.file_handler import FileHandler, create_full_export_file_name
from ibeatles.utilities.export import format_kropff_dict, format_kropff_table


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

    def image(self, d_spacing_image=False, strain_mapping_image=False, integrated_image=False):
        output_folder = str(QFileDialog.getExistingDirectory(self.grand_parent,
                                                             "Select where to export ...",
                                                              self.working_dir))

        if output_folder:

            output_folder = os.path.abspath(output_folder)
            o_get = Get(parent=self.parent)

            if d_spacing_image:
                d_spacing_file_name = Export._make_image_base_name(self.working_dir)
                full_d_output_file_name = os.path.join(output_folder, d_spacing_file_name)
                d_array = o_get.d_array()

                o_norm = Normalization()
                o_norm.load(data=d_array, notebook=False)
                o_norm.data['sample']['file_name'][0] = d_spacing_file_name
                o_norm.export(data_type='sample', folder=output_folder)
                logging.info(f"Export d_spacing: {full_d_output_file_name}")

            if strain_mapping_image:
                strain_mapping_file_name = Export._make_image_base_name(
                        self.working_dir, parameters=ParametersToDisplay.strain_mapping)
                full_strain_output_file_name = os.path.join(output_folder, strain_mapping_file_name)
                strain_mapping_array = o_get.strain_mapping()

                o_norm = Normalization()
                o_norm.load(data=strain_mapping_array, notebook=False)
                o_norm.data['sample']['file_name'][0] = strain_mapping_file_name
                o_norm.export(data_type='sample', folder=output_folder)
                logging.info(f"Export strain mapping: {full_strain_output_file_name}")

            if integrated_image:
                integrated_image_file_name = Export._make_image_base_name(self.working_dir,
                                                                          parameters=ParametersToDisplay.integrated_image)
                full_image_output_file_name = os.path.join(output_folder, integrated_image_file_name)
                integrated_image = o_get.integrated_image()

                o_norm = Normalization()
                o_norm.load(data=integrated_image, notebook=False)
                o_norm.data['sample']['file_name'][0] = integrated_image_file_name
                o_norm.export(data_type='sample', folder=output_folder)
                logging.info(f"Export strain mapping: {full_image_output_file_name}")

    def table(self, file_type=FileType.ascii):
        output_folder = str(QFileDialog.getExistingDirectory(self.grand_parent,
                                                             "Select where to export the table as an ASCII file",
                                                             self.working_dir))

        if output_folder:

            output_folder = os.path.abspath(output_folder)
            output_file_name = create_full_export_file_name(os.path.join(output_folder, "strain_mapping_table"),
                                                            file_type)

            kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
            d_dict = self.parent.d_dict
            o_get = Get(parent=self.parent)
            strain_mapping_dict = o_get.strain_mapping_dictionary()

            if file_type == FileType.ascii:
                formatted_table = format_kropff_table(table=kropff_table_dictionary,
                                                      d_dict=self.parent.d_dict,
                                                      strain_dict=strain_mapping_dict)
                FileHandler.make_ascii_file(data=formatted_table,
                                            output_file_name=output_file_name)
            else:
                formatted_dict = format_kropff_dict(table=kropff_table_dictionary,
                                                    d_dict=self.parent.d_dict,
                                                    strain_dict=strain_mapping_dict)
                FileHandler.make_json_file(data_dict=formatted_dict,
                                           output_file_name=output_file_name)

            logging.info(f"Exported {file_type} strain mapping table: {output_file_name}")

            # formatted_table = Export.format_kropff_table(table=kropff_table_dictionary,
            #                                              d_dict=d_dict,
            #                                              strain_dict=strain_mapping_dict)
            # FileHandler.make_ascii_file(data=formatted_table,
            #                             output_file_name=output_file_name)
            #
            # logging.info(f"Exported strain mapping table: {output_file_name}")
            # logging.info(f"formatted table: {formatted_table}")

    @staticmethod
    def format_kropff_table(table=None, d_dict={}, strain_dict={}):
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
                    _bin_x0, _bin_y0, _bin_x1, _bin_y1,
                    _lambda_hkl_val, _lambda_hkl_err,
                    _d_value, _d_err,
                    _strain_value, _strain_value_err]
            line = [str(_value) for _value in line]

            formatted_table.append(", ".join(line))

        return formatted_table
