from qtpy.QtWidgets import QFileDialog
import os
import logging

from ibeatles import DataType, FileType
from ibeatles.step6 import ParametersToDisplay
from ibeatles.fitting.kropff.get import Get as KropffGet
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
            formatted_table = format_kropff_table(table=kropff_table_dictionary,
                                                  d_dict=self.parent.d_dict,
                                                  strain_dict=strain_mapping_dict)
            FileHandler.make_ascii_file(data=formatted_table,
                                        output_file_name=output_file_name)
        else:
            formatted_dict = format_kropff_dict(table=kropff_table_dictionary,
                                                d_dict=self.parent.d_dict,
                                                strain_dict=strain_mapping_dict,
                                                json_friendly=True)
            FileHandler.make_json_file(data_dict=formatted_dict,
                                       output_file_name=output_file_name)

        logging.info(f"Exported {file_type} strain mapping table: {output_file_name}")
