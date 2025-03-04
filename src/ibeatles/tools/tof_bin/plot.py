import copy
import numpy as np

from src.ibeatles.tools.tof_bin.utilities.get import Get
from src.ibeatles.tools.utilities import TimeSpectraKeys

from src.ibeatles.tools.tof_bin import TO_MICROS_UNITS, TO_ANGSTROMS_UNITS
from src.ibeatles.tools import LAMBDA, MICRO, ANGSTROMS


class Plot:
    def __init__(self, parent=None):
        self.parent = parent

    def refresh_profile_plot_and_clear_bins(self):
        """
        this clear, remove all bin items and just replot the profile on the bin right imageView
        """
        x0 = self.parent.bin_roi["x0"]
        y0 = self.parent.bin_roi["y0"]
        width = self.parent.bin_roi["width"]
        height = self.parent.bin_roi["height"]

        self.parent.bin_profile_view.clear()  # clear previous plot
        if self.parent.dict_of_bins_item is not None:  # remove previous bins
            for _key in self.parent.dict_of_bins_item.keys():
                self.parent.bin_profile_view.removeItem(
                    self.parent.dict_of_bins_item[_key]
                )
            self.parent.dict_of_bins_item = None

        array_of_data = self.parent.images_array

        profile_signal = [
            np.mean(_data[y0 : y0 + height, x0 : x0 + width]) for _data in array_of_data
        ]
        # profile_signal = self.parent.profile_signal

        o_get = Get(parent=self.parent)
        time_spectra_x_axis_name = o_get.x_axis_selected()

        x_axis = copy.deepcopy(self.parent.time_spectra[time_spectra_x_axis_name])

        if time_spectra_x_axis_name == TimeSpectraKeys.file_index_array:
            x_axis_label = "file index"
        elif time_spectra_x_axis_name == TimeSpectraKeys.tof_array:
            x_axis *= TO_MICROS_UNITS  # to display axis in micros
            x_axis_label = "tof (" + MICRO + "s)"
        elif time_spectra_x_axis_name == TimeSpectraKeys.lambda_array:
            x_axis *= TO_ANGSTROMS_UNITS  # to display axis in Angstroms
            x_axis_label = LAMBDA + "(" + ANGSTROMS + ")"

        self.parent.bin_profile_view.plot(x_axis, profile_signal, pen="r", symbol="x")
        self.parent.bin_profile_view.setLabel("bottom", x_axis_label)
