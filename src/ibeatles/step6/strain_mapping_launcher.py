from qtpy.QtWidgets import QMainWindow

from src.ibeatles import load_ui, FileType
from src.ibeatles.utilities.status_message_config import (
    StatusMessageStatus,
    show_status_message,
)
from src.ibeatles.widgets.qrangeslider import FakeKey

from src.ibeatles.step6.initialization import Initialization
from src.ibeatles.step6.display import Display
from src.ibeatles.step6.event_handler import EventHandler
from src.ibeatles.step6.get import Get
from src.ibeatles.step6.export import Export
from src.ibeatles.step6 import ParametersToDisplay


class StrainMappingLauncher:
    def __init__(self, parent=None, fitting_parent=None):
        self.parent = parent

        if self.parent.fitting_ui is None:
            show_status_message(
                parent=fitting_parent,
                message="Strain Mapping requires to first launch the fitting window!",
                status=StatusMessageStatus.error,
                duration_s=10,
            )
            show_status_message(
                parent=self.parent,
                message="Strain Mapping requires to first launch the fitting window!",
                status=StatusMessageStatus.error,
                duration_s=10,
            )
        else:
            try:
                strain_mapping_window = StrainMappingWindow(parent=parent)
                strain_mapping_window.show()
                strain_mapping_window.ui.range_slider.keyPressEvent(FakeKey(key="down"))
                self.parent.strain_mapping_ui = strain_mapping_window
            except ValueError:
                show_status_message(
                    parent=fitting_parent,
                    message="Please perform a fitting first",
                    status=StatusMessageStatus.error,
                    duration_s=10,
                )
                show_status_message(
                    parent=self.parent,
                    message="Please perform a fitting first",
                    status=StatusMessageStatus.error,
                    duration_s=10,
                )


