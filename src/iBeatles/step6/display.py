import numpy as np

from src.iBeatles.step6.get import Get
from src.iBeatles.step6 import ParametersToDisplay


class Display:

    histo_widget = None

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        o_get = Get(parent=self.parent)
        self.parameters_to_display = o_get.parameter_to_display()
        self.image_view = self.parent.image_view
        self.view_box = self._get_view_box()
        self.state = self._get_state()
        self.previous_parameters_displayed = self.parent.previous_parameters_displayed
        self._save_histogram()
        self.is_first_histogram = self._is_first_histogram_for_this_parameter()

    def run(self):

        self.image_view.clear()
        if self.parameters_to_display == ParametersToDisplay.d:
            self.d_array()
            self.parent.ui.stackedWidget.setCurrentIndex(1)
        elif self.parameters_to_display == ParametersToDisplay.strain_mapping:
            self.strain_mapping()
            self.parent.ui.stackedWidget.setCurrentIndex(1)
        elif self.parameters_to_display == ParametersToDisplay.integrated_image:
            self.integrated_image()
            self.parent.ui.stackedWidget.setCurrentIndex(0)
        else:
            raise NotImplementedError("Display not implemented!")

        self.cleanup()

    def cleanup(self):
        self.view_box.setState(self.state)
        if not (self.parent.histogram[self.parameters_to_display] is None):
            self.histo_widget.setLevels(self.parent.histogram[self.parameters_to_display][0],
                                        self.parent.histogram[self.parameters_to_display][1])
        self.parent.previous_parameters_displayed = self.parameters_to_display

    def integrated_image(self):
        o_get = Get(parent=self.parent)
        integrated_image = o_get.integrated_image()
        self.image_view.setImage(np.transpose(integrated_image))
        self.parent.previous_parameters_displayed = ParametersToDisplay.integrated_image

    def d_array(self):
        o_get = Get(parent=self.parent)
        d_array = o_get.d_array()

        min_value = self.parent.min_max['d']['min']
        max_value = self.parent.min_max['d']['max']

        self.parent.ui.matplotlib_plot.axes.imshow(d_array, vmin=min_value, vmax=max_value)
        self.parent.ui.matplotlib_plot.draw()

    def strain_mapping(self):
        o_get = Get(parent=self.parent)
        strain_mapping = o_get.strain_mapping()

        min_value = self.parent.min_max['strain_mapping']['min']
        max_value = self.parent.min_max['strain_mapping']['max']

        self.parent.ui.matplotlib_plot.axes.imshow(strain_mapping, vmin=min_value, vmax=max_value)
        self.parent.ui.matplotlib_plot.draw()

    def _get_view_box(self):
        _view = self.image_view.getView()
        _view_box = _view.getViewBox()
        return _view_box

    def _get_state(self):
        return self.view_box.getState()

    def _save_histogram(self):
        self.histo_widget = self.image_view.getHistogramWidget()
        histogram_level = self.histo_widget.getLevels()
        self.parent.histogram[self.previous_parameters_displayed] = histogram_level

    def _is_first_histogram_for_this_parameter(self):
        if self.parent.histogram[self.parameters_to_display] is None:
            return True
        return False
