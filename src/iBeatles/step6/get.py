import numpy as np

from src.iBeatles.step6 import ParametersToDisplay


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def active_d0(self):
        if self.parent.ui.d0_value.isChecked():
            return np.float(self.parent.ui.d0_value.text())
        else:
            return np.float(self.parent.ui.d0_user_value.text())

    def parameter_to_display(self):
        if self.parent.ui.display_d_radioButton.isChecked():
            return ParametersToDisplay.d
        elif self.parent.ui.display_strain_mapping_radioButton.isChecked():
            return ParametersToDisplay.strain_mapping
        elif self.parent.ui.display_integrated_image_radioButton.isChecked():
            return ParametersToDisplay.integrated_image
        else:
            raise NotImplementedError("Parameters to display not implemented!")

    def strain_mapping(self):
        d_array = self.parent.d_array
        d0 = self.active_d0()
        strain_mapping = (d_array - d0) / d0
        return strain_mapping

    def d_array(self):
        return self.parent.d_array

    def integrated_image(self):
        return self.parent.integrated_image
