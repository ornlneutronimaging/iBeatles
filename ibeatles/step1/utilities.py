from ibeatles.utilities.gui_handler import GuiHandler


def get_tab_selected(parent=None):
    '''
    return: 'sample', 'ob', 'normalization' or 'normalized'
    
    '''
    o_gui = GuiHandler(parent = parent)
    return o_gui.get_active_tab()

