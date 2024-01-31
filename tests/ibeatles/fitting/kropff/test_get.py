from unittest import TestCase
import pytest

from src.ibeatles.fitting.kropff.get import Get
import ibeatles.utilities.error as fitting_error


class CheckBox:

    def __init__(self, value=True):
        self.value = value

    def isChecked(self):
        return self.value


class LineEdit:

    def __init__(self, text_value=""):
        self.text_value = text_value

    def text(self):
        return self.text_value


class MockWidget:

    lambda_hkl_fix_lineEdit = None
    lambda_hkl_fix_radioButton = None
    lambda_hkl_from_lineEdit = None
    lambda_hkl_to_lineEdit = None
    lambda_hkl_step_lineEdit = None

    sigma_fix_lineEdit = None
    sigma_fix_radioButton = None
    sigma_from_lineEdit = None
    sigma_to_lineEdit = None
    sigma_step_lineEdit = None

    def __init__(self, fix_value=None, fix_radioButton=True,
                 from_lineEdit=None, to_lineEdit=None, step_lineEdit=None):

        self.lambda_hkl_fix_lineEdit = LineEdit(fix_value)
        self.lambda_hkl_fix_radioButton = CheckBox(fix_radioButton)
        self.lambda_hkl_from_lineEdit = LineEdit(from_lineEdit)
        self.lambda_hkl_to_lineEdit = LineEdit(to_lineEdit)
        self.lambda_hkl_step_lineEdit = LineEdit(step_lineEdit)

        self.sigma_fix_lineEdit = LineEdit(fix_value)
        self.sigma_fix_radioButton = CheckBox(fix_radioButton)
        self.sigma_from_lineEdit = LineEdit(from_lineEdit)
        self.sigma_to_lineEdit = LineEdit(to_lineEdit)
        self.sigma_step_lineEdit = LineEdit(step_lineEdit)

        self.tau_fix_lineEdit = LineEdit(fix_value)
        self.tau_fix_radioButton = CheckBox(fix_radioButton)
        self.tau_from_lineEdit = LineEdit(from_lineEdit)
        self.tau_to_lineEdit = LineEdit(to_lineEdit)
        self.tau_step_lineEdit = LineEdit(step_lineEdit)


class MockParent:
    ui = MockWidget()

    def __init__(self, fix_value=None,
                 fix_radioButton=True,
                 from_lineEdit=None,
                 to_lineEdit=None,
                 step_lineEdit=None):

        self.ui = MockWidget(fix_value=fix_value,
                             fix_radioButton=fix_radioButton,
                             from_lineEdit=from_lineEdit,
                             to_lineEdit=to_lineEdit,
                             step_lineEdit=step_lineEdit)


