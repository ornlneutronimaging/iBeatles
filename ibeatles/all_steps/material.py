import numpy as np

from neutronbraggedge.braggedge import BraggEdge

from ibeatles.utilities.check import is_float, is_int
from ibeatles.utilities.bragg_edge_element_handler import BraggEdgeElementCalculator
from ibeatles.utilities.table_handler import TableHandler


class Material:

    def __init__(self, parent=None):
        self.parent = parent

    def tab_changed(self):
        self.check_status_of_all_widgets()

    def check_status_of_all_widgets(self):
        """
        check the status of the widgets
        """
        top_tab_index = self.parent.ui.material_top_tabWidget.currentIndex()
        if top_tab_index == 0:
            return

        if top_tab_index == 1:
            element_name = self.parent.ui.user_defined_element_name.text()
            if element_name.strip() == "":
                self.parent.ui.material_custom_tabWidget.setEnabled(False)
                self.parent.ui.user_defined_name_error.setVisible(True)

            else:
                self.parent.ui.material_custom_tabWidget.setEnabled(True)
                self.parent.ui.user_defined_name_error.setVisible(False)

                custom_tab_index = self.parent.ui.material_custom_tabWidget.currentIndex()
                if custom_tab_index == 0:  # method 1

                    lattice = self.parent.ui.method1_lattice_value_2.text()
                    if not is_float(lattice):
                        self.parent.ui.method1_lattice_error.setVisible(True)
                    else:
                        self.parent.ui.method1_lattice_error.setVisible(False)

                    # check validity of table
                    is_valid = self.is_table_valid(table_ui=self.parent.ui.method1_tableWidget)
                    if is_valid:
                        self.parent.ui.user_defined_method1_table_error.setVisible(False)
                    else:
                        self.parent.ui.user_defined_method1_table_error.setVisible(True)

                else:  # method 2

                    # check validity of table
                    is_valid = self.is_table_valid(table_ui=self.parent.ui.method2_tableWidget)
                    if is_valid:
                        self.parent.ui.user_defined_method2_table_error.setVisible(False)
                    else:
                        self.parent.ui.user_defined_method2_table_error.setVisible(True)

    def is_table_valid(self, table_ui=None):

        o_table = TableHandler(table_ui=table_ui)
        nbr_row = o_table.row_count()
        at_least_one_row_valid = False
        for _row in np.arange(nbr_row):

            h = o_table.get_item_str_from_cell(row=_row, column=0)
            k = o_table.get_item_str_from_cell(row=_row, column=1)
            l = o_table.get_item_str_from_cell(row=_row, column=2)
            d0_or_lambda = o_table.get_item_str_from_cell(row=_row, column=3)

            if ((h is None) or h == "") and \
                    ((k is None) or k == "") and \
                    ((l is None) or l == "") and \
                    ((d0_or_lambda is None) or d0_or_lambda == ""):
                continue

            elif (h is None):
                return False

            elif k is None:
                return False

            elif l is None:
                return False

            elif d0_or_lambda is None:
                return False

            if (h.strip() == "") and (k.strip() == "") and (l.strip() == "") and (d0_or_lambda.strip() == ""):
                continue

            if not is_int(h):
                return False

            if not is_int(k):
                return False

            if not is_int(l):
                return False

            if not is_float(d0_or_lambda):
                return False

            at_least_one_row_valid = True

        return at_least_one_row_valid


class MaterialPreDefined(Material):

    def update_pre_defined_widgets(self):
        element_selected = self.parent.ui.pre_defined_list_of_elements.currentText()
        _handler = BraggEdge(material=element_selected)
        _crystal_structure = _handler.metadata['crystal_structure'][element_selected]
        _lattice = str(_handler.metadata['lattice'][element_selected])

        o_calculator = BraggEdgeElementCalculator(element_name=element_selected,
                                                  lattice_value=_lattice,
                                                  crystal_structure=_crystal_structure)
        o_calculator.run()

        selected_element_bragg_edges_array = o_calculator.lambda_array
        selected_element_hkl_array = o_calculator.hkl_array

        self.parent.ui.pre_defined_lattice_value.setText(_lattice)
        self.parent.ui.pre_defined_crystal_value.setText(_crystal_structure)

        o_table = TableHandler(table_ui=self.parent.ui.pre_defined_tableWidget)
        o_table.remove_all_rows()

        _row = 0
        for _hkl, _lambda in zip(selected_element_hkl_array, selected_element_bragg_edges_array):

            o_table.insert_empty_row(row=_row)
            _h = _hkl[0]
            _k = _hkl[1]
            _l = _hkl[2]

            o_table.insert_item(row=_row,
                                column=0,
                                editable=False,
                                value=_h)

            o_table.insert_item(row=_row,
                                column=1,
                                editable=False,
                                value=_k)

            o_table.insert_item(row=_row,
                                column=2,
                                editable=False,
                                value=_l)

            o_table.insert_item(row=_row,
                                column=3,
                                editable=False,
                                value=_lambda,
                                format_str="{:.3f}")

            _row += 1


