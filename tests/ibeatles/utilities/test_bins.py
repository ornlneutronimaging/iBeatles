from unittest import TestCase
import numpy as np

from ibeatles.utilities.bins import create_list_of_bins_from_selection
from ibeatles.utilities.bins import create_list_of_surrounding_bins
from ibeatles.utilities.bins import convert_bins_to_keys


class TestCreateListOfBinsFromSelection(TestCase):

    def test_case1(self):
        """assert simple case with only 1 bin"""
        top_row = 0
        bottom_row = 0
        left_column = 0
        right_column = 0
        list_bins = create_list_of_bins_from_selection(top_row=top_row,
                                                       bottom_row=bottom_row,
                                                       left_column=left_column,
                                                       right_column=right_column)
        expected_list_bins = [(0, 0)]
        expected_list_bins.sort()
        self.assertEqual(expected_list_bins, list_bins)

    def test_case2(self):
        """assert case with 2 bins in the same column"""
        top_row = 0
        bottom_row = 1
        left_column = 0
        right_column = 0
        list_bins = create_list_of_bins_from_selection(top_row=top_row,
                                                       bottom_row=bottom_row,
                                                       left_column=left_column,
                                                       right_column=right_column)
        expected_list_bins = [(0, 0), (1, 0)]
        expected_list_bins.sort()
        self.assertEqual(expected_list_bins, list_bins)

    def test_case3(self):
        """assert case with 2 bins in the same row"""
        top_row = 0
        bottom_row = 0
        left_column = 0
        right_column = 1
        list_bins = create_list_of_bins_from_selection(top_row=top_row,
                                                       bottom_row=bottom_row,
                                                       left_column=left_column,
                                                       right_column=right_column)
        expected_list_bins = [(0, 0), (0, 1)]
        expected_list_bins.sort()
        self.assertEqual(expected_list_bins, list_bins)

    def test_case4(self):
        """assert case with 4 bins """
        top_row = 0
        bottom_row = 0
        left_column = 0
        right_column = 1
        list_bins = create_list_of_bins_from_selection(top_row=top_row,
                                                       bottom_row=bottom_row,
                                                       left_column=left_column,
                                                       right_column=right_column)
        expected_list_bins = [(0, 0), (0, 1)]
        expected_list_bins.sort()
        self.assertEqual(expected_list_bins, list_bins)

    def test_case5(self):
        """assert case with 4 bins in the middle"""
        top_row = 5
        bottom_row = 6
        left_column = 3
        right_column = 4
        list_bins = create_list_of_bins_from_selection(top_row=top_row,
                                                       bottom_row=bottom_row,
                                                       left_column=left_column,
                                                       right_column=right_column)
        expected_list_bins = [(5, 3), (6, 3), (5, 4), (6, 4)]
        expected_list_bins.sort()
        self.assertEqual(expected_list_bins, list_bins)


class TestCreateListOfSurroundingBins(TestCase):

    def setUp(self):
        self.full_bin_width = 5
        self.full_bin_height = 10

    def test_case_top_left_corner(self):
        """assert case for top left corner"""
        central_bin = (0, 0)
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(1, 0), (1, 1), (0, 1)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)

    def test_case_bottom_left_middle(self):
        """assert case for left middle"""
        central_bin = (4, 0)
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(3, 0), (3, 1), (4, 1), (5, 1), (5, 0)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)

    def test_case_top_right_corner(self):
        """assert case for top right corner"""
        central_bin = (0, 4)
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(0, 3), (1, 3), (1, 4)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)

    def test_case_bottom_right_corner(self):
        """assert case for bottom right corner"""
        central_bin = (9, 4)
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(9, 3), (8, 3), (8, 4)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)

    def test_case_central_bin(self):
        """assert case for bin inside the image, not on the edge"""
        central_bin = (3, 2)
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(2, 1), (2, 2), (2, 3), (3, 1), (3, 3), (4, 1), (4, 2), (4, 3)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)

    def test_case_last_column_large_array(self):
        """assert case for bin in last column with a large 2D array"""
        central_bin = (14, 25)
        self.full_bin_height = 26
        self.full_bin_width = 25
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(13, 24), (14, 24), (15, 24), (13, 25), (15, 25)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)

class TestConvertBinsToKeys(TestCase):

    def setUp(self):
        self.full_bin_width = 5
        self.full_bin_height = 10

    def test_first_bin(self):
        """assert case for 1 bin (0,0)"""
        list_of_bins = [(0, 0)]
        list_of_keys_returned = convert_bins_to_keys(list_of_bins=list_of_bins,
                                                     full_bin_height=self.full_bin_height)
        list_of_keys_expected = ["0"]

        self.assertEqual(list_of_keys_expected, list_of_keys_returned)

    def test_last_bin_of_first_column(self):
        """assert case for last bin of first column (9,0)"""
        list_of_bins = [(9, 0)]
        list_of_keys_returned = convert_bins_to_keys(list_of_bins=list_of_bins,
                                                     full_bin_height=self.full_bin_height)
        list_of_keys_expected = ["9"]

        self.assertEqual(list_of_keys_expected, list_of_keys_returned)

    def test_first_bin_of_second_column(self):
        """assert case for last bin of first column (0,1)"""
        list_of_bins = [(0, 1)]
        list_of_keys_returned = convert_bins_to_keys(list_of_bins=list_of_bins,
                                                     full_bin_height=self.full_bin_height)
        list_of_keys_expected = ["10"]

        self.assertEqual(list_of_keys_expected, list_of_keys_returned)

    def test_first_bin_of_second_column(self):
        """assert case for last bin (9, 4)"""
        list_of_bins = [(9, 4)]
        list_of_keys_returned = convert_bins_to_keys(list_of_bins=list_of_bins,
                                                     full_bin_height=self.full_bin_height)
        list_of_keys_expected = ["49"]

        self.assertEqual(list_of_keys_expected, list_of_keys_returned)

    def test_list_of_bins_case1(self):
        """assert case for list of bins"""
        list_of_bins = [(0, 0), [9, 0], [0, 1], [9, 4]]
        list_of_keys_returned = convert_bins_to_keys(list_of_bins=list_of_bins,
                                                     full_bin_height=self.full_bin_height)
        list_of_keys_expected = ["0", "9", "10", "49"]

        self.assertEqual(list_of_keys_expected, list_of_keys_returned)