class TestGet(TestCase):

    # fix_value
    def test_list_lambda_hkl_initial_guess_fix_value(self):
        """assert correct list of lambda_hkl is returned for fix value"""
        parent = MockParent(fix_value=5e-8,
                            fix_radioButton=True)
        o_get = Get(parent=parent)
        list_lambda_hkl_returned = o_get.list_lambda_hkl_initial_guess()
        list_lambda_hkl_expected = [5.e-8]
        self.assertEqual(list_lambda_hkl_expected, list_lambda_hkl_returned)

    def test_list_sigma_initial_guess_fix_value(self):
        """assert correct list of sigma is returned for fix value"""
        parent = MockParent(fix_value=1,
                            fix_radioButton=True)
        o_get = Get(parent=parent)
        list_sigma_returned = o_get.list_sigma_initial_guess()
        list_sigma_expected = [1]
        self.assertEqual(list_sigma_expected, list_sigma_returned)

    def test_list_tau_initial_guess_fix_value(self):
        """assert correct list of tau is returned for fix value"""
        parent = MockParent(fix_value=1,
                            fix_radioButton=True)
        o_get = Get(parent=parent)
        list_tau_returned = o_get.list_tau_initial_guess()
        list_tau_expected = [1]
        self.assertEqual(list_tau_expected, list_tau_returned)

    # range value
    def test_list_lambda_hkl_initial_guess_range_value(self):
        """assert correct list of lambda_hkl is returned for range of values"""
        parent = MockParent(from_lineEdit=5e-8,
                            to_lineEdit=1e-7,
                            step_lineEdit=1e-8,
                            fix_radioButton=False)
        o_get = Get(parent=parent)
        list_lambda_hkl_returned = o_get.list_lambda_hkl_initial_guess()
        list_lambda_hkl_expected = [5e-8, 6e-8, 7e-8, 8e-8, 9e-8, 1e-7]
        for _expected, _returned in zip(list_lambda_hkl_expected, list_lambda_hkl_returned):
            self.assertAlmostEqual(_expected, _returned, delta=1e-10)

    def test_list_sigma_initial_guess_range_value(self):
        """assert correct list of sigma is returned for range of values"""
        parent = MockParent(from_lineEdit=0.1,
                            to_lineEdit=1,
                            step_lineEdit=0.1,
                            fix_radioButton=False)
        o_get = Get(parent=parent)
        list_sigma_returned = o_get.list_sigma_initial_guess()
        list_sigma_expected = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        for _expected, _returned in zip(list_sigma_expected, list_sigma_returned):
            self.assertAlmostEqual(_expected, _returned, delta=1e-10)

    def test_list_tau_initial_guess_range_value(self):
        """assert correct list of tau is returned for range of values"""
        parent = MockParent(from_lineEdit=5e-8,
                            to_lineEdit=1e-7,
                            step_lineEdit=1e-8,
                            fix_radioButton=False)
        o_get = Get(parent=parent)
        list_tau_returned = o_get.list_tau_initial_guess()
        list_tau_expected = [5e-8, 6e-8, 7e-8, 8e-8, 9e-8, 1e-7]
        for _expected, _returned in zip(list_tau_expected, list_tau_returned):
            self.assertAlmostEqual(_expected, _returned, delta=1e-10)

    # error with range
    def test_list_lambda_hkl_initial_guess_raise_value_error_with_range(self):
        """assert ValueError lambda_hkl is raised when values are not float with range value"""
        parent = MockParent(from_lineEdit="abc",
                            to_lineEdit=1e-7,
                            step_lineEdit=1e-8,
                            fix_radioButton=False)
        o_get = Get(parent=parent)
        with pytest.raises(fitting_error.BraggPeakFittingError):
            o_get.list_lambda_hkl_initial_guess()

    def test_list_sigma_initial_guess_raise_value_error_with_range(self):
        """assert ValueError sigma is raised when values are not float with range value"""
        parent = MockParent(from_lineEdit="abc",
                            to_lineEdit=1e-7,
                            step_lineEdit=1e-8,
                            fix_radioButton=False)
        o_get = Get(parent=parent)
        with pytest.raises(fitting_error.BraggPeakFittingError):
            o_get.list_sigma_initial_guess()

    def test_list_tau_initial_guess_raise_value_error_with_range(self):
        """assert ValueError tau is raised when values are not float with range value"""
        parent = MockParent(from_lineEdit="abc",
                            to_lineEdit=1e-7,
                            step_lineEdit=1e-8,
                            fix_radioButton=False)
        o_get = Get(parent=parent)
        with pytest.raises(fitting_error.BraggPeakFittingError):
            o_get.list_tau_initial_guess()

    # error with fix
    def test_list_lambda_hkl_initial_guess_raise_value_error_with_fix(self):
        """assert ValueError lambda_hkl is raised when values are not float with fix value"""
        parent = MockParent(fix_value="abc",
                            fix_radioButton=True)
        o_get = Get(parent=parent)
        with pytest.raises(fitting_error.BraggPeakFittingError):
            o_get.list_lambda_hkl_initial_guess()

    def test_list_sigma_initial_guess_raise_value_error_with_fix(self):
        """assert ValueError sigma is raised when values are not float with fix value"""
        parent = MockParent(fix_value="abc",
                            fix_radioButton=True)
        o_get = Get(parent=parent)
        with pytest.raises(fitting_error.BraggPeakFittingError):
            o_get.list_sigma_initial_guess()

    def test_list_tau_initial_guess_raise_value_error_with_fix(self):
        """assert ValueError tau is raised when values are not float with fix value"""
        parent = MockParent(fix_value="abc",
                            fix_radioButton=True)
        o_get = Get(parent=parent)
        with pytest.raises(fitting_error.BraggPeakFittingError):
            o_get.list_tau_initial_guess()