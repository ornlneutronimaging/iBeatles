import os

from ibeatles import DataType, Material
from ibeatles.step1.data_handler import DataHandler
from ibeatles.step1.gui_handler import Step1GuiHandler
from ibeatles.step2.plot import Step2Plot
from ibeatles.utilities.gui_handler import GuiHandler
from ibeatles.utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities
from ibeatles.session import SessionKeys, SessionSubKeys


class LoadLoadDataTab:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict
        self.combine_algo = 'sum' if self.parent.ui.roi_add_button.isChecked() else 'mean'

    def sample(self):

        session_dict = self.session_dict
        data_type = DataType.sample

        list_sample_files = self.session_dict[data_type][SessionSubKeys.list_files]
        if list_sample_files:
            input_folder = session_dict[data_type][SessionSubKeys.current_folder]
            self.parent.image_view_settings[data_type]['state'] = \
                session_dict[data_type][SessionSubKeys.image_view_state]
            o_data_handler = DataHandler(parent=self.parent,
                                         data_type=data_type)
            list_sample_files_fullname = [os.path.join(input_folder, _file) for _file in list_sample_files]
            o_data_handler.load_files(list_of_files=list_sample_files_fullname)
            time_spectra_file = session_dict[data_type][SessionSubKeys.time_spectra_filename]
            o_data_handler.load_time_spectra(time_spectra_file=time_spectra_file)
            list_files_selected = session_dict[data_type][SessionSubKeys.list_files_selected]
            self.parent.list_roi[data_type] = session_dict[data_type][SessionSubKeys.list_rois]
            o_gui = Step1GuiHandler(parent=self.parent, data_type=data_type)
            o_gui.initialize_rois_and_labels()
            self.parent.ui.list_sample.blockSignals(True)
            for _row_selected in list_files_selected:
                _item = self.parent.ui.list_sample.item(_row_selected)
                _item.setSelected(True)
            self.parent.ui.list_sample.blockSignals(False)
            o_gui.check_time_spectra_widgets()
            o_gui.check_step1_widgets()
            self.parent.check_files_error()
            self.parent.retrieve_general_infos(data_type=data_type)
            self.parent.retrieve_general_data_infos(data_type=data_type)
            self.parent.infos_window_update(data_type=data_type)

            o_step2_plot = Step2Plot(parent=self.parent)
            o_step2_plot.prepare_data()
            o_step2_plot.init_roi_table()

            o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                        image_view=self.parent.ui.image_view,
                                        data_type=data_type)
            o_pyqt.set_state(session_dict[data_type][SessionSubKeys.image_view_state])
            histogram_level = session_dict[data_type][SessionSubKeys.image_view_histogram][self.combine_algo]
            o_pyqt.set_histogram_level(histogram_level=histogram_level)

    def ob(self):

        session_dict = self.session_dict
        data_type = DataType.ob

        self.parent.image_view_settings[data_type]['state'] = session_dict[data_type][SessionSubKeys.image_view_state]
        # self.parent.image_view_settings[data_type]['histogram'][self.combine_algo] = \
        #     session_dict[data_type][SessionSubKeys.image_view_histogram]
        list_ob_files = session_dict[data_type][SessionSubKeys.list_files]
        if list_ob_files:
            input_folder = session_dict[data_type][SessionSubKeys.current_folder]
            o_data_handler = DataHandler(parent=self.parent,
                                         data_type=data_type)
            list_ob_files_fullname = [os.path.join(input_folder, _file) for _file in list_ob_files]
            o_data_handler.load_files(list_of_files=list_ob_files_fullname)
        list_files_selected = session_dict[data_type][SessionSubKeys.list_files_selected]
        self.parent.list_roi[data_type] = session_dict[data_type][SessionSubKeys.list_rois]
        o_gui = Step1GuiHandler(parent=self.parent, data_type=data_type)
        o_gui.initialize_rois_and_labels()
        self.parent.ui.list_open_beam.blockSignals(True)
        for _row_selected in list_files_selected:
            _item = self.parent.ui.list_open_beam.item(_row_selected)
            _item.setSelected(True)
        self.parent.ui.list_open_beam.blockSignals(False)

        o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                    image_view=self.parent.ui.ob_image_view,
                                    data_type=data_type)
        o_pyqt.set_state(session_dict[data_type][SessionSubKeys.image_view_state])
        o_pyqt.reload_histogram_level()
        histogram_level = session_dict[data_type][SessionSubKeys.image_view_histogram][self.combine_algo]
        o_pyqt.set_histogram_level(histogram_level=histogram_level)

    def instrument(self):

        session_dict = self.session_dict

        o_gui = GuiHandler(parent=self.parent)
        list_ui_data = {'distance': self.parent.ui.distance_source_detector,
                        'beam': self.parent.ui.beam_rate,
                        'detector': self.parent.ui.detector_offset}

        for _key in list_ui_data.keys():
            list_ui_data[_key].blockSignals(True)

        o_gui.set_index_selected(index=session_dict[SessionKeys.instrument][SessionSubKeys.beam_index],
                                 ui=list_ui_data['beam'])
        o_gui.set_text(value=session_dict[SessionKeys.instrument][SessionSubKeys.distance_source_detector],
                       ui=list_ui_data['distance'])

        for _key in list_ui_data.keys():
            list_ui_data[_key].blockSignals(False)

        o_gui.set_text(value=session_dict[SessionKeys.instrument][SessionSubKeys.detector_value],
                       ui=list_ui_data['detector'])

    def material(self):

        session_dict = self.session_dict

        selected_element_index = session_dict[SessionKeys.material][SessionSubKeys.selected_element][SessionSubKeys.index]
        lattice = session_dict[SessionKeys.material][SessionSubKeys.lattice]
        crystal_structure_index = session_dict[SessionKeys.material][SessionSubKeys.crystal_structure][SessionSubKeys.index]
        count = self.parent.ui.list_of_elements.count()
        user_defined_bragg_edge_list = session_dict[SessionKeys.material][Material.user_defined_bragg_edge_list]
        self.parent.user_defined_bragg_edge_list = user_defined_bragg_edge_list

        self.parent.ui.list_of_elements.blockSignals(True)

        if selected_element_index >= count:
           selected_element_name = session_dict[SessionKeys.material][SessionSubKeys.selected_element][SessionSubKeys.name]
           self.parent.ui.list_of_elements.addItem(selected_element_name)

           # only 1 lattice user defined value can be saved between sessions
           self.parent.ui.list_of_elements.setCurrentIndex(count)

        else:
            self.parent.ui.list_of_elements.setCurrentIndex(selected_element_index)

        self.parent.ui.lattice_parameter.setText(lattice)
        self.parent.ui.crystal_structure.setCurrentIndex(crystal_structure_index)

        self.parent.ui.list_of_elements.blockSignals(False)

        o_gui = Step1GuiHandler(parent=self.parent)
        o_gui.update_lattice_and_crystal_when_index_selected()

        self.parent.check_status_of_material_widgets()
        self.parent.list_of_element_index_changed(index=selected_element_index)

        self.parent.pre_defined_element_dropBox_changed(0)
