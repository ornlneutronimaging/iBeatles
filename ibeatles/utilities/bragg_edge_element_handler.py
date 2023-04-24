from ibeatles.utilities.gui_handler import GuiHandler
from neutronbraggedge.braggedge import BraggEdge


class BraggEdgeElementHandler:
    bragg_edges_array = []

    def __init__(self, parent=None):
        self.parent = parent

        o_gui = GuiHandler(parent=self.parent)

        element_name = str(o_gui.get_text_selected(ui=self.parent.ui.list_of_elements))
        lattice_value = float(o_gui.get_text(ui=self.parent.ui.lattice_parameter))
        crystal_structure = str(o_gui.get_text_selected(ui=self.parent.ui.crystal_structure))

        _element_dictionary = {'name': element_name,
                               'lattice': lattice_value,
                               'crystal_structure': crystal_structure}

        o_calculator = BraggEdgeElementCalculator(element_name=element_name,
                                                  lattice_value=lattice_value,
                                                  crystal_structure=crystal_structure)
        o_calculator.run()

        selected_element_bragg_edges_array = o_calculator.lambda_array
        selected_element_hkl_array = o_calculator.hkl_array

        self.parent.selected_element_bragg_edges_array = selected_element_bragg_edges_array
        self.parent.selected_element_hkl_array = selected_element_hkl_array
        self.parent.selected_element_name = element_name

        # modified the fitting window list of h,k,l if window is alive
        if self.parent.fitting_ui:
            hkl_list = selected_element_hkl_array
            str_hkl_list = ["{},{},{}".format(_hkl[0], _hkl[1], _hkl[2]) for _hkl in hkl_list]
            self.parent.fitting_ui.ui.hkl_list_ui.clear()
            self.parent.fitting_ui.ui.hkl_list_ui.addItems(str_hkl_list)
            self.parent.fitting_ui.ui.material_groupBox.setTitle(element_name)


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
