from unittest import TestCase
import glob
import os

from ibeatles.utilities.load_data import LoadData


class TestLoadData(TestCase):

    def setUp(self):
        _file_path = os.path.dirname(__file__)
        self.data_path = os.path.abspath(os.path.join(_file_path, '../../data/sample_with_time_spectra/'))

    def test_load_not_supported_file_format(self):
        """Assert loading not supported file format raises error"""
        o_load = LoadData(list_of_files='*.txt', image_ext='.txt')
        self.assertRaises(TypeError, o_load.load)

    def test_load_fits(self):
        fits_file = glob.glob(os.path.join(self.data_path, '*.fits'))
        o_load = LoadData(list_of_files=fits_file, image_ext='.fits')
        o_load.load()
        data_loaded = o_load.image_array
