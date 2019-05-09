from unittest import TestCase
import os
import glob

from ibeatles.step1.data_handler import DataHandler


class MockWidget:
    list_sample = None
    sample_folder = None
    list_open_beam = None
    open_beam_folder = None
    list_normalized = None
    normalized_folder = None
    time_spectra = None
    time_spectra_2 = None
    time_spectra_folder = None
    time_spectra_folder_2 = None


class MockParent:
    ui = MockWidget()


class TestDataHandler(TestCase):

    def setUp(self):
        self.mock_parent = MockParent()
        _file_path = os.path.dirname(__file__)
        self.data_path = os.path.abspath(os.path.join(_file_path, '../../data/'))

    def test_canceled_sample_import_files_from_folder(self):
        """User clicked CANCEL button when trying to import sample data files in step1"""
        o_data = DataHandler(parent=self.mock_parent)
        o_data.import_files_from_folder(folder='')
        self.assertTrue(o_data.user_canceled)

    def test_getting_list_of_sample_files_from_folder(self):
        """Checking that the correct list of files is retrieved from the folder"""
        o_data = DataHandler(parent=self.mock_parent)
        sample_path = os.path.join(self.data_path, 'sample_with_time_spectra')
        list_of_files = o_data.get_list_of_files(folder=sample_path)
        list_of_files.sort()
        self.assertEqual(len(list_of_files), 10)

        test_regular_expression = os.path.join(self.data_path, 'sample_with_time_spectra/*.fits')
        test_list_sample = glob.glob(test_regular_expression)
        test_list_sample.sort()
        self.assertTrue(list_of_files == test_list_sample)

        test_regular_expression_with_no_data = os.path.join(self.data_path, 'sample_without_fits/*.fits')
        test_list_sample = glob.glob(test_regular_expression_with_no_data)
        test_list_sample.sort()
        o_data = DataHandler(parent=self.mock_parent)
        sample_path = os.path.join(self.data_path, 'sample_without_fits')
        list_of_files = o_data.get_list_of_files(folder=sample_path)
        list_of_files.sort()
        self.assertEqual(test_list_sample, list_of_files)

    def test_time_spectra_automatically_retrieved(self):
        """Checking that the timespectra from the folder is correctly located or return empty string when not found"""
        o_data_with = DataHandler(parent=self.mock_parent)
        sample_path = os.path.join(self.data_path, 'sample_with_time_spectra')
        time_spectra_file = o_data_with.get_time_spectra_file(folder=sample_path)
        test_spectra_file = os.path.join(self.data_path, 'sample_with_time_spectra/Image019_Spectra.txt')
        self.assertEqual(time_spectra_file, test_spectra_file)

        o_data_without = DataHandler(parent=self.mock_parent)
        sample_path = os.path.join(self.data_path, 'sample_without_time_spectra')
        time_spectra_file = o_data_without.get_time_spectra_file(folder=sample_path)
        test_spectra_file = ''
        self.assertEqual(time_spectra_file, test_spectra_file)

    def test_image_type_is_correct(self):
        """making sure the method correctly retrieve the extension of the file"""
        list_image_test1 = ["name_not_important.tiff"]
        o_data = DataHandler(parent=self.mock_parent)
        ext_returned = o_data.get_image_type(list_image_test1)
        self.assertEqual(ext_returned, '.tiff')