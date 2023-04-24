from PIL import Image
from astropy.io import fits
import os
import numpy as np
import time
import copy


class ImageHandler:

    metadata = {}
    data_type = 'tiff'
    data = []  # numpy array of image
    metadata = {}  # metadata dictionary
    filename = ''

    def __init__(self, parent=None, filename=None):
        self.data = []
        self.parent = parent

        # only first file loaded for now
        self.filename = filename
        self.retrieve_image_type()

    def retrieve_image_type(self):
        _file_0 = self.filename
        [_, file_extension] = os.path.splitext(_file_0)
        if (file_extension == '.tiff') or (file_extension == '.tif'):
            self.data_type = 'tiff'
        elif file_extension == '.fits':
            self.data_type = 'fits'
        else:
            raise ValueError("File Format not Supported!")

    def get_data(self):
        if self.filename == '':
            return []

        # if data not loaded yet
        if self.data == []:

            # only load first selected data
            # _file = self.filename
            if self.data_type == 'tiff':
                self.get_tiff_data()
            elif self.data_type == 'fits':
                self.get_fits_data()

            self.cleanup_data()

        return self.data

    def cleanup_data(self):
        _data = self.data

        where_are_nan = np.isnan(_data)
        _data[where_are_nan] = 0

        where_are_inf = np.isinf(_data)
        _data[where_are_inf] = 0
        self.data = _data

    def get_metadata(self, selected_infos_dict={}):
        if self.data == []:
            self.get_data()

        if self.data_type == 'tiff':
            self.get_tiff_metadata(selected_infos_dict)
        elif self.data_type == 'fits':
            self.get_fits_metadata(selected_infos_dict)

        return self.metadata

    def get_tiff_data(self):
        filename = self.filename
        _o_image = Image.open(filename)

        # metadata dict
        try:
            metadata = _o_image.tag_v2.as_dict()
        except AttributeError:
            metadata = None
        self.metadata = metadata

        # image
        data = np.array(_o_image)
        self.data = data

        _o_image.close()

    def get_fits_data(self):
        filename = self.filename
        self.data = copy.deepcopy(fits.getdata(filename))
        self.metadata = {}

    def get_tiff_metadata(self, selected_infos):

        _metadata = self.metadata

        # acquisition time
        try:  # new format
            acquisition_time_raw = _metadata[65000][0]
        except KeyError:
            acquisition_time_raw = _metadata[279][0]
        acquisition_time = time.ctime(acquisition_time_raw)
        selected_infos['acquisition_time']['value'] = acquisition_time

        # acquisition duration
        try:
            acquisition_duration_raw = _metadata[65021][0]
            [_, value] = acquisition_duration_raw.split(':')
        except KeyError:
            value = 'N/A'
        selected_infos['acquisition_duration']['value'] = value

        # image size
        try:
            sizeX_raw = _metadata[65028][0]
            [_, valueX] = sizeX_raw.split(':')
        except KeyError:
            valueX = _metadata[256]

        try:
            sizeY_raw = _metadata[65029][0]
            [_, valueY] = sizeY_raw.split(':')
        except KeyError:
            valueY = _metadata[257]
        image_size = "{} x {}".format(valueX, valueY)
        selected_infos['image_size']['value'] = image_size

        # image type
        bits = _metadata[258][0]
        selected_infos['image_type']['value'] = "{} bits".format(bits)

        # min counts
        min_value = np.min(self.data)
        selected_infos['min_counts']['value'] = "{}".format(min_value)

        # max counts
        max_value = np.max(self.data)
        selected_infos['max_counts']['value'] = "{}".format(max_value)

        self.metadata = selected_infos

    def get_fits_metadata(self, selected_infos):

        _metadata = self.metadata
        _filename = self.filename

        try:

            # acquisition time
            try:  # new format
                acquisition_time = _metadata['DATE']
            except KeyError:
                acquisition_time = time.ctime(os.path.getmtime(_filename))
            selected_infos['acquisition_duration']['value'] = acquisition_time

            # acquisition duration
            try:
                acquisition_duration = _metadata['EXPOSURE']
            except KeyError:
                acquisition_duration = _metadata['TiMEBIN']
            selected_infos['acquisition_time']['value'] = acquisition_duration

            # image size
            valueX = _metadata['NAXIS1']
            valueY = _metadata['NAXIS2']
            image_size = "{} x {}".format(valueX, valueY)
            selected_infos['image_size']['value'] = image_size

            # image type
            bits = _metadata['BITPIX']
            selected_infos['image_type']['value'] = "{} bits".format(bits)

            # min counts
            min_value = np.min(self.data)
            selected_infos['min_counts']['value'] = "{}".format(min_value)

            # max counts
            max_value = np.max(self.data)
            selected_infos['max_counts']['value'] = "{}".format(max_value)

        except KeyError:

            selected_infos['acquisition_duration']['value'] = 'N/A'
            selected_infos['acquisition_time']['value'] = 'N/A'
            selected_infos['image_size']['value'] = 'N/A'
            selected_infos['image_type']['value'] = 'N/A'
            selected_infos['min_counts']['value'] = 'N/A'
            selected_infos['max_counts']['value'] = 'N/A'

        self.metadata = selected_infos
