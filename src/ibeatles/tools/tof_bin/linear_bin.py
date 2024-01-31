import numpy as np
import logging

from src.ibeatles.tools.utilities import TimeSpectraKeys


class LinearBin:

    linear_bins = {TimeSpectraKeys.tof_array: None,
                   TimeSpectraKeys.file_index_array: None,
                   TimeSpectraKeys.lambda_array: None}

    def __init__(self, parent=None, source_array=TimeSpectraKeys.file_index_array):
        self.parent = parent
        self.source_array = source_array
        self.logger = logging.getLogger('maverick')

    def create_linear_file_index_bin_array(self, bin_value=1):
        """creates the array of bins
        output will look like [[0,1],[2,3],[4,5]...]
        """
        original_array = np.array(self.parent.time_spectra[self.source_array])

        if self.source_array == TimeSpectraKeys.file_index_array:
            number_of_files = len(original_array)
            new_index_array = np.arange(0, number_of_files, bin_value)
            self.parent.full_bin_axis_requested = new_index_array

            linear_file_index_bin_array = [[] for _ in np.arange(len(new_index_array))]
            for _file_index, _bin in enumerate(original_array):
                result = np.where(_bin >= new_index_array)
                index = result[0][-1]
                linear_file_index_bin_array[index].append(_file_index)

            array_of_bins = linear_file_index_bin_array

        elif self.source_array == TimeSpectraKeys.tof_array:
            original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])

            new_tof_array = np.arange(original_tof_array[0], original_tof_array[-1], bin_value)
            new_tof_array = np.append(new_tof_array, new_tof_array[-1] + bin_value)
            self.parent.full_bin_axis_requested = new_tof_array

            linear_tof_bin_array = [[] for _ in np.arange(len(new_tof_array)-1)]
            for _tof_index, _bin in enumerate(original_tof_array):
                result = np.where(_bin >= new_tof_array)
                index = result[0][-1]
                linear_tof_bin_array[index].append(_tof_index)

            array_of_bins = linear_tof_bin_array

        elif self.source_array == TimeSpectraKeys.lambda_array:
            original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])
            new_lambda_array = np.arange(original_lambda_array[0], original_lambda_array[-1], bin_value)
            new_lambda_array = np.append(new_lambda_array, original_lambda_array[-1] + bin_value)
            self.parent.full_bin_axis_requested = new_lambda_array

            linear_lambda_bin_array = [[] for _ in np.arange(len(new_lambda_array)-1)]
            for _tof_index, _bin in enumerate(original_lambda_array):
                result = np.where(_bin >= new_lambda_array)
                index = result[0][-1]
                linear_lambda_bin_array[index].append(_tof_index)

            array_of_bins = linear_lambda_bin_array

        self.linear_bins[self.source_array] = array_of_bins
        self.logger.info(f"{self.source_array} array of bins: {array_of_bins}")

    def create_linear_lambda_array(self, lambda_value):
        """this method create the linear lambda array"""
        original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])
        linear_bins = self._create_general_linear_array(stepping=lambda_value,
                                                         original_array=original_lambda_array)
        self.linear_bins[TimeSpectraKeys.lambda_array] = linear_bins

    def _create_general_linear_array(self, stepping=None, original_array=None):
        """
        generic function used to create a linear bin array

        :param stepping: stepping bin value
        :param original_array: original array that will be used to determine when to stop
        :return: the linear bin array
        """
        left_value = original_array[0]
        right_value = stepping + left_value
        _linear_bins = []
        while right_value < original_array[-1]:
            _linear_bins.append(left_value)
            left_value = right_value
            right_value += stepping
        _linear_bins.append(right_value)
        return np.array(_linear_bins)

    def create_linear_bin_arrays(self):
        self.logger.info("Creating the other arrays")

        file_index_array_of_bins = self.linear_bins[self.source_array]

        original_tof_array = np.array(self.parent.time_spectra[TimeSpectraKeys.tof_array])
        original_lambda_array = np.array(self.parent.time_spectra[TimeSpectraKeys.lambda_array])

        linear_bins_tof_array = []
        linear_bins_lambda_array = []

        for _index, _bin in enumerate(file_index_array_of_bins):

            if _bin == []:
                linear_bins_tof_array.append([])
                linear_bins_lambda_array.append([])
                continue

            tof_bin = []
            lambda_bin = []
            for _file_index in _bin:
                tof_bin.append(original_tof_array[_file_index])
                lambda_bin.append(original_lambda_array[_file_index])
            linear_bins_tof_array.append(tof_bin)
            linear_bins_lambda_array.append(lambda_bin)

        self.linear_bins[TimeSpectraKeys.tof_array] = linear_bins_tof_array
        self.linear_bins[TimeSpectraKeys.lambda_array] = linear_bins_lambda_array
        self.linear_bins[TimeSpectraKeys.file_index_array] = file_index_array_of_bins

    def get_linear_file_index(self):
        return self.linear_bins[TimeSpectraKeys.file_index_array]

    def get_linear_tof(self):
        return self.linear_bins[TimeSpectraKeys.tof_array]

    def get_linear_lambda(self):
        return self.linear_bins[TimeSpectraKeys.lambda_array]