class MaterialUserDefined(Material):

    def user_defined_element_name_changed(self):
        element_name = self.parent.ui.user_defined_element_name.text()
        if element_name.strip() == "":
            display_error_message = True
        else:
            display_error_message = False
        self.parent.ui.user_defined_name_error.setVisible(display_error_message)


class MaterialUserDefinedMethod1(Material):

    def fill_fields_with_selected_element_clicked(self):
        element_selected = self.parent.ui.user_defined_list_of_elements.currentText()
        if element_selected == 'None':
            return

        _handler = BraggEdge(material=element_selected)
        _crystal_structure = _handler.metadata['crystal_structure'][element_selected]
        _lattice = str(_handler.metadata['lattice'][element_selected])

        o_calculator = BraggEdgeElementCalculator(element_name=element_selected,
                                                  lattice_value=_lattice,
                                                  crystal_structure=_crystal_structure)
        o_calculator.run()

        selected_element_bragg_edges_array = o_calculator.lambda_array
        selected_element_hkl_array = o_calculator.hkl_array

        self.parent.ui.method1_lattice_value_2.setText(f"{float(_lattice):.3f}")
        _row_to_select = self.parent.ui.method1_crystal_value_2.findText(_crystal_structure)
        self.parent.ui.method1_crystal_value_2.setCurrentIndex(_row_to_select)

        self.fill_table_method1(selected_element_hkl_array=selected_element_hkl_array,
                                selected_element_bragg_edges_array=selected_element_bragg_edges_array)

    def user_defined_element_name_changed(self):
        element_name = self.parent.ui.user_defined_element_name.text()
        lattice_value = self.parent.ui.method1_lattice_value_2.text()
        if not is_float(lattice_value):
            o_table = TableHandler(table_ui=self.parent.ui.method1_tableWidget)
            o_table.remove_all_rows()
            return

        crystal_structure = self.parent.ui.method1_crystal_value_2.currentText()

        o_calculator = BraggEdgeElementCalculator(element_name=element_name,
                                                  lattice_value=lattice_value,
                                                  crystal_structure=crystal_structure)
        o_calculator.run()

        selected_element_bragg_edges_array = o_calculator.lambda_array
        selected_element_hkl_array = o_calculator.hkl_array

        self.fill_table_method1(selected_element_hkl_array=selected_element_hkl_array,
                                selected_element_bragg_edges_array=selected_element_bragg_edges_array)

    def fill_table_method1(self, selected_element_hkl_array=None,
                           selected_element_bragg_edges_array=None):

        o_table = TableHandler(table_ui=self.parent.ui.method1_tableWidget)
        o_table.remove_all_rows()

        _row = 0
        for _hkl, _lambda in zip(selected_element_hkl_array, selected_element_bragg_edges_array):

            o_table.insert_empty_row(row=_row)
            _h = _hkl[0]
            _k = _hkl[1]
            _l = _hkl[2]

            o_table.insert_item(row=_row,
                                column=0,
                                value=_h)

            o_table.insert_item(row=_row,
                                column=1,
                                value=_k)

            o_table.insert_item(row=_row,
                                column=2,
                                value=_l)

            o_table.insert_item(row=_row,
                                column=3,
                                value=_lambda/2.,
                                format_str="{:.3f}")

            _row += 1

    def lattice_crystal_changed(self):
        """recalculate the hkl and lambda 0 of the table"""
        self.user_defined_element_name_changed()


class MaterialUserDefinedMethod2(Material):

    def clear_user_defined_method2_table(self):
        o_table = TableHandler(table_ui=self.parent.ui.method2_tableWidget)
        o_table.remove_all_rows()
        for _row in np.arange(10):
            o_table.insert_empty_row(row=_row)
