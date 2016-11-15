class GuiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def get_active_tab(self):
        """return either 'sample', 'ob', 'normalization' or 'normalized' """
        top_tab_index = self.parent.ui.tabWidget.currentIndex()
        if top_tab_index == 1:
            return 'normalization'
        if top_tab_index == 2:
            return 'normalized'
        if top_tab_index == 0:
            load_data_tab_index = self.parent.ui.toolBox.currentIndex()
            if load_data_tab_index == 0:
                return 'sample'
            if load_data_tab_index == 1:
                return 'ob'