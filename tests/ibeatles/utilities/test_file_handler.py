from unittest import TestCase
import os
import glob

from ibeatles.utilities.file_handler import FileHandler


class TestDataHandler(TestCase):

    def setUp(self):
        _file_path = os.path.dirname(__file__)
        self.data_path = os.path.abspath(os.path.join(_file_path, '../../data/'))

    def test_get_file_extension(self):
        """assert that the file extension method works"""
        file_name_1 = "file_name_is_not_important.tiff"
        file_extension_returned = FileHandler.get_file_extension(file_name_1)
        self.assertEqual('.tiff', file_extension_returned)

        file_name_2 = "file_name_is_not_important.fits"
        file_extension_returned = FileHandler.get_file_extension(file_name_2)
        self.assertEqual('.fits', file_extension_returned)