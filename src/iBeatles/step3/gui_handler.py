# from iBeatles.py.step1.plot import Step1Plot
from ..utilities.retrieve_data_infos import RetrieveGeneralFileInfos, RetrieveSelectedFileDataInfos


class Step3GuiHandler(object):

    def __init__(self, parent=None):
        self.parent = parent

    def load_normalized_changed(self, tab_index=0):
        if tab_index == 0:
            data_preview_box_label = "Sample Image Preview"
            o_general_infos = RetrieveGeneralFileInfos(parent=self.parent,
                                                       data_type='sample')
            o_selected_infos = RetrieveSelectedFileDataInfos(parent=self.parent,
                                                             data_type='sample')
        else:
            data_preview_box_label = "Open Beam Image Preview"
            o_general_infos = RetrieveGeneralFileInfos(parent=self.parent,
                                                       data_type='ob')
            o_selected_infos = RetrieveSelectedFileDataInfos(parent=self.parent,
                                                             data_type='ob')

        self.parent.ui.data_preview_box.setTitle(data_preview_box_label)
        o_general_infos.update()
        o_selected_infos.update()

    def select_normalized_row(self, row=0):
        self.parent.ui.list_normalized.setCurrentRow(row)

    #        o_step1_plot = Step1Plot(parent = self.parent)
    #        o_step1_plot.display_2d_preview()

    def check_time_spectra_widgets(self):
        time_spectra_data = self.parent.data_metadata['time_spectra']['normalized_folder']
        if self.parent.ui.material_display_checkbox_2.isChecked():
            if time_spectra_data == []:
                _display_error_label = True
            else:
                _display_error_label = False
        else:
            _display_error_label = False

        self.parent.ui.display_warning_2.setVisible(_display_error_label)

    def check_widgets(self):
        # if self.parent.data_files['normalized'] == []:
        #     status = False
        # else:
        #     status = True

        self.parent.ui.actionRotate_Images.setEnabled(True)
