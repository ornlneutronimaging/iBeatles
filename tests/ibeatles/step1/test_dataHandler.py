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
        sample_path = os.path.join(self.data_path, 'sample')
        list_of_files = o_data.get_list_of_files(folder=sample_path)
        list_of_files.sort()

        self.assertEqual(len(list_of_files), 10)

        test_regular_expression = os.path.join(self.data_path, 'sample/*.fits')
        test_list_sample = glob.glob(test_regular_expression)
        test_list_sample.sort()

        self.assertTrue(list_of_files == test_list_sample)


