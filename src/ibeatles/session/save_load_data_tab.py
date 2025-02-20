import logging
import os

from src.ibeatles import DataType
from src.ibeatles.session.save_tab import SaveTab
from src.ibeatles.utilities.gui_handler import GuiHandler
from src.ibeatles.utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities

from src.ibeatles.session import SessionKeys, SessionSubKeys


class SaveLoadDataTab(SaveTab):
    def sample(self):
        """record all the parameters of the Load Data tab / Sample accordion tab"""

        data_type = DataType.sample

        list_files = self.parent.list_files[data_type]
        current_folder = self.parent.data_metadata[data_type]["folder"]
        time_spectra_filename = self.parent.data_metadata[data_type]["time_spectra"][
            "filename"
        ]
        list_files_selected = [
            int(index) for index in self.parent.list_file_selected[data_type]
        ]
        list_roi = self.parent.list_roi[data_type]
        o_pyqt = PyqtgraphUtilities(
            parent=self.parent,
            image_view=self.parent.ui.image_view,
            data_type=data_type,
        )
        state = o_pyqt.get_state()
        o_pyqt.save_histogram_level()
        histogram = self.parent.image_view_settings[data_type]["histogram"]

        extension = os.path.splitext(list_files[0])

        logging.info("Recording parameters of Load Data / Sample")
        logging.info(f" len(list files) = {len(list_files)}")
        logging.info(f" current folder: {current_folder}")
        logging.info(f" time spectra filename: {time_spectra_filename}")
        logging.info(f" list files selected: {list_files_selected}")
        logging.info(f" len(list rois): {len(list_roi)}")
        logging.info(f" state: {state}")
        logging.info(f" histogram: {histogram}")
        logging.info(f" extension: {extension}")

        self.session_dict[data_type][SessionSubKeys.list_files] = list_files
        self.session_dict[data_type][SessionSubKeys.current_folder] = current_folder
        self.session_dict[data_type][SessionSubKeys.time_spectra_filename] = (
            time_spectra_filename
        )
        self.session_dict[data_type][SessionSubKeys.extension] = extension
        self.session_dict[data_type][SessionSubKeys.list_files_selected] = (
            list_files_selected
        )
        self.session_dict[data_type][SessionSubKeys.list_rois] = list_roi
        self.session_dict[data_type][SessionSubKeys.image_view_state] = state
        self.session_dict[data_type][SessionSubKeys.image_view_histogram] = histogram

    def ob(self):
        """record all the parameters of the Load Data tab / ob accordion tab"""

        data_type = DataType.ob

        list_files = self.parent.list_files[data_type]
        current_folder = self.parent.data_metadata[data_type]["folder"]
        list_files_selected = [
            int(index) for index in self.parent.list_file_selected[data_type]
        ]
        list_roi = self.parent.list_roi[data_type]
        o_pyqt = PyqtgraphUtilities(
            parent=self.parent,
            image_view=self.parent.ui.ob_image_view,
            data_type=data_type,
        )
        state = o_pyqt.get_state()
        o_pyqt.save_histogram_level()
        histogram = self.parent.image_view_settings[data_type]["histogram"]

        logging.info("Recording parameters of Load Data / OB")
        logging.info(f" len(list files) = {len(list_files)}")
        logging.info(f" current folder: {current_folder}")
        logging.info(f" list files selected: {list_files_selected}")
        logging.info(f" len(list rois): {len(list_roi)}")
        logging.info(f" state: {state}")
        logging.info(f" histogram: {histogram}")

        self.session_dict[data_type][SessionSubKeys.list_files] = list_files
        self.session_dict[data_type][SessionSubKeys.current_folder] = current_folder
        self.session_dict[data_type][SessionSubKeys.list_files_selected] = (
            list_files_selected
        )
        self.session_dict[data_type][SessionSubKeys.list_rois] = list_roi
        self.session_dict[data_type][SessionSubKeys.image_view_state] = state
        self.session_dict[data_type][SessionSubKeys.image_view_histogram] = histogram

    def instrument(self):
        """record the settings of the instrument such as offset, distance source/detector ..."""

        list_ui = {
            "distance": self.parent.ui.distance_source_detector,
            "beam": self.parent.ui.beam_rate,
            "detector": self.parent.ui.detector_offset,
        }

        o_gui = GuiHandler(parent=self.parent)
        distance_value = o_gui.get_text(ui=list_ui["distance"])
        detector_value = o_gui.get_text(ui=list_ui["detector"])
        beam_index = o_gui.get_index_selected(ui=list_ui["beam"])

        logging.info("Recording instrument")
        logging.info(f" distance source detector: {distance_value}")
        logging.info(f" detector value: {detector_value}")
        logging.info(f" beam index: {beam_index}")

        self.session_dict[SessionKeys.instrument][
            SessionSubKeys.distance_source_detector
        ] = distance_value
        self.session_dict[SessionKeys.instrument][SessionSubKeys.detector_value] = (
            detector_value
        )
        self.session_dict[SessionKeys.instrument][SessionSubKeys.beam_index] = (
            beam_index
        )

    def material(self):
        """record the material settings (element selected, full list, crystal structure, lattice"""

        # pre-defined
        pre_defined_material_index = (
            self.parent.ui.pre_defined_list_of_elements.currentIndex()
        )
        o_gui = GuiHandler(parent=self.parent)
        material_mode = o_gui.get_material_active_tab()

        # custom
        custom_material_name = self.parent.ui.user_defined_element_name.text()

        ## method1
        index_element = self.parent.ui.user_defined_list_of_elements.currentIndex()
        lattice_value = self.parent.ui.method1_lattice_value_2.text()
        crystal_structure_index = self.parent.ui.method1_crystal_value_2.currentIndex()
        method1_table, column1_names = GuiHandler.collect_table_data(
            table_ui=self.parent.ui.method1_tableWidget
        )

        ## method 2
        method2_table, column2_names = GuiHandler.collect_table_data(
            table_ui=self.parent.method2_tableWidget
        )

        self.session_dict[SessionKeys.material] = {
            SessionSubKeys.material_mode: material_mode,
            SessionSubKeys.pre_defined: {
                SessionSubKeys.pre_defined_selected_element_index: pre_defined_material_index
            },
            SessionSubKeys.custom_material_name: custom_material_name,
            SessionSubKeys.custom_method1: {
                SessionSubKeys.user_defined_fill_fields_with_element_index: index_element,
                SessionSubKeys.lattice: lattice_value,
                SessionSubKeys.crystal_structure_index: crystal_structure_index,
                SessionSubKeys.material_hkl_table: method1_table,
                SessionSubKeys.column_names: column1_names,
            },
            SessionSubKeys.custom_method2: {
                SessionSubKeys.material_hkl_table: method2_table,
                SessionSubKeys.column_names: column2_names,
            },
        }

        logging.info("Recording Material")
        logging.info(f" pre-defined material index: {pre_defined_material_index}")
        logging.info(f" custom material name: {custom_material_name}")
        logging.info(f" index of element used to fill fields: {index_element}")
        logging.info(f" custom method1 lattice: {lattice_value}")
        logging.info(
            f" custom method1 crystal structure index: {crystal_structure_index}"
        )
        logging.info(f" custom method1 table: {method1_table}")
        logging.info(f" custom method2 table: {method2_table}")
