from qtpy.QtWidgets import QFileDialog
import os
import logging
import numpy as np

from NeuNorm.normalization import Normalization

from src.iBeatles import DataType
from src.iBeatles.step6 import ParametersToDisplay
from src.iBeatles.step6.get import Get


class Export:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        self.working_dir = os.path.dirname(os.path.abspath((self.grand_parent.data_metadata[DataType.normalized][
            'folder'])))

    def _make_image_base_name(self, normalized_folder, ext='tiff', parameters=ParametersToDisplay.d):
        base_file_name = os.path.basename(normalized_folder) + "_" + parameters + f".{ext}"
        return base_file_name

    def export(self):
        output_folder = str(QFileDialog.getExistingDirectory(self.grand_parent,
                                                             "Select where to save the d and strain mapping images",
                                                             self.working_dir))

        if output_folder:

            output_folder = os.path.abspath(output_folder)
            o_get = Get(parent=self.parent)

            # d_spacing
            d_spacing_file_name = self._make_image_base_name(output_folder)
            full_d_output_file_name = os.path.join(output_folder, d_spacing_file_name)
            d_array = o_get.d_array()

            o_norm = Normalization()
            o_norm.load(data=d_array, notebook=False)
            o_norm.data['sample']['file_name'][0] = self.working_dir
            o_norm.export(data_type='sample', folder=output_folder)

            # dxchange.write_tiff(d_array, full_d_output_file_name, dtype=float)
            logging.info(f"Export d_spacing: {full_d_output_file_name}")

            # strain mapping
            strain_mapping_file_name = self._make_image_base_name(
                    output_folder, parameters=ParametersToDisplay.strain_mapping)
            full_strain_output_file_name = os.path.join(output_folder, strain_mapping_file_name)
            strain_mapping_array = o_get.strain_mapping()
            # dxchange.write_tiff(strain_mapping_array, full_strain_output_file_name, dtype=float)
            logging.info(f"Export strain mapping: {full_strain_output_file_name}")

