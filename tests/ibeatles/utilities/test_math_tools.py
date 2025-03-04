from unittest import TestCase
import numpy as np

from ibeatles.utilities.math_tools import get_index_of_closest_match


class TestCreateListOfBinsFromSelection(TestCase):
    def test_case_file_index(self):
        """assert case with right linear units"""
        array_to_look_for = np.arange(10)
        value = 4
        left_margin = True

        index_returned = get_index_of_closest_match(
            array_to_look_for=array_to_look_for, value=value, left_margin=left_margin
        )
        index_expected = 4
        self.assertEqual(index_returned, index_expected)

        value = 0
        left_margin = True

        index_returned = get_index_of_closest_match(
            array_to_look_for=array_to_look_for, value=value, left_margin=left_margin
        )
        index_expected = 0
        self.assertEqual(index_returned, index_expected)

        value = -1
        left_margin = True

        index_returned = get_index_of_closest_match(
            array_to_look_for=array_to_look_for, value=value, left_margin=left_margin
        )
        index_expected = 0
        self.assertEqual(index_returned, index_expected)

        value = 10
        left_margin = True

        index_returned = get_index_of_closest_match(
            array_to_look_for=array_to_look_for, value=value, left_margin=left_margin
        )
        index_expected = 9
        self.assertEqual(index_returned, index_expected)

        value = 15
        left_margin = True

        index_returned = get_index_of_closest_match(
            array_to_look_for=array_to_look_for, value=value, left_margin=left_margin
        )
        index_expected = 9
        self.assertEqual(index_returned, index_expected)

    def test_case_tof_index(self):
        """assert case with right linear units"""
        array_to_look_for = np.arange(10) * 0.5
        value = 3.5
        left_margin = True

        index_returned = get_index_of_closest_match(
            array_to_look_for=array_to_look_for, value=value, left_margin=left_margin
        )
        index_expected = 7
        self.assertEqual(index_returned, index_expected)

        array_to_look_for = np.arange(10) * 0.25
        value = 1.25
        left_margin = True

        index_returned = get_index_of_closest_match(
            array_to_look_for=array_to_look_for, value=value, left_margin=left_margin
        )
        index_expected = 5
        self.assertEqual(index_returned, index_expected)
