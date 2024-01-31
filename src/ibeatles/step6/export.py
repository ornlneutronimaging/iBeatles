from qtpy.QtWidgets import QFileDialog
import os
import logging
import h5py

from NeuNorm.normalization import Normalization

from src.ibeatles import DataType, FileType
from src.ibeatles.step6 import ParametersToDisplay
from src.ibeatles.step6.get import Get
from src.ibeatles.utilities.file_handler import FileHandler, create_full_export_file_name
from src.ibeatles.utilities.export import format_kropff_dict, format_kropff_table
from src.ibeatles.utilities.get import Get as UtilitiesGet
from src.ibeatles.fitting import FittingKeys


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

    def select_output_folder(self):
        output_folder = str(QFileDialog.getExistingDirectory(self.parent,
                                                             "Select where to export ...",
                                                              self.working_dir))
        return output_folder

    def image(self, d_spacing_image=False, strain_mapping_image=False, integrated_image=False, output_folder=None):

        if output_folder is None:
            output_folder = str(QFileDialog.getExistingDirectory(self.parent,
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

    def table(self, file_type=FileType.ascii, output_folder=None):

        if output_folder is None:
            output_folder = str(QFileDialog.getExistingDirectory(self.grand_parent,
                                                                 "Select where to export the table as an ASCII file",
                                                                 self.working_dir))

        if output_folder:

            output_folder = os.path.abspath(output_folder)
            output_file_name = create_full_export_file_name(os.path.join(output_folder, "strain_mapping_table"),
                                                            file_type)

            kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
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

    def hdf5(self, output_folder: str = None):
        output_folder = os.path.abspath(output_folder)
        # output_file_name = os.path.join(output_folder, "strain_mapping_table.txt")
        output_file_name = create_full_export_file_name(os.path.join(output_folder, "fitting"),
                                                        FileType.hdf5)

        logging.info(f"Exporting fitting table and images to hdf5 file {output_file_name}")

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        o_get = Get(parent=self.parent)
        o_get_utilities = UtilitiesGet(parent=self.grand_parent)

        integrated_image = o_get.integrated_image()
        strain_mapping_dict = o_get.strain_mapping_dictionary()
        formatted_dict = format_kropff_dict(table=kropff_table_dictionary,
                                            d_dict=self.parent.d_dict,
                                            strain_dict=strain_mapping_dict)

        with h5py.File(output_file_name, 'w') as f:
            entry = f.create_group('entry')

            # general infos
            d0 = o_get.active_d0()
            material_name = o_get.material_name()
            hkl_value = o_get.hkl_value()
            distance_source_detector = o_get_utilities.distance_source_detector()
            detector_offset = o_get_utilities.detector_offset()
            bin_size = o_get_utilities.bin_size()

            metadata_group = entry.create_group('metadata')
            metadata_group.create_dataset('d0', data=d0)
            metadata_group.create_dataset('hkl_value', data=hkl_value)
            metadata_group.create_dataset('material_name', data=material_name)
            metadata_group.create_dataset('distance_source_detector', data=distance_source_detector)
            metadata_group.create_dataset('detector_offset', data=detector_offset)
            metadata_group.create_dataset('bin_size', data=bin_size)

            # strain mapping dict
            strain_group = entry.create_group('strain mapping')
            for key in strain_mapping_dict.keys():
                key_group = strain_group.create_group(key)
                key_group.create_dataset('val', data=strain_mapping_dict[key]['val'])
                key_group.create_dataset('err', data=strain_mapping_dict[key]['err'])
                coordinate_group = key_group.create_group('bin coordinates')
                coordinate_group.create_dataset('x0', data=formatted_dict[key]['bin_coordinates']['x0'])
                coordinate_group.create_dataset('y0', data=formatted_dict[key]['bin_coordinates']['y0'])
                coordinate_group.create_dataset('x1', data=formatted_dict[key]['bin_coordinates']['x1'])
                coordinate_group.create_dataset('y1', data=formatted_dict[key]['bin_coordinates']['y1'])

            # fitting
            fitting_group = entry.create_group('fitting')

            # kropff
            kropff_group = fitting_group.create_group('kropff')

            for key in formatted_dict.keys():

                key_group = kropff_group.create_group(key)

                _item1 = formatted_dict[key]
                key_group.create_dataset('xaxis', data=_item1['xaxis'])
                key_group.create_dataset('yaxis', data=_item1['yaxis'])

                fitted_group = key_group.create_group('fitted')
                _item12 = _item1['fitted']

                high_tof_group = fitted_group.create_group('high_tof')
                _item123 = _item12['high_tof']
                if _item123['xaxis']:
                    high_tof_group.create_dataset('xaxis', data=_item123['xaxis'])
                    high_tof_group.create_dataset('yaxis', data=_item123['yaxis'])
                else:
                    high_tof_group.create_dataset('xaxis', data='None')
                    high_tof_group.create_dataset('yaxis', data='None')

                low_tof_group = fitted_group.create_group('low_tof')
                _item123 = _item12['low_tof']
                if _item123['xaxis']:
                    low_tof_group.create_dataset('xaxis', data=_item123['xaxis'])
                    low_tof_group.create_dataset('yaxis', data=_item123['yaxis'])
                else:
                    low_tof_group.create_dataset('xaxis', data='None')
                    low_tof_group.create_dataset('yaxis', data='None')

                bragg_peak_group = fitted_group.create_group('bragg_peak')
                _item123 = _item12['bragg_peak']
                if _item123['xaxis']:
                    bragg_peak_group.create_dataset('xaxis', data=_item123['xaxis'])
                    bragg_peak_group.create_dataset('yaxis', data=_item123['yaxis'])
                else:
                    bragg_peak_group.create_dataset('xaxis', data='None')
                    bragg_peak_group.create_dataset('yaxis', data='None')

                for _item in ['strain', 'd', 'a0', 'b0', 'ahkl', 'bhkl', 'tau', 'sigma', 'lambda_hkl']:
                    _group = fitted_group.create_group(_item)
                    _group.create_dataset('val', data=_item1[_item]['val'])
                    _group.create_dataset('err', data=_item1[_item]['err'])

                fitted_group.create_dataset('row_index', data=_item1[FittingKeys.row_index])
                fitted_group.create_dataset('column_index', data=_item1[FittingKeys.column_index])

                bragg_peak_threshold = fitted_group.create_group('bragg peak threshold')
                bragg_peak_threshold.create_dataset('left', data=_item1['bragg peak threshold']['left'])
                bragg_peak_threshold.create_dataset('right', data=_item1['bragg peak threshold']['right'])

            # integrated image
            integrated_image_group = entry.create_group('integrated normalized radiographs')
            integrated_image_group.create_dataset('2D array', data=integrated_image)
