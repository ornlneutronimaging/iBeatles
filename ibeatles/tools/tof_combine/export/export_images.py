from qtpy.QtWidgets import QFileDialog
import logging
import os
import shutil

from NeuNorm.normalization import Normalization

from ibeatles.tools.tof_combine.utilities.get import Get
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.tools.tof_combine.utilities import TimeSpectraKeys
class ExportImages:
    output_folder = None

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def run(self):

        working_dir = self.parent.top_folder

        _folder = str(QFileDialog.getExistingDirectory(caption="Select Folder to ExportImages the Images",
                                                       directory=working_dir,
                                                       options=QFileDialog.ShowDirsOnly))

        if _folder == "":
            logging.info("User cancel export images!")
            return

        o_get = Get(parent=self.parent)
        nbr_folder = o_get.number_of_folders_we_want_to_combine()
        time_stamp = FileHandler.get_current_timestamp()
        output_folder = os.path.join(_folder, f"combined_{time_stamp}")
        self.output_folder = output_folder
        FileHandler.make_or_reset_folder(output_folder)
        logging.info(f"Combined images will be exported to {output_folder}!")

        # initialize progress bar
        self.parent.eventProgress.setMinimum(0)
        self.parent.eventProgress.setMaximum(nbr_folder-1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        # export the arrays
        combine_arrays = self.parent.combine_data
        for _index, _array in enumerate(combine_arrays):
            short_file_name = f"image_{_index:04d}"
            o_norm = Normalization()
            o_norm.load(data=_array)
            o_norm.data['sample']['file_name'][0] = short_file_name
            o_norm.export(folder=output_folder, data_type='sample', file_type='tif')
            self.parent.eventProgress.setValue(_index+1)

        # export time spectra file
        self.export_time_spectra_file()

        self.parent.eventProgress.setVisible(False)

    def export_time_spectra_file(self):
        """use the time spectra file from the first folder selected and export it to the output folder"""
        logging.info("Export time spectra file:")
        output_folder = self.output_folder

        # retrieve full path of the time spectra file from first folder selected
        full_path_time_spectra_file = self.parent.time_spectra[TimeSpectraKeys.file_name]

        logging.info(f" - time spectra file: {full_path_time_spectra_file}")
        logging.info(f" - to output folder: {output_folder}")

        # copy that spectra file to final location
        shutil.copy(full_path_time_spectra_file, output_folder)
