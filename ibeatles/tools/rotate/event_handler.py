import logging
from qtpy.QtWidgets import QFileDialog
import numpy as np
import scipy
import pyqtgraph as pg

from ibeatles import DataType
from ibeatles.session import SessionSubKeys
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.utilities.load_files import LoadFiles


class EventHandler:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def select_folder(self):
        default_path = self.top_parent.session_dict[DataType.sample][SessionSubKeys.current_folder]
        folder = str(QFileDialog.getExistingDirectory(caption="Select folder containing images to load",
                                                      directory=default_path,
                                                      options=QFileDialog.ShowDirsOnly))
        if folder == "":
            logging.info("User Canceled the selection of folder!")
            return

        logging.info(f"Users selected the folder: {folder}")

        list_tif_files = FileHandler.get_list_of_tif(folder=folder)
        if not list_tif_files:
            logging.info(f"-> folder does not contain any tif file!")

        self.parent.list_tif_files = list_tif_files

    def load_data(self):
        if not self.parent.list_tif_files:
            return

        dict = LoadFiles.load_interactive_data(parent=self.parent,
                                               list_tif_files=self.parent.list_tif_files)
        self.parent.image_size['height'] = dict['height']
        self.parent.image_size['width'] = dict['width']

        self.parent.integrated_image = np.mean(dict['image_array'], axis=0)

    def display_data(self):
        if not self.parent.list_tif_array:
            return

    def display_rotated_images(self):
        if not self.parent.integrated_image:
            return

        data = self.parent.integrated_image
        rotation_value = self.parent.ui.angle_horizontalSlider.value()

        rotated_data = scipy.ndimage.interpolation.rotate(data, rotation_value)
        self.parent.ui.image_view.setImage(rotated_data)

        self.display_grid(data=rotated_data)

    def display_grid(self, data=None):
        [height, width] = np.shape(data)

        pos = []
        adj = []

        # vertical lines
        x = self.parent.grid_size
        index = 0
        while (x <= width):
            one_edge = [x, 0]
            other_edge = [x, height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            x += self.parent.grid_size
            index += 2

        # horizontal lines
        y = self.parent.grid_size
        while (y <= height):
            one_edge = [0, y]
            other_edge = [width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            y += self.parent.grid_size
            index += 2

        pos = np.array(pos)
        adj = np.array(adj)

        line_color = (0, 255, 0, 255, 0.5)
        lines = np.array([line_color for n in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        # remove old line_view
        if self.parent.ui.line_view:
            self.parent.ui.image_view.removeItem(self.ui.line_view)
        line_view = pg.GraphItem()
        self.parent.ui.image_view.addItem(line_view)
        line_view.setData(pos=pos,
                          adj=adj,
                          pen=lines,
                          symbol=None,
                          pxMode=False)
        self.parent.ui.line_view = line_view

    def check_widgets(self):

        # enable the slider if there is something to rotate
        if self.parent.integrated_image:
            enable_group_widgets = True

            # enable the process button if the slider is not at zero and there are data loaded
            if self.parent.ui.angle_horizontalSlider.value == 0:
                enable_button = False
            else:
                enable_button = True

            self.parent.ui.save_and_use_button.setEnabled(enable_button)

        else:
            enable_group_widgets = False

        self.parent.ui.rotation_angle_groupBox.setEnabled(enable_group_widgets)

