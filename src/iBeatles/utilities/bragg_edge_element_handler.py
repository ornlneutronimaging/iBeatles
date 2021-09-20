import numpy as np

from ..utilities.gui_handler import GuiHandler
from neutronbraggedge.braggedge import BraggEdge


class BraggEdgeElementHandler(object):
    bragg_edges_array = []

    def __init__(self, parent=None):
        self.parent = parent

        o_gui = GuiHandler(parent=self.parent)
        element_name = str(o_gui.get_text_selected(ui=self.parent.ui.list_of_elements))
        lattice_value = np.float(o_gui.get_text(ui=self.parent.ui.lattice_parameter))
        crystal_structure = str(o_gui.get_text_selected(ui=self.parent.ui.crystal_structure))

        _element_dictionary = {'name': element_name,
                               'lattice': lattice_value,
                               'crystal_structure': crystal_structure}

        _handler = BraggEdge(new_material=[_element_dictionary])
        self.parent.selected_element_bragg_edges_array = _handler.bragg_edges[element_name]
        self.parent.selected_element_hkl_array = _handler.hkl[element_name]
        self.parent.selected_element_name = element_name

        # modified the fitting window list of h,k,l if window is alive
        if self.parent.fitting_ui:
            hkl_list = _handler.hkl[element_name]
            str_hkl_list = ["{},{},{}".format(_hkl[0], _hkl[1], _hkl[2]) for _hkl in hkl_list]
            self.parent.fitting_ui.ui.hkl_list_ui.clear()
            self.parent.fitting_ui.ui.hkl_list_ui.addItems(str_hkl_list)
            self.parent.fitting_ui.ui.material_groupBox.setTitle(element_name)
