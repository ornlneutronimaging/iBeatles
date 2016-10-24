from ibeatles.step1.plot import Step1Plot
from ibeatles.utilities.retrieve_data_infos import RetrieveGeneralFileInfos, RetrieveSelectedFileDataInfos


class Step1GuiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def load_data_tab_changed(self, tab_index=0):
        if tab_index == 0:
            data_preview_box_label = "Sample Image Preview"
            o_general_infos = RetrieveGeneralFileInfos(parent = self.parent, 
                                                       data_type = 'sample')
            o_selected_infos = RetrieveSelectedFileDataInfos(parent = self.parent,
                                                                  data_type = 'sample')
        else:
            data_preview_box_label = "Open Beam Image Preview"
            o_general_infos = RetrieveGeneralFileInfos(parent = self.parent, 
                                                       data_type = 'ob')
            o_selected_infos = RetrieveSelectedFileDataInfos(parent = self.parent,
                                                                  data_type = 'ob')
        
        self.parent.ui.data_preview_box.setTitle(data_preview_box_label)
        o_general_infos.update()            
        o_selected_infos.update()
        
        
    def init_gui(self):
        # define position and size
        rect = self.parent.geometry()
        self.parent.setGeometry(10, 10, rect.width(), rect.height())

        # remove axis from image preview
        self.parent.ui.preview_widget.canvas.ax.axis('off')
        self.parent.ui.preview_widget.draw()
        
    def select_load_data_row(self, data_type='sample', row=0):
        if data_type == 'sample':
            self.parent.ui.list_sample.setCurrentRow(row)
        else:
            self.parent.ui.list_open_beam.setCurrentRow(row)
            
        o_step1_plot = Step1Plot(parent = self.parent)
        o_step1_plot.display_2d_preview()
    