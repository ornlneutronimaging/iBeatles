import numpy as np


class BinningHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        self.binning_ui = self.parent.binning_ui
        
    def display_image(self, data=[]):
        if not(data == []):
            self.binning_ui.data = data
            self.parent.binning_line_view['image_view'].setImage(data)
        else:
            data = self.parent.binning_ui.data
            if len(data) == 0:
                return
            else:
                self.parent.binning_line_view['image_view'].setImage(data)
                self.binning_ui.data = data
                    
    def display_selection(self):
        if self.parent.binning_line_view['ui']:
            
            binning_line_view = self.parent.binning_line_view
            line_view_binning = binning_line_view['ui']
#            self.parent.binning_ui.line_view = line_view_binning
            
            pos = binning_line_view['pos']
            adj = binning_line_view['adj']
            lines = binning_line_view['pen']
            
            self.parent.binning_line_view['ui'].setData(pos=pos, 
                                                        adj=adj,
                                                        pen=lines,
                                                        symbol=None,
                                                        pxMode=False)                                  
            
            self.parent.binning_line_view['ui'] = line_view_binning
            self.parent.binning_line_view['pos'] = pos
            self.parent.binning_line_view['adj'] = adj
            self.parent.binning_line_view['pen'] = lines
                
            #self.parent.binning_ui.line_view.setData(pos=pos, 
                                                             #adj=adj,
                                                             #pen=lines,
                                                             #symbol=None,
                                                             #pxMode=False)                                  
        
            #self.parent.binning_ui.line_view_binning = line_view_binning
            #self.parent.binning_ui.pos = pos
            #self.parent.binning_ui.adj = adj
            #self.parent.binning_ui.lines = lines

            

  