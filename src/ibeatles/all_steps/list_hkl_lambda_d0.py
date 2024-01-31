from qtpy import QtCore
from qtpy.QtWidgets import QDialog
import numpy as np
from collections import OrderedDict

from src.ibeatles import Material
from src.ibeatles.utilities.gui_handler import GuiHandler
from src.ibeatles import load_ui
from src.ibeatles.utilities.table_handler import TableHandler


class ListHKLLambdaD0Handler:

    def __init__(self, parent=None):
        if parent.list_hkl_lambda_d0_ui is None:
            list_dialog = ListHKLLambdaD0(parent=parent)
            list_dialog.show()
            parent.list_hkl_lambda_d0_ui = list_dialog
        else:
            parent.list_hkl_lambda_d0_ui.setFocus()
            parent.list_hkl_lambda_d0_ui.activateWindow()


class ListHKLLambdaD0(QDialog):
    new_element = {}

    def __init__(self, parent=None):
        self.parent = parent

        QDialog.__init__(self, parent=parent)
        self.ui = load_ui('ui_list_hkl.ui', baseinstance=self)
        self.setWindowTitle("List of h, k, l, lambda and d0")

        self.init_table()
        self.populate_table()

    def init_table(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        column_sizes = [70, 70, 70, 70, 70]
        o_table.set_column_sizes(column_sizes=column_sizes)

        column_names = ["h", "k", "l", u"\u03bb", u"d\u2090"]
        o_table.set_column_names(column_names=column_names)

    def populate_table(self):
        """
        Take the self.parent.selected_element_bragg_edges_array, self.parent.selected_element_hkl_array
        and the current selected element to populate the corresponding infos
        """
        o_gui = GuiHandler(parent=self.parent)
        element_name = str(o_gui.get_text_selected(ui=self.parent.ui.list_of_elements))
        self.ui.selected_element_value.setText(element_name)

        if element_name in self.parent.user_defined_bragg_edge_list.keys():
            user_defined_bragg_edge_list = self.parent.user_defined_bragg_edge_list[element_name]
            list_hkl_d0 = user_defined_bragg_edge_list[Material.hkl_d0]
            o_table = TableHandler(table_ui=self.ui.tableWidget)
            _row = 0
            for _key in list_hkl_d0.keys():
                _entry = list_hkl_d0[_key]
                if _entry['h'] is None:
                    continue
                o_table.insert_empty_row(row=_row)

                _h = _entry['h']
                _k = _entry['k']
                _l = _entry['l']
                _d0 = _entry['d0']
                _lambda = 2*float(_d0)

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
                                    value=_lambda,
                                    format_str="{:.3f}")

                o_table.insert_item(row=_row,
                                    column=4,
                                    value=_d0,
                                    format_str="{:.3f}")

                _row += 1

        else:  # element found in the default list
            selected_element_bragg_edges_array = self.parent.selected_element_bragg_edges_array
            selected_element_hkl_array = self.parent.selected_element_hkl_array

            nbr_row = len(selected_element_hkl_array)
            o_table = TableHandler(table_ui=self.ui.tableWidget)
            for _row in np.arange(nbr_row):
                o_table.insert_empty_row(row=_row)
                [_h, _k, _l] = selected_element_hkl_array[_row]
                _lambda = selected_element_bragg_edges_array[_row]

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
                                    value=_lambda,
                                    format_str="{:.3f}")

                o_table.insert_item(row=_row,
                                    column=4,
                                    value=_lambda/2.,
                                    format_str="{:.3f}")

    def closeEvent(self, ev):
        self.parent.list_hkl_lambda_d0_ui = None

    def close_clicked(self):
        self.parent.list_hkl_lambda_d0_ui = None
        self.close()

    def refresh_populate_table(self):
        o_table = TableHandler(table_ui=self.ui.tableWidget)
        o_table.remove_all_rows()
        self.populate_table()
