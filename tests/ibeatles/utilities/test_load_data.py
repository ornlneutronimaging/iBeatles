from unittest import TestCase
import glob
import os
import numpy as np

from ibeatles.utilities.load_data import LoadData


class TestLoadData(TestCase):

    def setUp(self):
        _file_path = os.path.dirname(__file__)
        self.data_path = os.path.abspath(os.path.join(_file_path, '../../data/sample_with_time_spectra/'))

    def test_load_not_supported_file_format(self):
        """Assert loading not supported file format raises error"""
        o_load = LoadData(list_of_files='*.txt', image_ext='.txt')
        self.assertRaises(TypeError, o_load.load)

    # fits
    def test_load_single_fits_file(self):
        """Assert loading single fits file works"""
        fits_file = glob.glob(os.path.join(self.data_path, '*.fits'))
        image_array = LoadData.load_fits_file(fits_file[0])
        self.assertEqual(image_array.shape, (512, 512))

    def test_list_fits_files(self):
        """Assert loading list of fits works"""
        fits_file = glob.glob(os.path.join(self.data_path, '*.fits'))
        o_load = LoadData(list_of_files=fits_file[:2], image_ext='.fits')
        o_load.load_fits()
        data_loaded = o_load.image_array
        self.assertEqual(len(data_loaded), 2)
        self.assertEqual(np.shape(data_loaded), (2, 512, 512))

    def test_list_fits_files_from_main_caller(self):
        """Assert loading list of fits works"""
        fits_file = glob.glob(os.path.join(self.data_path, '*.fits'))
        o_load = LoadData(list_of_files=fits_file[:2], image_ext='.fits')
        o_load.load()
        data_loaded = o_load.image_array
        self.assertEqual(len(data_loaded), 2)
        self.assertEqual(np.shape(data_loaded), (2, 512, 512))

    # tiff
    # def test_load_