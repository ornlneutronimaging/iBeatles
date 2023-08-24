from unittest import TestCase
import numpy as np

from ibeatles.utilities.bins import create_list_of_bins_from_selection
from ibeatles.utilities.bins import create_list_of_surrounding_bins


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

    def test_case_bottom_left_corner(self):
        """assert case for bottom left corner"""
        central_bin = (4, 0)
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(3, 0), (3, 1), (4, 1)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)

    def test_case_top_right_corner(self):
        """assert case for top right corner"""
        central_bin = (0, 9)
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(0, 8), (1, 8), (1, 9)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)

    def test_case_bottom_right_corner(self):
        """assert case for bottom right corner"""
        central_bin = (4, 9)
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(3, 8), (3, 9), (4, 8)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)

    def test_case_central_bin(self):
        """assert case for bin inside the image, not on the edge"""
        central_bin = (3, 4)
        surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                           full_bin_width=self.full_bin_width,
                                                           full_bin_height=self.full_bin_height)
        expected_surrounding_bins = [(2, 3), (2, 4), (2, 5), (3, 3), (3, 5), (4, 3), (4, 4), (4, 5)]
        expected_surrounding_bins.sort()

        self.assertEqual(expected_surrounding_bins, surrounding_bins)
