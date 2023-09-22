from qtpy.QtWidgets import QMainWindow
from qtpy.QtWidgets import QApplication

from ibeatles import load_ui
from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message

from ibeatles.step6.initialization import Initialization
from ibeatles.step6.display import Display
from ibeatles.step6.event_handler import EventHandler
from ibeatles.step6.get import Get
from ibeatles.step6.export import Export
from ibeatles.step6 import ParametersToDisplay


class StrainMappingLauncher:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.fitting_ui is None:
            show_status_message(parent=self.parent,
                                message="Strain Mapping requires to first launch the fitting window!",
                                status=StatusMessageStatus.error,
                                duration_s=10)
        else:
            strain_mapping_window = StrainMappingWindow(parent=parent)
            strain_mapping_window.show()
            self.parent.strain_mapping_ui = strain_mapping_window


class StrainMappingWindow(QMainWindow):

    # slider_nbr_steps = 1000
    slider_min = 0
    slider_max = 1000

    integrated_image = None
    image_size = {'width': None,
                  'height': None}

    # min_max = {'d': {min: -1,
    #                  max: -1},
    #            'strain_mapping': {min: -1,
    #                               max: -1},
    #            }
    min_max = {ParametersToDisplay.d: None,
               ParametersToDisplay.strain_mapping: None}

    histogram = {'d': None,
                 'strain_mapping': None,
                 'integrated_image': None}

    previous_parameters_displayed = ParametersToDisplay.d

    def __init__(self, parent=None):

        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_strainMapping.ui', baseinstance=self)
        self.setWindowTitle("6. Strain Mapping")

        o_init = Initialization(parent=self, grand_parent=self.parent)
        o_init.all()

        o_event = EventHandler(parent=self, grand_parent=self.parent)
        o_event.calculate_d_array()
        o_init.min_max_values()

        self.update_display()

        o_get = Get(parent=self)
        self.previous_parameter_displayed = o_get.parameter_to_display()
        self.update_min_max_values()

    def fitting_algorithm_changed(self):
        self.update_display()

    def parameters_to_display_changed(self):
        self.update_min_max_values()
        self.update_display()

    def d0_to_use_changed(self):
        self.update_display()

    def export_clicked(self):
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.export_image()

    def export_table(self):
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.export_table()

    def min_max_value_changed(self):
        o_event = EventHandler(parent=self)
        o_event.min_max_changed()

    def update_display(self):
        o_display = Display(parent=self,
                            grand_parent=self.parent)
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
        term1 = (float_value - min_float)/(max_float - min_float)
        term2 = int(round(term1 * (self.slider_max - self.slider_min)))
        return term2

    def update_min_max_values(self):
        o_get = Get(parent=self)
        parameter_displayed = o_get.parameter_to_display()
        if parameter_displayed == ParametersToDisplay.integrated_image:
            return

        min_value = self.min_max[parameter_displayed]['min']
        max_value = self.min_max[parameter_displayed]['max']

        self.ui.max_value_lineEdit.setText(f"{max_value:.8f}")
        self.ui.min_value_lineEdit.setText(f"{min_value:.8f}")

        # global_min_value = self.min_max[parameter_displayed]['global_min']
        # global_max_value = self.min_max[parameter_displayed]['global_max']

        # self.ui.range_slider.setRealMin(global_min_value)
        # self.ui.range_slider.setRealMax(global_max_value)

        self.ui.range_slider.setRealMin(min_value)
        self.ui.range_slider.setRealMax(max_value)

        int_min_value = self.calculate_int_value_from_real(float_value=min_value,
                                                           max_float=max_value,
                                                           min_float=min_value)

        self.ui.range_slider.setMin(int_min_value)


        int_max_value = self.calculate_int_value_from_real(float_value=max_value,
                                                           max_float=max_value,
                                                           min_float=min_value)
        self.ui.range_slider.setMax(int_max_value)

        int_start_value = self.calculate_int_value_from_real(float_value=min_value,
                                                             max_float=max_value,
                                                             min_float=min_value)
        int_end_value = self.calculate_int_value_from_real(float_value=max_value,
                                                           max_float=max_value,
                                                           min_float=min_value)
        # self.ui.range_slider.setRange(start=int_end_value,
        #                               end=int_start_value,
        #                               minimumRange=int_start_value)
        # self.ui.range_slider._setEnd(int_start_value)
        QApplication.processEvents()

    def range_slider_start_value_changed(self, value):
        # print(f"start value changed: {value}")
        pass

    def range_slider_end_value_changed(self, value):
        # print(f"end value changed: {value}")
        pass
