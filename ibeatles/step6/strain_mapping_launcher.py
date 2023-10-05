from qtpy.QtWidgets import QMainWindow
from qtpy.QtWidgets import QApplication

from ibeatles import load_ui
from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
from ibeatles.widgets.qrangeslider import FakeKey

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
            strain_mapping_window.ui.range_slider.keyPressEvent(FakeKey(key='down'))
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
    min_max = {ParametersToDisplay.d: {'min': None, 'max': None},
               ParametersToDisplay.strain_mapping: {'min': None, 'max': None}}

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
        o_init.range_slider()

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
        self.update_slider_and_lineEdit()

    def export_clicked(self):
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.export_image()

    def export_table(self):
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.export_table()

    def min_max_value_changed(self):
        o_event = EventHandler(parent=self)
        o_event.min_max_changed()

    def update_slider_and_lineEdit(self):
        self.update_min_max_values()
        o_get = Get(parent=self)
        parameter_displayed = o_get.parameter_to_display()
        min_value = self.min_max[parameter_displayed]['global_min']
        max_value = self.min_max[parameter_displayed]['global_max']
        self.ui.max_range_lineEdit.setText(f"{max_value:.5f}")
        self.ui.min_range_lineEdit.setText(f"{min_value:.5f}")

    def min_max_lineEdit_value_changed(self):
        min_value = float(self.ui.min_range_lineEdit.text())
        max_value = float(self.ui.max_range_lineEdit.text())
        o_get = Get(parent=self)
        parameter_displayed = o_get.parameter_to_display()
        self.min_max[parameter_displayed]['global_min'] = min_value
        self.min_max[parameter_displayed]['global_max'] = max_value

        if self.min_max[parameter_displayed]['min'] < min_value:
            self.min_max[parameter_displayed]['min'] = min_value

        if self.min_max[parameter_displayed]['max'] > max_value:
            self.min_max[parameter_displayed]['max'] = max_value

        self.update_min_max_values()
        self.update_display()

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

        # min_value = self.min_max[parameter_displayed]['min']
        # max_value = self.min_max[parameter_displayed]['max']

        # self.ui.max_value_lineEdit.setText(f"{max_value:.8f}")
        # self.ui.min_value_lineEdit.setText(f"{min_value:.8f}")

        global_min_value = self.min_max[parameter_displayed]['global_min']
        global_max_value = self.min_max[parameter_displayed]['global_max']

        self.ui.range_slider.setRealMin(global_min_value)
        self.ui.range_slider.setRealMax(global_max_value)

        self.ui.max_range_lineEdit.setText(f"{global_max_value:.5f}")
        self.ui.min_range_lineEdit.setText(f"{global_min_value:.5f}")

        # self.ui.range_slider.setRealRange(min_value, max_value)
        # self.ui.range_slider.setRealRange(global_min_value, global_max_value)

        self.ui.range_slider.setFocus(True)
        # my_fake_key = FakeKey(key='down')
        # self.ui.range_slider.keyPressEvent(my_fake_key)

    def range_slider_start_value_changed(self, value):
        real_start_value = self.ui.range_slider.get_real_value_from_slider_value(value)
        o_get = Get(parent=self)
        parameters_to_display = o_get.parameter_to_display()
        self.min_max[parameters_to_display]['max'] = real_start_value
        self.min_max_value_changed()

    def range_slider_end_value_changed(self, value):
        real_end_value = self.ui.range_slider.get_real_value_from_slider_value(value)
        o_get = Get(parent=self)
        parameters_to_display = o_get.parameter_to_display()
        self.min_max[parameters_to_display]['min'] = real_end_value
        self.min_max_value_changed()
