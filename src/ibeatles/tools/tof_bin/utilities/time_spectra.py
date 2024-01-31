from pathlib import Path
import numpy as np
import logging

from src.ibeatles.utilities.file_handler import FileHandler


def export_time_stamp_file(counts_array=None, tof_array=None, file_index_array=None, export_folder=None):
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

    FileHandler.make_ascii_file(
        data=file_content, output_file_name=time_spectra_file_name
    )

    logging.info(f"Exported the new time spectra file: {time_spectra_file_name} ... Done!")
