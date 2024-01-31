import numpy as np
from matplotlib.image import _resample
from matplotlib.transforms import Affine2D

from src.ibeatles.step6 import Get
from src.ibeatles.step6 import ParametersToDisplay


class Display:

    histo_widget = None
    image_width = None
    image_height = None

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

        self.image_height = self.parent.image_size['height']
        self.image_width = self.parent.image_size['width']

        o_get = Get(parent=self.parent)
        self.parameters_to_display = o_get.parameter_to_display()

    def run(self):
        o_get = Get(parent=self.parent)
        if o_get.parameter_to_display() == ParametersToDisplay.d:
            self.d_array()
        else:
            self.strain_mapping()
        self.parent.ui.stackedWidget.setCurrentIndex(1)     # 0 for debugging, 1 otherwise
        self.cleanup()

    def cleanup(self):
        self.parent.previous_parameters_displayed = self.parameters_to_display

    def d_array(self):
        """ display of the d 2d image overlapping the sample image """
        d_array = self.parent.compact_d_array
        max_value = np.nanmax(d_array)
        d_array = d_array / max_value

        data_array = d_array
        post_correction_coefficient = max_value
        parameter_to_display = ParametersToDisplay.d

        self.display_array(data_array=data_array,
                           post_correction_coefficient=post_correction_coefficient,
                           parameter_to_display=parameter_to_display)

    def strain_mapping(self):
        """ display of the strain mapping 2D image overlapping the sample image """
        o_get = Get(parent=self.parent)
        strain_mapping = o_get.compact_strain_mapping()

        data_array = strain_mapping
        post_correction_coefficient = 1
        parameter_to_display = ParametersToDisplay.strain_mapping

        self.display_array(data_array=data_array,
                           post_correction_coefficient=post_correction_coefficient,
                           parameter_to_display=parameter_to_display)

    def display_array(self, data_array=None, post_correction_coefficient=1,
                      parameter_to_display=ParametersToDisplay.d):
        o_get = Get(parent=self.parent)
        integrated_image = o_get.integrated_image()
        interpolation_method = o_get.interpolation_method()
        cmap = o_get.cmap()
        scale_factor = self.parent.bin_size
        out_dimensions = (data_array.shape[0] * scale_factor,
                          data_array.shape[1] * scale_factor)
        transform = Affine2D().scale(scale_factor, scale_factor)

        self.parent.ui.matplotlib_interpolation_plot.axes.cla()
        img = self.parent.ui.matplotlib_interpolation_plot.axes.imshow(data_array,
                                                                       cmap=cmap,
                                                                       interpolation=interpolation_method)
        self.parent.ui.matplotlib_interpolation_plot.draw()

        interpolated = _resample(img, data_array, out_dimensions, transform=transform)

        self.parent.ui.matplotlib_interpolation_plot.axes.cla()
        self.parent.ui.matplotlib_interpolation_plot.axes.imshow(interpolated, cmap=cmap)
        self.parent.ui.matplotlib_interpolation_plot.draw()

        interpolated *= post_correction_coefficient

        # with overlap
        interpolated_d_array_2d = np.empty((self.image_height, self.image_width))
        interpolated_d_array_2d[:] = np.nan

        [y0, x0] = self.parent.top_left_corner_of_roi
        inter_height, inter_width = np.shape(interpolated)
        interpolated_d_array_2d[y0: y0 + inter_height, x0: x0 + inter_width] = interpolated

        self.parent.ui.matplotlib_plot.axes.cla()
        self.parent.ui.matplotlib_plot.axes.imshow(integrated_image, cmap='gray', vmin=0, vmax=1)
        self.parent.ui.matplotlib_plot.draw()

        min_value = self.parent.min_max[parameter_to_display]['min']
        max_value = self.parent.min_max[parameter_to_display]['max']

        im = self.parent.ui.matplotlib_plot.axes.imshow(interpolated_d_array_2d,
                                                        interpolation=interpolation_method,
                                                        vmin=min_value,
                                                        vmax=max_value,
                                                        cmap=cmap,
                                                        alpha=0.5)
        if self.parent.colorbar:
            self.parent.colorbar.mappable = im
            self.parent.colorbar.update_normal(im)
            #self.parent.colorbar.remove()
        else:
            self.parent.colorbar = self.parent.ui.matplotlib_plot.fig.colorbar(im,
                                                                           ax=self.parent.ui.matplotlib_plot.axes)

        self.parent.ui.matplotlib_plot.draw()






        #
        #
        # integrated_image = o_get.integrated_image()
        # interpolation_method = o_get.interpolation_method()
        # cmap = o_get.cmap()
        # scale_factor = self.parent.bin_size
        # out_dimensions = (strain_mapping.shape[0] * scale_factor,
        #                   strain_mapping.shape[1] * scale_factor)
        # transform = Affine2D().scale(scale_factor, scale_factor)
        #
        # self.parent.ui.matplotlib_interpolation_plot.axes.cla()
        # img = self.parent.ui.matplotlib_interpolation_plot.axes.imshow(strain_mapping,
        #                                                                cmap=cmap,
        #                                                                interpolation=interpolation_method)
        # self.parent.ui.matplotlib_interpolation_plot.draw()
        #
        # interpolated = _resample(img, strain_mapping, out_dimensions, transform=transform)
        #
        # self.parent.ui.matplotlib_interpolation_plot.axes.cla()
        # self.parent.ui.matplotlib_interpolation_plot.axes.imshow(interpolated, cmap=cmap)
        # self.parent.ui.matplotlib_interpolation_plot.draw()
        #
        # # with overlap
        # interpolated_strain_mapping_2d = np.empty((self.image_height, self.image_width))
        # interpolated_strain_mapping_2d[:] = np.nan
        #
        # [y0, x0] = self.parent.top_left_corner_of_roi
        # inter_height, inter_width = np.shape(interpolated)
        # interpolated_strain_mapping_2d[y0: y0+inter_height, x0: x0+inter_width] = interpolated
        #
        # self.parent.ui.matplotlib_plot.axes.cla()
        # self.parent.ui.matplotlib_plot.axes.imshow(integrated_image, cmap='gray', vmin=0, vmax=1)
        # self.parent.ui.matplotlib_plot.draw()
        #
        # min_value = self.parent.min_max[ParametersToDisplay.strain_mapping]['min']
        # max_value = self.parent.min_max[ParametersToDisplay.strain_mapping]['max']
        #
        # im = self.parent.ui.matplotlib_plot.axes.imshow(interpolated_strain_mapping_2d,
        #                                                 interpolation=interpolation_method,
        #                                                 vmin=min_value,
        #                                                 vmax=max_value,
        #                                                 cmap=cmap,
        #                                                 alpha=0.5)
        #
        # if self.parent.colorbar:
        #     self.parent.colorbar.remove()
        #
        # self.parent.colorbar = self.parent.ui.matplotlib_plot.fig.colorbar(im,
        #                                                                    ax=self.parent.ui.matplotlib_plot.axes)
        # self.parent.ui.matplotlib_plot.draw()
