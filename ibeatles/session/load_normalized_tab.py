import os

from ibeatles import DataType
from ibeatles.step1.data_handler import DataHandler
from ibeatles.step1.gui_handler import Step1GuiHandler
from ibeatles.step3.gui_handler import Step3GuiHandler
from ibeatles.utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities
from ibeatles.session import SessionKeys, SessionSubKeys


class LoadNormalized:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def all(self):

        session_dict = self.session_dict
        data_type = DataType.normalized

        list_normalized_files = self.session_dict[data_type][SessionSubKeys.list_files]
        if list_normalized_files:
            input_folder = self.session_dict[data_type][SessionSubKeys.current_folder]
            o_data_handler = DataHandler(parent=self.parent,
                                         data_type=data_type)
            list_normalized_files_fullname = [os.path.join(input_folder, _file) for _file in list_normalized_files]
            o_data_handler.load_files(list_of_files=list_normalized_files_fullname)
            time_spectra_file = session_dict[data_type][SessionSubKeys.time_spectra_filename]
            o_data_handler.load_time_spectra(time_spectra_file=time_spectra_file)
            list_files_selected = session_dict[data_type][SessionSubKeys.list_files_selected]
            self.parent.list_file_selected[data_type] = list_files_selected
            self.parent.list_roi[data_type] = session_dict[data_type][SessionSubKeys.list_rois]
            o_gui = Step1GuiHandler(parent=self.parent, data_type=data_type)
            o_gui.initialize_rois_and_labels()
            for _row_selected in list_files_selected:
                _item = self.parent.ui.list_normalized.item(_row_selected)
                _item.setSelected(True)
            self.parent.retrieve_general_infos(data_type=data_type)
            self.parent.retrieve_general_data_infos(data_type=data_type)
            o_gui = Step3GuiHandler(parent=self.parent)
            o_gui.check_widgets()
            o_gui.check_time_spectra_widgets()

            self.parent.image_view_settings[data_type]['state'] = \
                session_dict[data_type][SessionSubKeys.image_view_state]
            self.parent.image_view_settings[data_type]['histogram'] = \
                session_dict[data_type][SessionSubKeys.image_view_histogram]

            o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                        image_view=self.parent.ui.normalized_image_view,
                                        data_type=data_type)
            o_pyqt.set_state(session_dict[data_type][SessionSubKeys.image_view_state])
            o_pyqt.reload_histogram_level()
            histogram_level = session_dict[data_type][SessionSubKeys.image_view_histogram]
            o_pyqt.set_histogram_level(histogram_level=histogram_level)
