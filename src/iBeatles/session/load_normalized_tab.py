import os

from .. import DataType
from ..step1.data_handler import DataHandler
from ..step1.gui_handler import Step1GuiHandler
from ..step3.gui_handler import Step3GuiHandler


class LoadNormalized:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def all(self):

        session_dict = self.session_dict
        data_type = DataType.normalized

        list_normalized_files = self.session_dict[data_type]['list files']
        if list_normalized_files:
            input_folder = self.session_dict[data_type]['current folder']
            o_data_handler = DataHandler(parent=self.parent,
                                         data_type=data_type)
            list_normalized_files_fullname = [os.path.join(input_folder, _file) for _file in list_normalized_files]
            o_data_handler.load_files(list_of_files=list_normalized_files_fullname)
            time_spectra_file = session_dict[data_type]['time spectra filename']
            o_data_handler.load_time_spectra(time_spectra_file=time_spectra_file)
            list_files_selected = session_dict[data_type]['list files selected']
            self.parent.list_file_selected[data_type] = list_files_selected
            self.parent.list_roi[data_type] = session_dict[data_type]['list rois']
            o_gui = Step1GuiHandler(parent=self.parent, data_type=data_type)
            o_gui.initialize_rois_and_labels()
            for _row_selected in list_files_selected:
                _item = self.parent.ui.list_normalized.item(_row_selected)
                _item.setSelected(True)
            o_gui.check_time_spectra_widgets()
            self.parent.retrieve_general_infos(data_type=data_type)
            self.parent.retrieve_general_data_infos(data_type=data_type)
            o_gui = Step3GuiHandler(parent=self.parent)
            o_gui.check_widgets()
