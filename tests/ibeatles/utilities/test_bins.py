from unittest import TestCase
import numpy as np

from ibeatles.utilities.bins import create_list_of_bins_from_selection


class TestLoadData(TestCase):

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
