from neutronbraggedge.braggedge import BraggEdge

from ibeatles.utilities.bragg_edge_element_handler import BraggEdgeElementCalculator
from ibeatles.utilities.table_handler import TableHandler


class Material:

    def __init__(self, parent=None):
        self.parent = parent

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
