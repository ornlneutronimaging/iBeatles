from qtpy.QtWidgets import QFileDialog
import logging
import os
from pathlib import Path
import inflect
import numpy as np
import json

from NeuNorm.normalization import Normalization

from src.ibeatles.session import SessionSubKeys
# from ..utilities.get import Get
# from ..utilities import TimeSpectraKeys
# from ..utilities.file_handler import FileHandler
# from ..bin.statistics import Statistics
# from ..utilities.status_message_config import StatusMessageStatus, show_status_message


class ExportImages:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent
        self.logger = logging.getLogger("maverick")

    def run(self):
        working_dir = self.top_parent.session[SessionSubKeys.top_folder]
        _folder = str(QFileDialog.getExistingDirectory(caption="Select Folder to ExportImages the Images",
                                                       directory=working_dir,
                                                       options=QFileDialog.ShowDirsOnly))

        if _folder == "":
            self.logger.info("User cancel export images!")
            return

        self.logger.info(f"Combined and Binned images will be exported to {_folder}!")

        # # use the combined data array
        # combine_arrays = self.parent.combine_data

        # retrieve the bin currently selected [[0],[1],[2,3],....]
        o_get = Get(parent=self.parent)
        bins_dict = o_get.current_bins_activated()
        number_of_bins = len(bins_dict[TimeSpectraKeys.file_index_array])

        # initialize progress bar
        self.parent.eventProgress.setMinimum(0)
        self.parent.eventProgress.setMaximum(number_of_bins-1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        sample_position = self.parent.session[SessionKeys.sample_position]

        file_index_array = bins_dict[TimeSpectraKeys.file_index_array]
        tof_array = bins_dict[TimeSpectraKeys.tof_array]
        lambda_array = bins_dict[TimeSpectraKeys.lambda_array]

        o_statistics = Statistics(parent=self.parent)
        self.logger.info(f"Images will be exported in: {_folder}")

        number_of_file_created = 0
        counts_array = []

        metadata_dict = {'sample_position': sample_position}
        file_info_dict = {}

        for _index, _bin in enumerate(file_index_array):

            self.logger.info(f"bin #: {_bin}")

            if _bin == []:
                self.logger.info(f"-> empty bin, skipping.")
                self.parent.eventProgress.setValue(_index + 1)
                continue

            short_file_name = f"image_{_index:04d}.tif"
            output_file_name = str(Path(_folder) / short_file_name)
            file_info_dict[short_file_name] = {'file_index': _bin,
                                               'tof': tof_array[_index],
                                               'lambda': lambda_array[_index]}

            self.logger.info(f"-> output_file_name: {output_file_name}")
            number_of_file_created += 1

            # we combine the file listed in _bin using the method
            _data_dict = o_statistics.extract_data_for_this_bin(list_runs=_bin)
            full_image = _data_dict['full_image']
            counts_array.append(int(np.sum(full_image)))
            o_norm = Normalization()
            o_norm.load(data=full_image)
            o_norm.data['sample']['file_name'][0] = os.path.basename(output_file_name)
            o_norm.export(folder=_folder, data_type='sample', file_type='tiff')

            self.parent.eventProgress.setValue(_index+1)

        metadata_dict['files_infos'] = file_info_dict
        metadata_file_name = str(Path(_folder) / "metadata.json")
        with open(metadata_file_name, 'w') as json_file:
            json.dump(metadata_dict, json_file)

        # export the new time stamp file
        self.export_time_stamp_file(counts_array=counts_array,
                                    tof_array=self.parent.time_spectra[TimeSpectraKeys.tof_array],
                                    file_index_array=file_index_array,
                                    export_folder=_folder)

        self.parent.eventProgress.setVisible(False)
        p = inflect.engine()
        self.logger.info(f"Done exporting {number_of_file_created} " + p.plural("file", number_of_file_created) + "!")
        show_status_message(parent=self.parent,
                            message=f"ExportImages to folder {_folder} ... Done!",
                            status=StatusMessageStatus.ready,
                            duration_s=5)

    def export_time_stamp_file(self,
                               counts_array=None,
                               tof_array=None,
                               file_index_array=None,
                               export_folder=None):
        """
        modify the time_spectra file to mirror the new bins
        :param counts_array: total counts of the given bin
               tof_array: original tof_array (coming from original spectra file)
               file_index_array: bin index
               export_folder: where to export that new time stamp file
        :return: None
        """
        time_spectra_file_name = str(Path(export_folder) / "image_Spectra.txt")
        new_tof_array = []
        for _list_files_index in file_index_array:
            list_tof = [tof_array[_index] for _index in _list_files_index]
            new_tof_array.append(np.mean(list_tof))

        file_content = ["shutter_time,counts"]
        for _tof, _counts in zip(new_tof_array, counts_array):
            file_content.append(f"{_tof},{_counts}")

        FileHandler.make_ascii_file(data=file_content,
                                    output_file_name=time_spectra_file_name)

        self.logger.info(f"Exported the new time spectra file: {time_spectra_file_name} ... Done!")

