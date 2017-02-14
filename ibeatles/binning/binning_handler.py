class BinningHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        self.binning_ui = self.parent.binning_ui
        
    def display_image(self, data=[]):
        self.binning_ui.image_view.setImage(data)

  