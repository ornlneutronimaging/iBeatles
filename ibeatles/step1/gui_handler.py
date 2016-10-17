from ibeatles.step1.plot import Step1Plot


class Step1GuiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def load_data_tab_changed(self, tab_index=0):
        if tab_index == 0:
            data_preview_box_label = "Sample Image(s) Preview"
        else:
            data_preview_box_label = "Open Beam Image(s) Preview"
        
        self.parent.ui.data_preview_box.setTitle(data_preview_box_label)
        
    def init_gui(self):
        self.parent.ui.preview_widget.canvas.ax.axis('off')
        self.parent.ui.preview_widget.draw()
        
    def select_load_data_row(self, data_type='sample', row=0):
        if data_type == 'sample':
            self.parent.ui.list_sample.setCurrentRow(row)
        else:
            self.parent.ui.list_open_beam.setCurrentRow(row)
            
        o_step1_plot = Step1Plot(parent = self.parent)
        o_step1_plot.display_2d_preview()
    