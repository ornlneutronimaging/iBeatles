from unittest import TestCase

from ibeatles.fitting.kropff.get import Get


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

    def __init__(self, fix_value=None, fix_radioButton=True,
                 from_lineEdit=None, to_lineEdit=None, step_lineEdit=None):

        self.lambda_hkl_fix_lineEdit = LineEdit(fix_value)
        self.lambda_hkl_fix_radioButton = CheckBox(fix_radioButton)
        self.lambda_hkl_from_lineEdit = LineEdit(from_lineEdit)
        self.lambda_hkl_to_lineEdit = LineEdit(to_lineEdit)
        self.lambda_hkl_step_lineEdit = LineEdit(step_lineEdit)


class MockParent:
    ui = MockWidget()

    def __init__(self, fix_value=None, fix_radioButton=True,
                 from_lineEdit=None, to_lineEdit=None, step_lineEdit=None):

        self.ui = MockWidget(fix_value=fix_value,
                             fix_radioButton=fix_radioButton,
                             from_lineEdit=from_lineEdit,
                             to_lineEdit=to_lineEdit)


class TestGet(TestCase):

    def test_list_lambda_hkl_initial_guess(self):
        """assert correct list of lambda_hkl is returned"""
        parent = MockParent(fix_value=5e-8,
                            fix_radioButton=True)
        o_get = Get(parent=parent)
        list_lambda_hkl_returned = o_get.list_lambda_hkl_initial_guess()
        list_lambda_hkl_expected = [5.e-8]

        self.assertEqual(list_lambda_hkl_expected, list_lambda_hkl_returned)
