import os

from src.ibeatles import DataType
from src.ibeatles.all_steps.material import Material as AllStepsMaterial
from src.ibeatles.step1.data_handler import DataHandler
from src.ibeatles.step1.gui_handler import Step1GuiHandler
from src.ibeatles.step2.plot import Step2Plot
from src.ibeatles.utilities.gui_handler import GuiHandler
from src.ibeatles.utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities
from src.ibeatles.session import SessionKeys, SessionSubKeys


class LoadLoadDataTab:
    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict
        self.combine_algo = (
            "sum" if self.parent.ui.roi_add_button.isChecked() else "mean"
        )

    def sample(self):
        session_dict = self.session_dict
        data_type = DataType.sample

        list_sample_files = self.session_dict[data_type][SessionSubKeys.list_files]
        if list_sample_files:
            input_folder = session_dict[data_type][SessionSubKeys.current_folder]
            self.parent.image_view_settings[data_type]["state"] = session_dict[
                data_type
            ][SessionSubKeys.image_view_state]
            o_data_handler = DataHandler(parent=self.parent, data_type=data_type)
            list_sample_files_fullname = [
                os.path.join(input_folder, _file) for _file in list_sample_files
            ]
            o_data_handler.load_files(list_of_files=list_sample_files_fullname)
            time_spectra_file = session_dict[data_type][
                SessionSubKeys.time_spectra_filename
            ]
            o_data_handler.load_time_spectra(time_spectra_file=time_spectra_file)
            list_files_selected = session_dict[data_type][
                SessionSubKeys.list_files_selected
            ]
            if not list_files_selected:
                list_files_selected = [0]
            self.parent.list_roi[data_type] = session_dict[data_type][
                SessionSubKeys.list_rois
            ]
            o_gui = Step1GuiHandler(parent=self.parent, data_type=data_type)
            o_gui.initialize_rois_and_labels()
            self.parent.ui.list_sample.blockSignals(True)
            for _row_selected in list_files_selected:
                _item = self.parent.ui.list_sample.item(_row_selected)
                _item.setSelected(True)
            self.parent.ui.list_sample.blockSignals(False)
            o_gui.check_time_spectra_widgets()
            o_gui.check_step1_widgets()
            # self.parent.check_files_error()
            self.parent.retrieve_general_infos(data_type=data_type)
            self.parent.retrieve_general_data_infos(data_type=data_type)
            self.parent.infos_window_update(data_type=data_type)

            o_step2_plot = Step2Plot(parent=self.parent)
            o_step2_plot.prepare_data()
            o_step2_plot.init_roi_table()

            o_pyqt = PyqtgraphUtilities(
                parent=self.parent,
                image_view=self.parent.ui.image_view,
                data_type=data_type,
            )
            o_pyqt.set_state(session_dict[data_type][SessionSubKeys.image_view_state])
            histogram_level = session_dict[data_type][
                SessionSubKeys.image_view_histogram
            ][self.combine_algo]
            o_pyqt.set_histogram_level(histogram_level=histogram_level)

    def ob(self):
        session_dict = self.session_dict
        data_type = DataType.ob

        self.parent.image_view_settings[data_type]["state"] = session_dict[data_type][
            SessionSubKeys.image_view_state
        ]
        # self.parent.image_view_settings[data_type]['histogram'][self.combine_algo] = \
        #     session_dict[data_type][SessionSubKeys.image_view_histogram]
        list_ob_files = session_dict[data_type][SessionSubKeys.list_files]
        if list_ob_files:
            input_folder = session_dict[data_type][SessionSubKeys.current_folder]
            o_data_handler = DataHandler(parent=self.parent, data_type=data_type)
            list_ob_files_fullname = [
                os.path.join(input_folder, _file) for _file in list_ob_files
            ]
            o_data_handler.load_files(list_of_files=list_ob_files_fullname)
        list_files_selected = session_dict[data_type][
            SessionSubKeys.list_files_selected
        ]
        self.parent.list_roi[data_type] = session_dict[data_type][
            SessionSubKeys.list_rois
        ]
        o_gui = Step1GuiHandler(parent=self.parent, data_type=data_type)
        o_gui.initialize_rois_and_labels()
        self.parent.ui.list_open_beam.blockSignals(True)
        for _row_selected in list_files_selected:
            _item = self.parent.ui.list_open_beam.item(_row_selected)
            _item.setSelected(True)
        self.parent.ui.list_open_beam.blockSignals(False)

        o_pyqt = PyqtgraphUtilities(
            parent=self.parent,
            image_view=self.parent.ui.ob_image_view,
            data_type=data_type,
        )
        o_pyqt.set_state(session_dict[data_type][SessionSubKeys.image_view_state])
        o_pyqt.reload_histogram_level()
        histogram_level = session_dict[data_type][SessionSubKeys.image_view_histogram][
            self.combine_algo
        ]
        o_pyqt.set_histogram_level(histogram_level=histogram_level)

    def instrument(self):
        session_dict = self.session_dict

        o_gui = GuiHandler(parent=self.parent)
        list_ui_data = {
            "distance": self.parent.ui.distance_source_detector,
            "beam": self.parent.ui.beam_rate,
            "detector": self.parent.ui.detector_offset,
        }

        for _key in list_ui_data.keys():
            list_ui_data[_key].blockSignals(True)

        o_gui.set_index_selected(
            index=session_dict[SessionKeys.instrument][SessionSubKeys.beam_index],
            ui=list_ui_data["beam"],
        )
        o_gui.set_text(
            value=session_dict[SessionKeys.instrument][
                SessionSubKeys.distance_source_detector
            ],
            ui=list_ui_data["distance"],
        )

        for _key in list_ui_data.keys():
            list_ui_data[_key].blockSignals(False)

        o_gui.set_text(
            value=session_dict[SessionKeys.instrument][SessionSubKeys.detector_value],
            ui=list_ui_data["detector"],
        )

    def material(self):
        material_session_dict = self.session_dict[SessionKeys.material]

        material_mode = material_session_dict[SessionSubKeys.material_mode]
        o_gui = GuiHandler(parent=self.parent)
        o_gui.set_material_active_tab(active_tab_mode=material_mode)

        # pre-defined
        pre_defined_material_index = material_session_dict[SessionSubKeys.pre_defined][
            SessionSubKeys.pre_defined_selected_element_index
        ]
        self.parent.ui.pre_defined_list_of_elements.setCurrentIndex(
            pre_defined_material_index
        )

        # custom
        custom_material_name = material_session_dict[
            SessionSubKeys.custom_material_name
        ]
        self.parent.ui.user_defined_element_name.setText(custom_material_name)

        # method 1
        index_of_element = material_session_dict[SessionSubKeys.custom_method1][
            SessionSubKeys.user_defined_fill_fields_with_element_index
        ]
        self.parent.ui.user_defined_list_of_elements.blockSignals(True)
        self.parent.ui.user_defined_list_of_elements.setCurrentIndex(index_of_element)
        self.parent.ui.user_defined_list_of_elements.blockSignals(False)

        lattice = material_session_dict[SessionSubKeys.custom_method1][
            SessionSubKeys.lattice
        ]
        if not (lattice == ""):
            self.parent.ui.method1_lattice_value_2.blockSignals(True)
            self.parent.ui.method1_lattice_value_2.setText(f"{float(lattice):.3f}")
            self.parent.ui.method1_lattice_value_2.blockSignals(False)

        crystal_structure_index = material_session_dict[SessionSubKeys.custom_method1][
            SessionSubKeys.crystal_structure_index
        ]
        self.parent.ui.method1_crystal_value_2.blockSignals(True)
        self.parent.ui.method1_crystal_value_2.setCurrentIndex(crystal_structure_index)
        self.parent.ui.method1_crystal_value_2.blockSignals(False)

        method1_table = material_session_dict[SessionSubKeys.custom_method1][
            SessionSubKeys.material_hkl_table
        ]
        method1_column_names = material_session_dict[SessionSubKeys.custom_method1][
            SessionSubKeys.column_names
        ]
        self.parent.ui.method1_tableWidget.blockSignals(True)
        GuiHandler.fill_table_data(
            table_ui=self.parent.ui.method1_tableWidget,
            table_dict=method1_table,
            column_names=method1_column_names,
        )
        self.parent.ui.method1_tableWidget.blockSignals(False)

        method2_table = material_session_dict[SessionSubKeys.custom_method2][
            SessionSubKeys.material_hkl_table
        ]
        method2_column_names = material_session_dict[SessionSubKeys.custom_method2][
            SessionSubKeys.column_names
        ]
        GuiHandler.fill_table_data(
            table_ui=self.parent.ui.method2_tableWidget,
            table_dict=method2_table,
            column_names=method2_column_names,
        )

        o_material = AllStepsMaterial(parent=self.parent)
        o_material.check_status_of_all_widgets()
