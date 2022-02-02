import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable

from src.iBeatles.step6.get import Get


class Display:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def run(self):
        if self.parent.ui.display_d_radioButton.isChecked():
            self.d_array()
        elif self.parent.ui.display_strain_mapping_radioButton.isChecked():
            self.strain_mapping()
        elif self.parent.ui.display_integrated_image_radioButton.isChecked():
            self.integrated_image()
        else:
            raise NotImplementedError("Display not implemented!")

    def integrated_image(self):
        integrated_image = self.parent.integrated_image
        img = self.parent.strain_mapping_plot.axes.imshow(integrated_image,
                                                          interpolation='nearest',
                                                          vmin=0,
                                                          vmax=1)
        img.set_cmap('viridis')
        self.parent.strain_mapping_plot.axes.axis('off')

        divider = make_axes_locatable(self.parent.strain_mapping_plot.axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.parent.strain_mapping_plot.fig.colorbar(img, cax=cax)

    def d_array(self):
        d_array = self.parent.d_array
        min_value = np.min(d_array)
        max_value = np.max(d_array)
        img = self.parent.strain_mapping_plot.axes.imshow(d_array,
                                                          interpolation='nearest',
                                                          vmin=min_value,
                                                          vmax=max_value)
        img.set_cmap('viridis')
        self.parent.strain_mapping_plot.axes.axis('off')

        divider = make_axes_locatable(self.parent.strain_mapping_plot.axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.parent.strain_mapping_plot.fig.colorbar(img, cax=cax)

    def strain_mapping(self):
        d_array = self.parent.d_array
        o_get = Get(parent=self.parent)
        d0 = o_get.active_d0()
        strain_mapping = (d_array - d0) / d0

        min_value = np.min(strain_mapping)
        max_value = np.max(strain_mapping)
        img = self.parent.strain_mapping_plot.axes.imshow(strain_mapping,
                                                          interpolation='nearest',
                                                          vmin=min_value,
                                                          vmax=max_value)
        img.set_cmap('viridis')
        self.parent.strain_mapping_plot.axes.axis('off')

        divider = make_axes_locatable(self.parent.strain_mapping_plot.axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.parent.strain_mapping_plot.fig.colorbar(img, cax=cax)
