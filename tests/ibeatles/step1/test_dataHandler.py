from unittest import TestCase

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
        self.parent = MockParent()

    def test_import_files_from_folder(self):
        o_data = DataHandler(parent=self.parent)
        o_data.import_files_from_folder(folder='')
        self.assertTrue(True)
