import numpy as np
import logging

from ibeatles.tools.utilities import TimeSpectraKeys


class LogBin:

    log_bins = {TimeSpectraKeys.tof_array: None,
                TimeSpectraKeys.file_index_array: None,
                TimeSpectraKeys.lambda_array: None}

    def __init__(self, parent=None, source_radio_button=TimeSpectraKeys.file_index_array):
        self.parent = parent
        self.source_array = source_radio_button

    def create_log_file_index_bin_array(self, bin_value=1):
        """
        This method create the 1D array of the bin positions
        :param source_array: either 'file_index', 'lambda' or 'tof'
        :param bin_value: value of the logarithmic bin
        """
        original_array = np.array(self.parent.time_spectra[self.source_array])

        # create the log bin array [value1, value2, value3, value4....]
        start_parameter = original_array[0]
        parameter_end = original_array[-1]
        new_bin_array = [start_parameter]
        parameter = start_parameter
        while parameter <= parameter_end:
            parameter += parameter * bin_value
            new_bin_array.append(parameter)

        # in case the last bin is smaller than the last array value
        if new_bin_array[-1] <= original_array[-1]:
            parameter += parameter * bin_value
            new_bin_array.append(parameter)

        self.parent.full_bin_axis_requested = new_bin_array

        logging.info(f"new bins array: {new_bin_array}")

        # we need to find where the file index end up in this array
        # will create [[0],[],[],[1],[2,3],[4,5,6,7],...]
        index_of_bin = [[] for _ in np.arange(len(new_bin_array)-1)]
        for _bin_index, _bin in enumerate(original_array):

            result = np.where(_bin >= new_bin_array)
            try:
                index = result[0][-1]
                index_of_bin[index].append(_bin_index)
            except IndexError:
                continue

        array_of_bins = index_of_bin

        self.log_bins[self.source_array] = array_of_bins
        logging.info(f"log {self.source_array} array of bins: {array_of_bins}")

    def create_log_bin_arrays(self):
        logging.info("Creating the other arrays")

        file_index_array_of_bins = self.log_bins[self.source_array]

        original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])
        original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])

        log_bins_tof_array = []
        log_bins_lambda_array = []

        for _index, _bin in enumerate(file_index_array_of_bins):

            if _bin == []:
                log_bins_tof_array.append([])
                log_bins_lambda_array.append([])
                continue

            tof_bin = []
            lambda_bin = []
            for _file_index in _bin:
                tof_bin.append(original_tof_array[_file_index])
                lambda_bin.append(original_lambda_array[_file_index])
            log_bins_tof_array.append(tof_bin)
            log_bins_lambda_array.append(lambda_bin)

        self.log_bins[TimeSpectraKeys.tof_array] = log_bins_tof_array
        self.log_bins[TimeSpectraKeys.lambda_array] = log_bins_lambda_array
        self.log_bins[TimeSpectraKeys.file_index_array] = file_index_array_of_bins

    def get_log_file_index(self):
        return self.log_bins[TimeSpectraKeys.file_index_array]

    def get_log_tof(self):
        return self.log_bins[TimeSpectraKeys.tof_array]

    def get_log_lambda(self):
        return self.log_bins[TimeSpectraKeys.lambda_array]