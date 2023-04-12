from qtpy import QtCore
from qtpy.QtWidgets import QDialog
import numpy as np

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

    def element_name_changed(self, current_value):
        self.check_add_widget_state()

    def lattice_changed(self, current_value):
        self.check_add_widget_state()

    def check_add_widget_state(self):

        print("in check_add_widget state")
        current_element_name = str(self.ui.element_name.text())
        if current_element_name.strip() == "":
            self.ui.add.setEnabled(False)

        if self.ui.method1_radioButton.isChecked():  # method 1

            lattice_value = self.ui.lattice.text()
            if lattice_value.strip() == "":
                self.ui.add.setEnabled(False)
                return

            if not is_float(lattice_value):
                self.ui.add.setEnabled(False)
                return

            list_element_root = self.parent.ui.list_of_elements.findText(current_element_name,
                                                                         QtCore.Qt.MatchCaseSensitive)
            if not (list_element_root == -1):  # element already there
                self.ui.element_name_error.setVisible(True)
                self.ui.add.setEnabled(False)
                return

            else:
                self.ui.element_name_error.setVisible(False)
                self.ui.add.setEnabled(True)
                return

        else:  # method 2

            # at least one entry in the table
            o_table = TableHandler(table_ui=self.ui.tableWidget)
            nbr_row = o_table.row_count()
            print(f"{nbr_row =}")
            at_least_one_row_valid = False
            for _row in np.arange(nbr_row):
                h = o_table.get_item_from_cell(row=_row, column=0)
                if h is None:
                    self.ui.add.setEnabled(False)
                    return

                k = o_table.get_item_from_cell(row=_row, column=1)
                if k is None:
                    self.ui.add.setEnabled(False)
                    return

                l = o_table.get_item_from_cell(row=_row, column=2)
                if l is None:
                    self.ui.add.setEnabled(False)
                    return
                d0 = o_table.get_item_from_cell(row=_row, column=3)
                if d0 is None:
                    self.ui.add.setEnabled(False)
                    return

                if (h.strip() == "") and (k.strip() == "") and (l.strip() == "") and (d0.strip() == ""):
                    print(f"here in row {_row}")
                    continue

                if not is_int(h):
                    self.ui.add.setEnabled(False)
                    print(f"{h =}")
                    return

                if not is_int(k):
                    self.ui.add.setEnabled(False)
                    print(f"{k =}")
                    return

                if not is_int(l):
                    self.ui.add.setEnabled(False)
                    print(f"{l =}")
                    return

                if not is_float(d0):
                    self.ui.add.setEnabled(False)
                    print(f"{d0 =}")
                    return

                at_least_one_row_valid = True

            print("I should be here")
            self.ui.add.setEnabled(at_least_one_row_valid)

    def method2_table_changed(self):
        self.check_add_widget_state()

    def retrieve_metadata(self):
        o_gui = GuiHandler(parent=self)

        element_name = o_gui.get_text(ui=self.ui.element_name)
        lattice = o_gui.get_text(ui=self.ui.lattice)
        crystal_structure = o_gui.get_text_selected(ui=self.ui.crystal_structure)

        self.new_element = {'element_name': element_name,
                            'lattice': lattice,
                            'crystal_structure': crystal_structure}

    def add_element_to_list_of_elements_widgets(self):
        _element = self.new_element
        self.parent.ui.list_of_elements.addItem(_element['element_name'])
        nbr_element = self.parent.ui.list_of_elements.count()
        self.parent.ui.list_of_elements.setCurrentIndex(nbr_element - 1)
        self.parent.ui.list_of_elements_2.addItem(_element['element_name'])
        self.parent.ui.list_of_elements_2.setCurrentIndex(nbr_element - 1)
        self.parent.ui.lattice_parameter.setText(_element['lattice'])
        self.parent.ui.lattice_parameter_2.setText(_element['lattice'])

    def save_new_element_to_local_list(self):
        _new_element = self.new_element

        _new_entry = {'lattice': _new_element['lattice'],
                      'crystal_structure': _new_element['crystal_structure']}

        self.parent.local_bragg_edge_list[_new_element['element_name']] = _new_entry

    def method_changed(self):
        is_method1_activated = self.ui.method1_radioButton.isChecked()
        self.ui.method1_groupBox.setEnabled(is_method1_activated)
        self.ui.method2_groupBox.setEnabled(not is_method1_activated)
        self.check_add_widget_state()

    def add_clicked(self):
        self.retrieve_metadata()
        self.save_new_element_to_local_list()
        self.add_element_to_list_of_elements_widgets()
        self.close()
