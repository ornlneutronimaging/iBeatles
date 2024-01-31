from neutronbraggedge.braggedge import BraggEdge

from src.ibeatles import Material, ScrollBarParameters, MATERIAL_BRAGG_PEAK_TO_DISPLAY_AT_THE_SAME_TIME
from src.ibeatles.utilities.gui_handler import GuiHandler
from src.ibeatles.session import MaterialMode


class BraggEdgeElementHandler:

    bragg_edges_array = []

    def __init__(self, parent=None):
        self.parent = parent

        table_ui_dict = {MaterialMode.pre_defined: self.parent.ui.pre_defined_tableWidget,
                         MaterialMode.custom_method1: self.parent.ui.method1_tableWidget,
                         MaterialMode.custom_method2: self.parent.ui.method2_tableWidget}

        o_gui = GuiHandler(parent=self.parent)

        material_active_tab = o_gui.get_material_active_tab()
        table_ui = table_ui_dict[material_active_tab]

        table_data, column_names = o_gui.collect_table_data(table_ui=table_ui)
        list_hkl, list_lambda = BraggEdgeElementHandler.extract_hkl_lambda_from_table(table_data=table_data)

        self.parent.selected_element_bragg_edges_array = list_lambda
        self.parent.selected_element_hkl_array = list_hkl
        self.parent.selected_element_name = "FIXME"

        self.reset_scroll_bar_in_bottom_right_plot()

    @staticmethod
    def extract_hkl_lambda_from_table(table_data=None):
        """
        using the table from the pre-defined, method1 and method2, will extract the rows into hkl and lambda list
        """
        list_hkl = []
        list_lambda = []
        for _index in table_data.keys():
            _row_entry = table_data[_index]
            _row_hkl = [_row_entry['h'],
                        _row_entry['k'],
                        _row_entry['l']]
            list_hkl.append(_row_hkl)

            if 'd0' in _row_entry.keys():
                if _row_entry['d0'] is None:
                    continue
                list_lambda.append(float(_row_entry['d0']) * 2)
            else:
                list_lambda.append(_row_entry[f'\u03BB\u2090'])

        return list_hkl, list_lambda

    def reset_scroll_bar_in_bottom_right_plot(self):

        _selected_element_bragg_edges_array = self.parent.selected_element_bragg_edges_array
        nbr_hkl_in_list = len(_selected_element_bragg_edges_array)
        scrollbar_max = nbr_hkl_in_list - MATERIAL_BRAGG_PEAK_TO_DISPLAY_AT_THE_SAME_TIME

        self.parent.hkl_scrollbar_dict = {ScrollBarParameters.maximum: scrollbar_max,
                                          ScrollBarParameters.value: scrollbar_max}


class BraggEdgeElementCalculator:

    element_name = None
    lattice_value = None
    crystal_structure = None

    hkl_array = None
    lambda_array = None
    d0_array = None

    def __init__(self, element_name=None, lattice_value=None, crystal_structure=None):
        self.element_name = element_name
        self.lattice_value = lattice_value
        self.crystal_structure = crystal_structure

    def run(self):
        _element_dictionary = {'name': self.element_name,
                               'lattice': self.lattice_value,
                               'crystal_structure': self.crystal_structure}

        _handler = BraggEdge(new_material=[_element_dictionary])

        self.hkl_array = _handler.hkl[self.element_name]
        self.lambda_array = _handler.bragg_edges[self.element_name]
        self.d0_array = [_value/2. for _value in self.lambda_array]
