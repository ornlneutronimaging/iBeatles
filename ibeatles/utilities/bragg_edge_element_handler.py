import numpy as np

from ibeatles.utilities.gui_handler import GuiHandler
from neutronbraggedge.braggedge import BraggEdge


class BraggEdgeElementHandler(object):
    
    bragg_edges_array = []

    def __init__(self, parent=None):
        self.parent = parent
        
        o_gui = GuiHandler(parent = self.parent)
        element_name = str(o_gui.get_text_selected(ui = self.parent.ui.list_of_elements))
        lattice_value = np.float(o_gui.get_text(ui = self.parent.ui.lattice_parameter))
        crystal_structure = str(o_gui.get_text_selected(ui = self.parent.ui.crystal_structure))
        
        _element_dictionary = {'name': element_name,
                               'lattice': lattice_value,
                               'crystal_structure': crystal_structure}
        
        _handler = BraggEdge(new_material = [_element_dictionary])
        self.bragg_edges_array = _handler.bragg_edges[element_name]
        print(self.bragg_edges_array)
