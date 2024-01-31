import numpy as np

from src.ibeatles.step6 import ParametersToDisplay


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def active_d0(self):
        if self.parent.ui.d0_value.isChecked():
            return float(self.parent.ui.d0_value.text())
        else:
            return float(self.parent.ui.d0_user_value.text())

    def parameter_to_display(self):
        if self.parent.ui.display_d_radioButton.isChecked():
            return ParametersToDisplay.d
        elif self.parent.ui.display_strain_mapping_radioButton.isChecked():
            return ParametersToDisplay.strain_mapping
        else:
            raise NotImplementedError("Parameters to display not implemented!")

    def strain_mapping(self):
        d_array = self.parent.d_array
        d0 = self.active_d0()
        strain_mapping = (d_array - d0) / d0

        if self.parent.min_max['strain_mapping'] is None:
            self.parent.min_max['strain_mapping'] = {'min': np.nanmin(strain_mapping),
                                                     'max': np.nanmax(strain_mapping)}
            self.parent.min_max['strain_mapping'] = {'global_min': np.nanmin(strain_mapping),
                                                     'global_max': np.nanmax(strain_mapping)}

        return strain_mapping

    def compact_strain_mapping(self):
        d_array = self.parent.compact_d_array
        d0 = self.active_d0()
        strain_mapping = (d_array - d0) / d0

        if self.parent.min_max['strain_mapping'] is None:
            self.parent.min_max['strain_mapping'] = {'min': np.nanmin(strain_mapping),
                                                     'max': np.nanmax(strain_mapping)}
            self.parent.min_max['strain_mapping'] = {'global_min': np.nanmin(strain_mapping),
                                                     'global_max': np.nanmax(strain_mapping)}

        return strain_mapping

    def d_array(self):
        return self.parent.d_array

    def integrated_image(self):
        return self.parent.integrated_image

    def strain_mapping_dictionary(self):
        d_dict = self.parent.d_dict
        strain_mapping_dict = {}
        for _row in d_dict.keys():
            d0 = self.active_d0()
            d = d_dict[_row]['val']
            d_error = d_dict[_row]['err']
            strain_mapping = (d - d0) / d0
            strain_mapping_err = d_error + np.sqrt(d0)

            strain_mapping_dict[_row] = {'val': strain_mapping,
                                         'err': strain_mapping_err}

        return strain_mapping_dict

    def interpolation_method(self):
        return self.parent.ui.interpolation_comboBox.currentText()

    def cmap(self):
        return self.parent.ui.cmap_comboBox.currentText()

    def material_name(self):
        return str(self.parent.ui.material_name.text())

    def hkl_value(self):
        return str(self.parent.ui.hkl_value.text())
