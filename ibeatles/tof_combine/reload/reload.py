from ibeatles import DataType
from ibeatles.session import SessionSubKeys
from ibeatles.utilities.file_handler import FileHandler


class Reload:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def run(self, data_type=DataType.normalized, output_folder=None):

        if data_type == DataType.none:
            return

        if data_type == DataType.sample:
            logging.info(f"Reloading TOF combine data in {data_type}")
            return

        if data_type == DataType.ob:
            logging.info(f"Reloading TOF combine in {data_type}")
            return

        if data_type == DataType.normalized:
            logging.info(f"Reloading TOF combine in {data_type}")
            return

        list_tiff = FileHandler.get_list_of_tif(folder=output_folder)
        self.top_parent.session_dict[data_type][SessionSubKeys.list_files] = list_tiff

        # FIXME




        # number_of_file_created = 0
        # counts_array = []
        #
        # metadata_dict = {'sample_position': sample_position}
        # file_info_dict = {}
        #
        # for _index, _bin in enumerate(file_index_array):
        #
        #     self.logger.info(f"bin #: {_bin}")
        #
        #     if _bin == []:
        #         self.logger.info(f"-> empty bin, skipping.")
        #         self.parent.eventProgress.setValue(_index + 1)
        #         continue
        #
        #     short_file_name = f"image_{_index:04d}.tif"
        #     output_file_name = str(Path(_folder) / short_file_name)
        #     file_info_dict[short_file_name] = {'file_index': _bin,
        #                                        'tof': tof_array[_index],
        #                                        'lambda': lambda_array[_index]}
        #
        #     self.logger.info(f"-> output_file_name: {output_file_name}")
        #     number_of_file_created += 1
        #
        #     # we combine the file listed in _bin using the method
        #     _data_dict = o_statistics.extract_data_for_this_bin(list_runs=_bin)
        #     full_image = _data_dict['full_image']
        #     counts_array.append(int(np.sum(full_image)))
        #     o_norm = Normalization()
        #     o_norm.load(data=full_image)
        #     o_norm.data['sample']['file_name'][0] = os.path.basename(output_file_name)
        #     o_norm.export(folder=_folder, data_type='sample', file_type='tiff')
        #
        #     self.parent.eventProgress.setValue(_index+1)
        #
        # metadata_dict['files_infos'] = file_info_dict
        # metadata_file_name = str(Path(_folder) / "metadata.json")
        # with open(metadata_file_name, 'w') as json_file:
        #     json.dump(metadata_dict, json_file)
        #
        # # export the new time stamp file
        # self.export_time_stamp_file(counts_array=counts_array,
        #                             tof_array=self.parent.time_spectra[TimeSpectraKeys.tof_array],
        #                             file_index_array=file_index_array,
        #                             export_folder=_folder)
        #
        # self.parent.eventProgress.setVisible(False)
        # p = inflect.engine()
        # self.logger.info(f"Done exporting {number_of_file_created} " + p.plural("file", number_of_file_created) + "!")
        # show_status_message(parent=self.parent,
        #                     message=f"ExportImages to folder {_folder} ... Done!",
        #                     status=StatusMessageStatus.ready,
        #                     duration_s=5)

    # def export_time_stamp_file(self,
    #                            counts_array=None,
    #                            tof_array=None,
    #                            file_index_array=None,
    #                            export_folder=None):
    #     """
    #     modify the time_spectra file to mirror the new bins
    #     :param counts_array: total counts of the given bin
    #            tof_array: original tof_array (coming from original spectra file)
    #            file_index_array: bin index
    #            export_folder: where to export that new time stamp file
    #     :return: None
    #     """
    #     time_spectra_file_name = str(Path(export_folder) / "image_Spectra.txt")
    #     new_tof_array = []
    #     for _list_files_index in file_index_array:
    #         list_tof = [tof_array[_index] for _index in _list_files_index]
    #         new_tof_array.append(np.mean(list_tof))
    #
    #     file_content = ["shutter_time,counts"]
    #     for _tof, _counts in zip(new_tof_array, counts_array):
    #         file_content.append(f"{_tof},{_counts}")
    #
    #     FileHandler.make_ascii_file(data=file_content,
    #                                 output_file_name=time_spectra_file_name)
    #
    #     self.logger.info(f"Exported the new time spectra file: {time_spectra_file_name} ... Done!")
    #
