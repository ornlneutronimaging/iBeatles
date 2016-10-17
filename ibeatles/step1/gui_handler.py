class Step1GuiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def load_data_tab_changed(self, tab_index=0):
        if tab_index == 0:
            data_preview_box_label = "Sample Image(s) Preview"
        else:
            data_preview_box_label = "Open Beam Image(s) Preview"
        
        self.parent.ui.data_preview_box.setTitle(data_preview_box_label)