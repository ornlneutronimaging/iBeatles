import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable


class Display:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

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
        img = self.parent.strain_mapping_plot.axes.imshow(d_array,
                                                          interpolation='nearest',
                                                          vmin=0,
                                                          vmax=1)
        img.set_cmap('viridis')
        self.parent.strain_mapping_plot.axes.axis('off')

        divider = make_axes_locatable(self.parent.strain_mapping_plot.axes)
        cax = divider.append_axes("right", size="5%", pad=0.05)
        self.parent.strain_mapping_plot.fig.colorbar(img, cax=cax)
