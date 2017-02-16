import numpy as np


class FittingHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        self.fitting_ui = self.parent.fitting_ui
        
    def display_image(self, data=[]):
        if not(data == []):
            self.fitting_ui.data = data
            self.fitting_ui.image_view.setImage(data)
        else:
            if not self.parent.data_metadata['normalized']['data_live_selection'] == []:
                data = np.array(self.parent.data_metadata['normalized']['data_live_selection'])
                if not(data == np.array([])):
                    self.fitting_ui.image_view.setImage(data)
                    self.fitting_ui.data = data
                
                
            

  