class StrainMappingWindow(QMainWindow):
    # slider_nbr_steps = 1000
    slider_min = 0
    slider_max = 1000

    integrated_image = None
    image_size = {"width": None, "height": None}

    # min_max = {'d': {min: -1,
    #                  max: -1},
    #            'strain_mapping': {min: -1,
    #                               max: -1},
    #            }
    min_max = {
        ParametersToDisplay.d: {"min": None, "max": None},
        ParametersToDisplay.strain_mapping: {"min": None, "max": None},
    }

    histogram = {"d": None, "strain_mapping": None, "integrated_image": None}

    previous_parameters_displayed = ParametersToDisplay.d

    colorbar = None

    bin_size = None
    d_array = None
    compact_d_array = None
    strain_mapping_array = None
    compact_strain_mapping_array = None

    def __init__(self, parent=None):
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui("ui_strainMapping.ui", baseinstance=self)
        self.setWindowTitle("6. Strain Mapping")

        o_init = Initialization(parent=self, grand_parent=self.parent)
        o_init.all()

        o_event = EventHandler(parent=self, grand_parent=self.parent)
        o_event.process_data()

        o_init.min_max_values()
        o_init.range_slider()

        self.update_display()

        o_get = Get(parent=self)
        self.previous_parameter_displayed = o_get.parameter_to_display()
        self.update_min_max_values()

    ## menu

    # export table
    def export_table_ascii(self):
        """export table only in ASCII"""
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.table()

    def export_table_json(self):
        """export table only in JSON"""
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.table(file_type=FileType.json)

    # export images
    def export_images_all_tiff(self):
        """export d, strain mapping and integrated in TIFF"""
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.image(
            d_spacing_image=True, strain_mapping_image=True, integrated_image=True
        )

    def export_images_d_tiff(self):
        """export d in TIFF"""
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.image(d_spacing_image=True)

    def export_images_strain_mapping_tiff(self):
        """export strain mapping in TIFF"""
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.image(strain_mapping_image=True)

    def export_images_integrated_tiff(self):
        """export integrated image in TIFF"""
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.image(integrated_image=True)

    # export table and images
    def export_all_ascii_json_tiff(self):
        """export table (ASCII and JSON) and all images as TIFF"""
        o_export = Export(parent=self, grand_parent=self.parent)
        output_folder = o_export.select_output_folder()
        o_export.image(
            d_spacing_image=True,
            strain_mapping_image=True,
            integrated_image=True,
            output_folder=output_folder,
        )
        o_export.table(file_type=FileType.ascii, output_folder=output_folder)
        o_export.table(file_type=FileType.json, output_folder=output_folder)

    def export_all_hdf5(self):
        """export table and images in HDF5"""
        o_export = Export(parent=self, grand_parent=self.parent)
        output_folder = o_export.select_output_folder()
        o_export.hdf5(output_folder=output_folder)

    def fitting_algorithm_changed(self):
        self.update_display()

    def interpolation_cmap_method_changed(self, _):
        self.ui.matplotlib_plot.axes.cla()
        self.ui.matplotlib_plot.draw()
        o_event = EventHandler(parent=self, grand_parent=self.parent)
        o_event.interpolation_cmap_method_changed()

    def parameters_to_display_changed(self):
        self.update_min_max_values()
        self.update_display()

    def d0_to_use_changed(self):
        self.update_display()
        self.update_slider_and_lineEdit()

    def min_max_value_changed(self):
        o_event = EventHandler(parent=self, grand_parent=self.parent)
        o_event.min_max_changed()

    def update_slider_and_lineEdit(self):
        self.update_min_max_values()
        o_get = Get(parent=self)
        parameter_displayed = o_get.parameter_to_display()
        min_value = self.min_max[parameter_displayed]["global_min"]
        max_value = self.min_max[parameter_displayed]["global_max"]
        self.ui.max_range_lineEdit.setText(f"{max_value:.5f}")
        self.ui.min_range_lineEdit.setText(f"{min_value:.5f}")

    def min_max_lineEdit_value_changed(self):
        min_value = float(self.ui.min_range_lineEdit.text())
        max_value = float(self.ui.max_range_lineEdit.text())
        o_get = Get(parent=self)
        parameter_displayed = o_get.parameter_to_display()
        self.min_max[parameter_displayed]["global_min"] = min_value
        self.min_max[parameter_displayed]["global_max"] = max_value

        if self.min_max[parameter_displayed]["min"] < min_value:
            self.min_max[parameter_displayed]["min"] = min_value

        if self.min_max[parameter_displayed]["max"] > max_value:
            self.min_max[parameter_displayed]["max"] = max_value

        self.update_min_max_values()
        self.update_display()

    def update_display(self):
        o_display = Display(parent=self, grand_parent=self.parent)
        o_display.run()

    def calculate_int_value_from_real(self, float_value=0, max_float=0, min_float=0):
        """
        use the real value to return the int value (between 0 and 100) to use in the slider
        Parameters
        ----------
        float_value

        Returns
        -------
        """
        term1 = (float_value - min_float) / (max_float - min_float)
        term2 = int(round(term1 * (self.slider_max - self.slider_min)))
        return term2

    def update_min_max_values(self):
        o_get = Get(parent=self)
        parameter_displayed = o_get.parameter_to_display()

        global_min_value = self.min_max[parameter_displayed]["global_min"]
        global_max_value = self.min_max[parameter_displayed]["global_max"]

        self.ui.range_slider.setRealMin(global_min_value)
        self.ui.range_slider.setRealMax(global_max_value)

        self.ui.max_range_lineEdit.setText(f"{global_max_value:.5f}")
        self.ui.min_range_lineEdit.setText(f"{global_min_value:.5f}")

        self.ui.range_slider.setFocus(True)

    def range_slider_start_value_changed(self, value):
        real_start_value = self.ui.range_slider.get_real_value_from_slider_value(value)
        o_get = Get(parent=self)
        parameters_to_display = o_get.parameter_to_display()
        self.min_max[parameters_to_display]["max"] = real_start_value
        self.min_max_value_changed()

    def range_slider_end_value_changed(self, value):
        real_end_value = self.ui.range_slider.get_real_value_from_slider_value(value)
        o_get = Get(parent=self)
        parameters_to_display = o_get.parameter_to_display()
        self.min_max[parameters_to_display]["min"] = real_end_value
        self.min_max_value_changed()

    def display_hidden_plot_changed(self):
        if self.ui.checkBox.isChecked():
            self.ui.stackedWidget.setCurrentIndex(0)
        else:
            self.ui.stackedWidget.setCurrentIndex(1)
