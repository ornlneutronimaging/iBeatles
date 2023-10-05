from unittest import TestCase
import pytest
import numpy as np

from ibeatles.fitting.kropff.event_handler import EventHandler
from ibeatles.fitting.kropff import SessionSubKeys as KropffSessionSubKeys


class Parent:

    def __init__(self):
        pass


class GrandParent:

    kropff_table_dictionary = {"0": {KropffSessionSubKeys.lambda_hkl: {'val': 0,
                                                                      'err': 0},
                                     },
                               }
    def __init__(self):
        pass


class TestPerformFitting(TestCase):

    def test_did_we_perform_fitting_with_no_fitting(self):
        """assert that it returns false if no fitting has been performed"""
        parent = Parent()
        grand_parent = GrandParent()
        grand_parent.kropff_table_dictionary["0"][KropffSessionSubKeys.lambda_hkl]["val"] = np.NaN
        event_handler = EventHandler(parent=parent,
                                     grand_parent=grand_parent)
        self.assertFalse(event_handler.did_we_perform_the_fitting())

    def test_did_we_perform_fitting_with_fitting(self):
        """assert that it returns false if no fitting has been performed"""
        parent = Parent()
        grand_parent = GrandParent()
        grand_parent.kropff_table_dictionary["0"][KropffSessionSubKeys.lambda_hkl]["val"] = 3.6
        event_handler = EventHandler(parent=parent,
                                     grand_parent=grand_parent)
        self.assertTrue(event_handler.did_we_perform_the_fitting())
