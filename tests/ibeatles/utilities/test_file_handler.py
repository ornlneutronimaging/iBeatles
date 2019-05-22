from unittest import TestCase
from pathlib import Path

from ibeatles.utilities.file_handler import FileHandler


class TestDataHandler(TestCase):

    def setUp(self):
        _file_path = Path(__file__).parent
        self.data_path = _file_path.resolve().parent.parent.joinpath('data')

    def test_get_file_extension(self):
        """assert that the file extension method works"""
        file_name_1 = "file_name_is_not_important.tiff"
        file_extension_returned = FileHandler.get_file_extension(file_name_1)
        self.assertEqual('.tiff', file_extension_returned)

        file_name_2 = "file_name_is_not_important.fits"
        file_extension_returned = FileHandler.get_file_extension(file_name_2)
        self.assertEqual('.fits', file_extension_returned)

    def test_get_parent_folder(self):
        """assert get_parent_folder works"""
        returned_parent_folder = FileHandler.get_parent_folder(self.data_path)
        expected_parent_folder = self.data_path.parent.parts[-1]
        self.assertEqual(returned_parent_folder, expected_parent_folder)

    def test_get_parent_path(self):
        """asssert get_parent_path works"""
        returned_parent_path = FileHandler.get_parent_path(self.data_path)
        expected_parent_path = self.data_path.parent
        self.assertEqual(returned_parent_path, expected_parent_path)

    def test_get_base_filename(self):
        """assert get_base_filename works"""
        filename = self.data_path.joinpath("file_name_is_not_important.tiff")
        returned_base_filename = FileHandler.get_base_filename(filename)
        expected_base_filename = filename.name
        self.assertEqual(returned_base_filename, expected_base_filename)

    def test_cleanup_list_of_files(self):
        """assert that the list of files is correctly cleaned up"""
        base_number = 3
        list_of_files = ['file_to_keep_1.txt',
                         'file_to_keep_2.txt',
                         'file_to_keep_3.txt',
                         'file_not_to_keep_1.tiff',
                         'file_not_to_keep_2.tiff']
        returned_list = FileHandler.cleanup_list_of_files(list_of_files=list_of_files,
                                                          base_number=base_number)
        expected_list = ['file_to_keep_1.txt',
                         'file_to_keep_2.txt',
                         'file_to_keep_3.txt',
                         ]
        self.assertListEqual(returned_list, expected_list)
