class BinningHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def update_plot(self):
        binning_ui = self.parent.binning_ui
        if binning_ui is None:
            return
        
        print("updating binning plot")