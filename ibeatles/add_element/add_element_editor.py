from qtpy import QtCore
from qtpy.QtWidgets import QDialog
import numpy as np
from collections import OrderedDict

from ibeatles import Material
from ibeatles.utilities.gui_handler import GuiHandler
from ibeatles import load_ui
from ibeatles.utilities.check import is_float, is_int
from ibeatles.utilities.table_handler import TableHandler


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
            lattice = o_gui.get_text(ui=self.ui.lattice)
            crystal_structure = o_gui.get_text_selected(ui=self.ui.crystal_structure)

            # calculate the hkl and d0 here
            pass



            # FIXME
            hkl_d0_dict = None




        else:
            lattice = None
            crystal_structure = None

            o_table = TableHandler(table_ui=self.ui.tableWidget)
            nbr_row = o_table.row_count()
            hkl_d0_dict = OrderedDict()
            for _row in np.arange(nbr_row):
                h = o_table.get_item_str_from_cell(row=_row, column=0)
                k = o_table.get_item_str_from_cell(row=_row, column=1)
                l = o_table.get_item_str_from_cell(row=_row, column=2)
                d0 = o_table.get_item_str_from_cell(row=_row, column=3)
                hkl_d0_dict[_row] = {'h': h,
                                     'k': k,
                                     'l': l,
                                     'd0': d0}

        self.new_element = {Material.element_name: element_name,
                            Material.lattice: lattice,
                            Material.crystal_structure: crystal_structure,
                            Material.hkl_d0: hkl_d0_dict}

    def add_element_to_list_of_elements_widgets(self):
        _element = self.new_element
        self.parent.ui.list_of_elements.addItem(_element[Material.element_name])
        nbr_element = self.parent.ui.list_of_elements.count()
        self.parent.ui.list_of_elements.setCurrentIndex(nbr_element - 1)
        self.parent.ui.list_of_elements_2.addItem(_element[Material.element_name])
        self.parent.ui.list_of_elements_2.setCurrentIndex(nbr_element - 1)
        self.parent.ui.lattice_parameter.setText(_element[Material.lattice])
        self.parent.ui.lattice_parameter_2.setText(_element[Material.lattice])

    def save_new_element_to_local_list(self):
        _new_element = self.new_element

        _new_entry = {Material.lattice: _new_element[Material.lattice],
                      Material.crystal_structure: _new_element[Material.crystal_structure]}

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
        self.parent.update_hkl_d0_table()

        self.close()
