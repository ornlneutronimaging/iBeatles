from qtpy.QtWidgets import QMainWindow, QApplication

import scipy
import shutil
import os
import logging

from src.ibeatles import load_ui, DataType

from src.ibeatles.tools.rotate.event_handler import EventHandler as RotateEventHandler
from src.ibeatles.tools.rotate.rotate_export_launcher import RotateExportLauncher
from src.ibeatles.tools.rotate.initialization import Initialization


class RotateImages:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.rotate_ui is None:
            rotate_ui = RotateImagesWindow(parent=parent)
            rotate_ui.show()
            self.parent.rotate_ui = rotate_ui
        else:
            self.parent.rotate_ui.setFocus()
            self.parent.rotate_ui.activateWindow()


class RotateImagesWindow(QMainWindow):
    grid_size = 100  # pixels

    integrated_image = None
    images_array = None

    histogram_level = None
    first_update = False

    list_tif_files = None
    image_size = {'width': None,
                  'height': None}

    def __init__(self, parent=None):

        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_rotateImages.ui', baseinstance=self)

        o_init = Initialization(parent=self)
        o_init.all()

    def select_folder_clicked(self):
        o_event = RotateEventHandler(parent=self,
                                     top_parent=self.parent)
        o_event.select_input_folder()
        o_event.load_data()
        o_event.display_rotated_images()
        o_event.check_widgets()

    def rotation_value_changed(self, rotation_value):
        o_event = RotateEventHandler(parent=self,
                                     top_parent=self.parent)
        o_event.display_rotated_images()
        o_event.check_widgets()

    def export_button_clicked(self):
        rotate_export_ui = RotateExportLauncher(parent=self,
                                                top_parent=self.parent)
        rotate_export_ui.show()

    # def save_and_use_clicked(self):
    #     logging.info("Rotating normalized images")
    #
    #     # select folder
    #     folder = os.path.dirname(self.parent.data_metadata[DataType.normalized]['folder'])
    #     output_folder = str(QFileDialog.getExistingDirectory(caption='Select Folder for Rotated Images ...',
    #                                                          directory=folder))
    #
    #     if not output_folder:
    #         logging.info(" User cancel rotating the images")
    #         return
    #
    #     QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
    #
    #     # create folder inside this selected folder
    #     rotation_value = self.ui.angle_horizontalSlider.value()
    #     if rotation_value < 0:
    #         rotation_value = f"minus{np.abs(rotation_value)}"
    #
    #     output_folder = os.path.join(output_folder, f"rotated_by_{rotation_value}degrees")
    #     FileHandler.make_or_reset_folder(output_folder)
    #
    #     self.rotate_and_save_all_images(target_folder=output_folder)
    #     self.reload_rotated_images()
    #     self.copy_time_spectra(target_folder=output_folder)
    #     QApplication.restoreOverrideCursor()
    #
    #     self.close()

    def copy_time_spectra(self, target_folder=None):
        time_spectra = self.parent.data_metadata[DataType.normalized]['time_spectra']['filename']
        target_filename = os.path.join(target_folder, os.path.basename(time_spectra))
        if os.path.exists(target_filename):
            os.remove(target_filename)
        self.parent.data_metadata[DataType.normalized]['time_spectra']['filename'] = target_filename
        self.parent.data_metadata[DataType.normalized]['time_spectra']['folder'] = os.path.dirname(target_filename)
        shutil.copyfile(time_spectra, target_filename)
        _folder_time_spectra = os.path.basename(os.path.abspath(target_folder))
        self.parent.ui.time_spectra_folder_2.setText(_folder_time_spectra)

    def reload_rotated_images(self):
        # update plot
        pass

    # def _save_image(self, filename='', data=[]):
    #     if os.path.exists(filename):
    #         os.remove(filename)
    #
    #     file_name, file_extension = os.path.splitext(filename)
    #     if file_extension.lower() in ['.tif', '.tiff']:
    #         FileHandler.make_tiff(data=data, filename=filename)
    #     elif file_extension.lower() == '.fits':
    #         FileHandler.make_fits(data=data, filename=filename)
    #     else:
    #         logging.info(f"file format {file_extension} not supported!")
    #         raise NotImplemented(f"file format {file_extension} not supported!")

    def rotate_and_save_all_images(self, target_folder=''):
        rotation_value = self.ui.angle_horizontalSlider.value()
        logging.info(f" rotation value: {rotation_value}")

        normalized_array = self.parent.data_metadata['normalized']['data']
        self.eventProgress.setValue(0)
        self.eventProgress.setMaximum(len(normalized_array))
        self.eventProgress.setVisible(True)

        rotated_normalized_array = []
        normalized_filename = self.parent.list_files[DataType.normalized]

        basefolder = os.path.basename(os.path.abspath(target_folder))
        self.parent.ui.normalized_folder.setText(basefolder)

        logging.info(f"-> base folder: {basefolder}")
        logging.info(f"-> target folder: {target_folder}")

        list_new_filename = []
        for _index, _data in enumerate(normalized_array):
            # rotate image
            rotated_data = scipy.ndimage.interpolation.rotate(_data, rotation_value)
            rotated_normalized_array.append(rotated_data)

            # save image
            new_filename = os.path.join(target_folder, normalized_filename[_index])
            list_new_filename.append(new_filename)

            self._save_image(filename=new_filename, data=rotated_data)

            self.eventProgress.setValue(_index + 1)
            QApplication.processEvents()

        self.parent.data_metadata['normalized']['data'] = rotated_normalized_array
        self.parent.list_files[DataType.normalized] = list_new_filename
        self.eventProgress.setVisible(False)

        self.parent.normalized_list_selection_changed()

    def cancel_clicked(self):
        self.closeEvent(self)

    def closeEvent(self, event=None):
        self.parent.rotate_ui.close()
        self.parent.rotate_ui = None
