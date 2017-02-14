import numpy as np


class BinningHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        self.binning_ui = self.parent.binning_ui
        
    def display_image(self, data=[]):
        if not(data == []):
            self.binning_ui.data = data
            self.binning_ui.image_view.setImage(data)
        else:
            if not self.parent.data_metadata['normalized']['data_live_selection'] == []:
                data = np.array(self.parent.data_metadata['normalized']['data_live_selection'])
                if not(data == np.array([])):
                    self.binning_ui.image_view.setImage(data)
                    self.binning_ui.data = data
                
                
            

  