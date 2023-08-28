from unittest import TestCase
import numpy as np

from ibeatles.utilities.array_utilities import calculate_median


class TestCalculateMedian(TestCase):

    def test_empty_array(self):
        """assert empty array return None"""
        array = None
        median_returned = calculate_median(array_of_value=array)
        median_expected = None

        self.assertEqual(median_returned, median_expected)

    def test_simple_array(self):
        """assert simple array [1, 2, 3] return 2"""
        array = [1, 2, 3]
        median_returned = calculate_median(array_of_value=array)
        median_expected = 2

        self.assertEqual(median_expected, median_returned)

    def test_array_with_nan(self):
        """assert simple array [1, 2, 3, NaN] return 2"""
        array = [1, 2, 3, np.NaN]
        median_returned = calculate_median(array_of_value=array)
        median_expected = 2

        self.assertEqual(median_expected, median_returned)

    def test_array_with_only_nan(self):
        """assert only nan return nan"""
        array = [np.NaN, np.NaN, np.NaN]
        median_returned = calculate_median(array_of_value=array)

        self.assertTrue(np.isnan(median_returned))

    def test_array_with_inf(self):
        """assert with inf"""
        array = [np.inf, 1, 2, 3]
        median_returned = calculate_median(array_of_value=array)
        median_expected = 2

        self.assertEqual(median_returned, median_expected)

    def test_array_with_negative_inf(self):
        """assert with neg inf"""
        array = [-np.inf, 1, 2, 3]
        median_returned = calculate_median(array_of_value=array)
        median_expected = 2

        self.assertEqual(median_returned, median_expected)

    def test_array_with_inf_and_nan(self):
        """assert with inf and nan"""
        array = [-np.inf, 1, 2, np.NaN]
        median_returned = calculate_median(array_of_value=array)
        median_expected = 1.5

        self.assertEqual(median_returned, median_expected)
