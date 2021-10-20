import os

from .. import DataType
from ..step1.data_handler import DataHandler
from ..step1.gui_handler import Step1GuiHandler
from ..step2.plot import Step2Plot
from ..utilities.gui_handler import GuiHandler


class LoadLoadDataTab:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def sample(self):

        session_dict = self.session_dict

        list_sample_files = self.session_dict[DataType.sample]['list files']
        if list_sample_files:
            input_folder = session_dict[DataType.sample]['current folder']
            self.parent.image_view_settings[DataType.sample]['state'] = session_dict[DataType.sample]['image view ' \
                                                                                                      'state']
            self.parent.image_view_settings[DataType.sample]['histogram'] = session_dict[DataType.sample][
                'image view histogram']

            print(session_dict[DataType.sample]['image view histogram'])

            o_data_handler = DataHandler(parent=self.parent,
                                         data_type=DataType.sample)
            list_sample_files_fullname = [os.path.join(input_folder, _file) for _file in list_sample_files]
            o_data_handler.load_files(list_of_files=list_sample_files_fullname)
            time_spectra_file = session_dict[DataType.sample]['time spectra filename']
            o_data_handler.load_time_spectra(time_spectra_file=time_spectra_file)
            list_files_selected = session_dict[DataType.sample]['list files selected']
            self.parent.list_roi[DataType.sample] = session_dict[DataType.sample]['list rois']
            o_gui = Step1GuiHandler(parent=self.parent, data_type=DataType.sample)
            o_gui.initialize_rois_and_labels()
            for _row_selected in list_files_selected:
                _item = self.parent.ui.list_sample.item(_row_selected)
                _item.setSelected(True)
            o_gui.check_time_spectra_widgets()
            o_gui.check_step1_widgets()
            self.parent.check_files_error()
            self.parent.retrieve_general_infos(data_type=DataType.sample)
            self.parent.retrieve_general_data_infos(data_type=DataType.sample)

            o_step2_plot = Step2Plot(parent=self.parent)
            o_step2_plot.prepare_data()
            o_step2_plot.init_roi_table()

    def ob(self):

        session_dict = self.session_dict

        self.parent.image_view_settings[DataType.ob]['state'] = session_dict[DataType.ob]['image view state']
        self.parent.image_view_settings[DataType.ob]['histogram'] = session_dict[DataType.ob]['image view histogram']
        list_ob_files = session_dict[DataType.ob]['list files']
        if list_ob_files:
            input_folder = session_dict[DataType.ob]['current folder']
            o_data_handler = DataHandler(parent=self.parent,
                                         data_type=DataType.ob)
            list_ob_files_fullname = [os.path.join(input_folder, _file) for _file in list_ob_files]
            o_data_handler.load_files(list_of_files=list_ob_files_fullname)
        list_files_selected = session_dict[DataType.ob]['list files selected']
        self.parent.list_roi[DataType.ob] = session_dict[DataType.ob]['list rois']
        o_gui = Step1GuiHandler(parent=self.parent, data_type=DataType.ob)
        o_gui.initialize_rois_and_labels()
        for _row_selected in list_files_selected:
            _item = self.parent.ui.list_open_beam.item(_row_selected)
            _item.setSelected(True)

    def instrument(self):

        session_dict = self.session_dict

        o_gui = GuiHandler(parent=self.parent)
        list_ui = {'distance': self.parent.ui.distance_source_detector,
                   'beam': self.parent.ui.beam_rate,
                   'detector': self.parent.ui.detector_offset}

        for _key in list_ui.keys():
            list_ui[_key].blockSignals(True)

        o_gui.set_index_selected(index=session_dict["instrument"]["beam index"], ui=list_ui['beam'])
        o_gui.set_text(value=session_dict["instrument"]["distance source detector"], ui=list_ui['distance'])

        for _key in list_ui.keys():
            list_ui[_key].blockSignals(False)

        o_gui.set_text(value=session_dict["instrument"]["detector value"], ui=list_ui['detector'])
