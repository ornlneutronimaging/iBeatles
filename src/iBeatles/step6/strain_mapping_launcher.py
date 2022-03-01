from qtpy.QtWidgets import QMainWindow

from .. import load_ui
from src.iBeatles.step6.initialization import Initialization
from src.iBeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
from src.iBeatles.step6.display import Display
from src.iBeatles.step6.event_handler import EventHandler
from src.iBeatles.step6.get import Get
from src.iBeatles.step6.export import Export
from src.iBeatles.step6 import ParametersToDisplay


class StrainMappingLauncher(object):

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.fitting_ui is None:
            show_status_message(parent=self.parent,
                                message="Strain Mapping requiere to first launch the fitting window!",
                                status=StatusMessageStatus.error,
                                duration_s=10)
        else:
            strain_mapping_window = StrainMappingWindow(parent=parent)
            strain_mapping_window.show()
            self.parent.strain_mapping_ui = strain_mapping_window


class StrainMappingWindow(QMainWindow):

    integrated_image = None
    image_size = {'width': None,
                  'height': None}

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

        self.update_display()

        o_get = Get(parent=self)
        self.previous_parameter_displayed = o_get.parameter_to_display()

    def fitting_algorithm_changed(self):
        self.update_display()

    def parameters_to_display_changed(self):
        self.update_display()

    def d0_to_use_changed(self):
        self.update_display()

    def export_clicked(self):
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.export_image()

    def export_table(self):
        o_export = Export(parent=self, grand_parent=self.parent)
        o_export.export_table()

    def update_display(self):
        o_display = Display(parent=self,
                            grand_parent=self.parent)
        o_display.run()
