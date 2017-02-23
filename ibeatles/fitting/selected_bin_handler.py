class SelectedBinsHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        self.fitting_ui = self.parent.fitting_ui
        
    def update_bins_selected(self):
        selection = self.fitting_ui.ui.value_table.selectedRanges()
        nbr_selection = len(selection)
        print(nbr_selection)
    
    def update_bins_locked(self):
        pass