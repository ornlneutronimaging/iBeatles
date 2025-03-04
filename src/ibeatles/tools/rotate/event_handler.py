import logging
from qtpy.QtWidgets import QFileDialog, QApplication
from qtpy import QtCore
import numpy as np
import scipy
import pyqtgraph as pg
import os
import shutil

from src.ibeatles import DataType, interact_me_style, normal_style
from src.ibeatles.utilities.status_message_config import (
    StatusMessageStatus,
    show_status_message,
)
from src.ibeatles.session import SessionSubKeys
from src.ibeatles.utilities.file_handler import FileHandler
from src.ibeatles.utilities.file_handler import retrieve_timestamp_file_name
from src.ibeatles.utilities.load_files import LoadFiles


class EventHandler:
    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def select_input_folder(self):
        default_path = self.top_parent.session_dict[DataType.sample][
            SessionSubKeys.current_folder
        ]
        folder = str(
            QFileDialog.getExistingDirectory(
                caption="Select folder containing images to load",
                directory=default_path,
                options=QFileDialog.ShowDirsOnly,
            )
        )
        if folder == "":
            logging.info("User Canceled the selection of folder!")
            return

        list_tif_files = FileHandler.get_list_of_tif(folder=folder)
        if not list_tif_files:
            logging.info("-> folder does not contain any tif file!")
            show_status_message(
                parent=self.parent,
                message=f"Folder {os.path.basename(folder)} does not contain any TIFF files!",
                duration_s=5,
                status=StatusMessageStatus.error,
            )
            return

        self.parent.ui.folder_selected_label.setText(folder)
        logging.info(f"Users selected the folder: {folder}")
        self.parent.list_tif_files = list_tif_files

    def load_data(self):
        if not self.parent.list_tif_files:
            return

        dict = LoadFiles.load_interactive_data(
            parent=self.parent, list_tif_files=self.parent.list_tif_files
        )
        self.parent.image_size["height"] = dict["height"]
        self.parent.image_size["width"] = dict["width"]
        self.parent.images_array = dict["image_array"]

        self.parent.integrated_image = np.mean(dict["image_array"], axis=0)

    def display_data(self):
        if not self.parent.list_tif_array:
            return

    def display_rotated_images(self):
        if self.parent.integrated_image is None:
            return

        data = self.parent.integrated_image
        rotation_value = self.parent.ui.rotation_doubleSpinBox.value()

        rotated_data = scipy.ndimage.interpolation.rotate(data, rotation_value)

        _view = self.parent.ui.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()

        histogram_level = self.parent.histogram_level
        if histogram_level is None:
            self.parent.first_update = True
        else:
            self.parent.first_update = False

        histogram_widget = self.parent.ui.image_view.getHistogramWidget()
        self.parent.histogram_level = histogram_widget.getLevels()

        self.parent.ui.image_view.setImage(rotated_data)

        _view_box.setState(_state)
        if not self.parent.first_update:
            histogram_widget.setLevels(
                self.parent.histogram_level[0], self.parent.histogram_level[1]
            )

        self.display_grid(data=rotated_data)

    def display_grid(self, data=None):
        [height, width] = np.shape(data)

        pos = []
        adj = []

        # vertical lines
        x = self.parent.grid_size
        index = 0
        while x <= width:
            one_edge = [x, 0]
            other_edge = [x, height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            x += self.parent.grid_size
            index += 2

        # horizontal lines
        y = self.parent.grid_size
        while y <= height:
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
        lines = np.array(
            [line_color for n in np.arange(len(pos))],
            dtype=[
                ("red", np.ubyte),
                ("green", np.ubyte),
                ("blue", np.ubyte),
                ("alpha", np.ubyte),
                ("width", float),
            ],
        )

        # remove old line_view
        if self.parent.ui.line_view:
            self.parent.ui.image_view.removeItem(self.parent.ui.line_view)
        line_view = pg.GraphItem()
        self.parent.ui.image_view.addItem(line_view)
        line_view.setData(pos=pos, adj=adj, pen=lines, symbol=None, pxMode=False)
        self.parent.ui.line_view = line_view

    def check_widgets(self):
        # enable the slider if there is something to rotate
        if self.parent.integrated_image is not None:
            enable_group_widgets = True

            # enable the process button if the slider is not at zero and there are data loaded
            if float(self.parent.ui.rotation_doubleSpinBox.value()) == 0.0:
                enable_button = False
                self.parent.ui.export_button.setStyleSheet(normal_style)
            else:
                enable_button = True
                self.parent.ui.export_button.setStyleSheet(interact_me_style)

            self.parent.ui.export_button.setEnabled(enable_button)
            self.parent.ui.select_folder_pushButton.setStyleSheet(normal_style)
            self.parent.ui.rotation_doubleSpinBox.setStyleSheet(interact_me_style)

        else:
            enable_group_widgets = False

        self.parent.ui.rotation_angle_groupBox.setEnabled(enable_group_widgets)

    def select_output_folder(self):
        folder = os.path.dirname(self.parent.ui.folder_selected_label.text())
        output_folder = str(
            QFileDialog.getExistingDirectory(
                caption="Select output folder ...", directory=folder
            )
        )

        if not output_folder:
            logging.info(" User cancel rotating the images")
            return

        return output_folder

    def rotate_data(self, output_folder=None):
        if output_folder is None:
            return

        logging.info("Rotating normalized images")
        angle = self.parent.ui.rotation_doubleSpinBox.value()
        data = self.parent.images_array
        import_folder_name = self.parent.ui.folder_selected_label.text()
        list_tiff_files = self.parent.list_tif_files

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        full_output_folder_name = EventHandler._create_full_output_folder_name(
            angle=angle, import_folder=import_folder_name, output_folder=output_folder
        )

        nbr_images = len(data)
        self.parent.eventProgress.setMinimum(0)
        self.parent.eventProgress.setMaximum(nbr_images)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)

        for _index, _data in enumerate(self.parent.images_array):
            rotated_data = scipy.ndimage.interpolation.rotate(_data, angle)

            _input_file = os.path.basename(list_tiff_files[_index])
            new_filename = os.path.join(full_output_folder_name, _input_file)

            EventHandler._save_image(filename=new_filename, data=rotated_data)

            self.parent.eventProgress.setValue(_index + 1)
            QApplication.processEvents()

        # export time stamp data
        EventHandler.export_time_spectra_file(
            output_folder=full_output_folder_name, input_folder=import_folder_name
        )

        self.parent.eventProgress.setVisible(False)
        return full_output_folder_name

    @staticmethod
    def export_time_spectra_file(output_folder=None, input_folder=None):
        """use the time spectra file from the first folder selected and export it to the output folder"""
        logging.info("Export time spectra file:")

        # retrieve full path of the time spectra file from first folder selected
        time_spectra_filename = retrieve_timestamp_file_name(folder=input_folder)

        logging.info(f" - time spectra file: {time_spectra_filename}")
        logging.info(f" - to output folder: {output_folder}")

        # copy that spectra file to final location
        shutil.copy(time_spectra_filename, output_folder)

    @staticmethod
    def _create_full_output_folder_name(
        angle=0.0, import_folder=None, output_folder=None
    ):
        """use the angle value and the folder name of the input data to create the
        output folder name

        ex:
            angle = -1.5
            input_folder = "/users/folder/data/my_input_folder/
            output_folder = "/users/folder/my_output_folder

            output_folder = "/users/folder/my_output_folder/my_input_folder_rotated_by_minus_1_5"
        """
        # define and create output folder file name
        if angle > 0:
            str_rotation_value = f"{angle}"
        else:
            str_rotation_value = f"minus_{np.abs(angle)}"
        str_rotation_value = f"rotated_by_{str_rotation_value}"

        str_rotation_value_parsed = str_rotation_value.split(".")
        new_rotation_value = "_".join(str_rotation_value_parsed)

        input_folder_name = os.path.basename(import_folder)
        full_output_folder_name = os.path.join(
            output_folder, f"{input_folder_name}_{new_rotation_value}"
        )
        FileHandler.make_or_reset_folder(folder_name=full_output_folder_name)
        logging.info(f" Created folder {full_output_folder_name}")
        return full_output_folder_name

    @staticmethod
    def _save_image(filename="", data=None):
        if os.path.exists(filename):
            os.remove(filename)

        file_name, file_extension = os.path.splitext(filename)
        if file_extension.lower() in [".tif", ".tiff"]:
            FileHandler.make_tiff(data=data, filename=filename)
        elif file_extension.lower() == ".fits":
            FileHandler.make_fits(data=data, filename=filename)
        else:
            logging.info(f"file format {file_extension} not supported!")
            raise NotImplementedError(f"file format {file_extension} not supported!")
