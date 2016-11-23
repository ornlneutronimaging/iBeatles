from ibeatles.utilities.gui_handler import GuiHandler


class BraggEdgeSelectionHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent

        o_gui = GuiHandler(parent = self.parent)
        self.data_type = o_gui.get_active_tab()
        
    def update_dropdown(self):
        
        lr = self.parent.list_bragg_edge_selection_id[self.data_type]
        print(lr.getRegion())