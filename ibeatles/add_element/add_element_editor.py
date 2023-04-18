from qtpy import QtCore
from qtpy.QtWidgets import QDialog
import numpy as np
from collections import OrderedDict

from ibeatles import Material
from ibeatles.utilities.gui_handler import GuiHandler
from ibeatles import load_ui
from ibeatles.utilities.check import is_float, is_int
from ibeatles.utilities.table_handler import TableHandler
from ibeatles.utilities.bragg_edge_element_handler import BraggEdgeElementCalculator


class AddElement(object):

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):

        _interface = AddElementInterface(parent=self.parent)
        _interface.show()
        self.parent.add_element_editor_ui = _interface


class AddElementInterface(QDialog):
    new_element = {}

    def __init__(self, parent=None):
        self.parent = parent

        QDialog.__init__(self, parent=parent)
        self.ui = load_ui('ui_addElement.ui', baseinstance=self)
        self.setWindowTitle("Add Element Editor")
        self.ui.element_name_error.setVisible(False)
        self.check_add_widget_state()

    def element_name_changed(self, current_value):
        self.check_add_widget_state()

    def lattice_changed(self, current_value):
        self.check_add_widget_state()

    def check_add_widget_state(self):

        self.ui.error_message.setText("")
        current_element_name = str(self.ui.element_name.text())
        if current_element_name.strip() == "":
            self.ui.add.setEnabled(False)
            self.ui.error_message.setText("Provide an element name!")
            return

        if self.ui.method1_radioButton.isChecked():  # method 1

            lattice_value = self.ui.lattice.text()
            if lattice_value.strip() == "":
                self.ui.add.setEnabled(False)
                self.ui.error_message.setText("Lattice value is missing!")
                return

            if not is_float(lattice_value):
                self.ui.add.setEnabled(False)
                self.ui.error_message.setText("Lattice must be a number")
                return

            list_element_root = self.parent.ui.list_of_elements.findText(current_element_name,
                                                                         QtCore.Qt.MatchCaseSensitive)
            if not (list_element_root == -1):  # element already there
                self.ui.element_name_error.setVisible(True)
                self.ui.add.setEnabled(False)
                self.ui.error_message.setText("Element name already used!")
                return

            else:
                self.ui.element_name_error.setVisible(False)
                self.ui.add.setEnabled(True)
                return

        else:  # method 2

            # at least one entry in the table
            o_table = TableHandler(table_ui=self.ui.tableWidget)
            nbr_row = o_table.row_count()
            at_least_one_row_valid = False
            for _row in np.arange(nbr_row):

                h = o_table.get_item_str_from_cell(row=_row, column=0)
                k = o_table.get_item_str_from_cell(row=_row, column=1)
                l = o_table.get_item_str_from_cell(row=_row, column=2)
                d0 = o_table.get_item_str_from_cell(row=_row, column=3)

                if ((h is None) or h == "") and \
                        ((k is None) or k == "") and \
                        ((l is None) or l == "") and \
                        ((d0 is None) or d0 == ""):
                    continue

                elif (h is None):
                    self.ui.add.setEnabled(False)
                    self.ui.error_message.setText("missing h value!")
                    return

                elif k is None:
                    self.ui.add.setEnabled(False)
                    self.ui.error_message.setText("missing k value!")
                    return

                elif l is None:
                    self.ui.add.setEnabled(False)
                    self.ui.error_message.setText("missing l value!")
                    return

                elif d0 is None:
                    self.ui.add.setEnabled(False)
                    self.ui.error_message.setText("missing d0 value!")
                    return

                if (h.strip() == "") and (k.strip() == "") and (l.strip() == "") and (d0.strip() == ""):
                    continue

                if not is_int(h):
                    self.ui.add.setEnabled(False)
                    self.ui.error_message.setText("h must be an integer!")
                    return

                if not is_int(k):
                    self.ui.add.setEnabled(False)
                    self.ui.error_message.setText("k must be an integer!")
                    return

                if not is_int(l):
                    self.ui.add.setEnabled(False)
                    self.ui.error_message.setText("l must be an integer!")
                    return

                if not is_float(d0):
                    self.ui.add.setEnabled(False)
                    self.ui.error_message.setText("d0 must be an integer!")
                    return

                at_least_one_row_valid = True

            self.ui.add.setEnabled(at_least_one_row_valid)

            if not at_least_one_row_valid:
                self.ui.error_message.setText("Define at least 1 row of entries!")

    def method2_table_changed(self):
        self.check_add_widget_state()

    def retrieve_metadata(self):
        o_gui = GuiHandler(parent=self)
        element_name = o_gui.get_text(ui=self.ui.element_name)

        if self.ui.method1_radioButton.isChecked():  # method 1
            user_defined = False
            method_used = Material.via_lattice_and_crystal_structure
            lattice = o_gui.get_text(ui=self.ui.lattice)
            crystal_structure = o_gui.get_text_selected(ui=self.ui.crystal_structure)

            # calculate the hkl and d0 here
            o_calculator = BraggEdgeElementCalculator(element_name=element_name,
                                                      lattice_value=lattice,
                                                      crystal_structure=crystal_structure)
            o_calculator.run()
            selected_element_bragg_edges_array = o_calculator.lambda_array
            selected_element_hkl_array = o_calculator.hkl_array

            hkl_d0_dict = OrderedDict()
            for _row_index in np.arange(len(selected_element_hkl_array)):
                hkl_list = selected_element_hkl_array[_row_index]
                h = hkl_list[0]
                k = hkl_list[1]
                l = hkl_list[2]

                _lambda_value = selected_element_bragg_edges_array[_row_index]
                d0 = _lambda_value / 2.

                hkl_d0_dict[_row_index] = {'h': h,
                                           'k': k,
                                           'l': l,
                                           'd0': d0}

        else:
            lattice = None
            method_used = Material.via_d0
            user_defined = True
            crystal_structure = None

            o_table = TableHandler(table_ui=self.ui.tableWidget)
            nbr_row = o_table.row_count()
            hkl_d0_dict = OrderedDict()
            _row_index = 0
            for _row in np.arange(nbr_row):
                h = o_table.get_item_str_from_cell(row=_row, column=0)
                if h == "":
                    continue

                k = o_table.get_item_str_from_cell(row=_row, column=1)
                l = o_table.get_item_str_from_cell(row=_row, column=2)
                d0 = o_table.get_item_str_from_cell(row=_row, column=3)
                hkl_d0_dict[_row_index] = {'h': h,
                                           'k': k,
                                           'l': l,
                                           'd0': d0}
                _row_index += 1

        self.new_element = {Material.element_name: element_name,
                            Material.lattice: lattice,
                            Material.crystal_structure: crystal_structure,
                            Material.hkl_d0: hkl_d0_dict,
                            Material.user_defined: user_defined,
                            Material.method_used: method_used}

    def add_element_to_list_of_elements_widgets(self):
        _element = self.new_element
        self.parent.ui.list_of_elements.blockSignals(True)
        self.parent.ui.list_of_elements_2.blockSignals(True)
        self.parent.ui.list_of_elements.addItem(_element[Material.element_name])
        self.parent.ui.list_of_elements_2.addItem(_element[Material.element_name])
        nbr_element = self.parent.ui.list_of_elements.count()
        self.parent.ui.list_of_elements.setCurrentIndex(nbr_element - 1)
        self.parent.ui.list_of_elements_2.setCurrentIndex(nbr_element - 1)
        self.parent.ui.lattice_parameter.setText(_element[Material.lattice])
        self.parent.ui.lattice_parameter_2.setText(_element[Material.lattice])
        self.parent.ui.list_of_elements.blockSignals(False)
        self.parent.ui.list_of_elements_2.blockSignals(False)

    def save_new_element_to_local_list(self):
        _new_element = self.new_element

        _new_entry = {Material.lattice: _new_element[Material.lattice],
                      Material.crystal_structure: _new_element[Material.crystal_structure],
                      Material.hkl_d0: _new_element[Material.hkl_d0],
                      Material.method_used: _new_element[Material.method_used]}

        self.parent.user_defined_bragg_edge_list[_new_element[Material.element_name]] = _new_entry
        self.parent.local_bragg_edge_list[_new_element[Material.element_name]] = _new_entry

    def method_changed(self):
        is_method1_activated = self.ui.method1_radioButton.isChecked()
        self.ui.method1_groupBox.setEnabled(is_method1_activated)
        self.ui.method2_groupBox.setEnabled(not is_method1_activated)
        self.check_add_widget_state()

    def add_clicked(self):
        self.retrieve_metadata()
        self.save_new_element_to_local_list()
        self.add_element_to_list_of_elements_widgets()
        self.parent.update_hkl_lambda_d0()

        self.close()
