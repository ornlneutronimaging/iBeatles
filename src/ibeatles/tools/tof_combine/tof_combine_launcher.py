from qtpy.QtWidgets import QMainWindow
import logging
import warnings
from src.ibeatles import load_ui
from src.ibeatles import DataType

from src.ibeatles.utilities.status_message_config import (
    StatusMessageStatus,
    show_status_message,
)

from src.ibeatles.tools.utilities.time_spectra import TimeSpectraLauncher
from src.ibeatles.tools.utilities import TimeSpectraKeys
from src.ibeatles.tools.utilities.reload.reload import Reload

from src.ibeatles.tools.tof_combine import SessionKeys
from src.ibeatles.tools.tof_combine.initialization import Initialization
from src.ibeatles.tools.tof_combine.combine.event_handler import (
    EventHandler as CombineEventHandler,
)
from src.ibeatles.tools.tof_combine.export.export_images import ExportImages
from src.ibeatles.tools.tof_combine.tof_combine_export_launcher import (
    TofCombineExportLauncher,
)

warnings.filterwarnings("ignore")


class TofCombineLauncher:
    def __init__(self, parent=None):
        if parent.binning_ui is None:
            tof_combine_window = TofCombine(parent=parent)
            tof_combine_window.show()
            parent.tof_combining_binning_ui = tof_combine_window

        else:
            parent.binning_ui.setFocus()
            parent.binning_ui.activateWindow()


class TofCombine(QMainWindow):
    output_folder = None

    visualize_flag = False

    # list of folders listed in the combine table
    list_folders = None

    # full path to the top folder selected and used to fill the table
    top_folder = None

    # folder we will use or not
    list_of_folders_status = None

    combine_roi = {"x0": 0, "y0": 0, "width": 200, "height": 200}

    # dictionary that will keep record of the entire UI and used to load and save the session
    session = {
        SessionKeys.list_folders: None,
        SessionKeys.list_folders_status: None,
        SessionKeys.top_folder: None,
        SessionKeys.combine_roi: combine_roi,
    }

    # save info from all the folders
    # {0: {SessionKeys.folder: None,
    #      SessionKeys.data: None,
    #      SessionKeys.list_files: None,
    #      SessionKeys.nbr_files: None,
    #      SessionKeys.use: False,
    #      },
    #  1: ....,
    # }
    dict_data_folders = {}

    combine_image_view = None
    combine_roi_item_id = None

    # time spectra dict
    time_spectra = {
        TimeSpectraKeys.file_name: None,
        TimeSpectraKeys.tof_array: None,
        TimeSpectraKeys.lambda_array: None,
        TimeSpectraKeys.file_index_array: None,
    }

    def __init__(self, parent=None):
        """
        Initialization
        Parameters
        ----------
        """
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui("ui_tof_combine.ui", baseinstance=self)
        self.parent = parent
        self.initialization()
        self.setup()
        self.setWindowTitle("TOF combine tool")

    def initialization(self):
        o_init = Initialization(parent=self)
        o_init.all()

    def setup(self):
        distance_source_detector = self.parent.ui.distance_source_detector.text()
        self.ui.distance_source_detector_label.setText(distance_source_detector)

        detector_offset = self.parent.ui.detector_offset.text()
        self.ui.detector_offset_label.setText(detector_offset)

    # combine events
    def visualize_clicked(self):
        o_event = CombineEventHandler(parent=self)
        o_event.visualize_flag_changed()
        self.radio_buttons_of_folder_changed()

    # def check_combine_widgets(self):
    #     o_event = CombineEventHandler(parent=self)
    #     o_event.check_widgets()

    def select_top_folder_button_clicked(self):
        o_event = CombineEventHandler(parent=self, grand_parent=self.parent)
        o_event.select_top_folder()

    def refresh_table_clicked(self):
        o_event = CombineEventHandler(parent=self)
        o_event.refresh_table_clicked()

    def radio_buttons_of_folder_changed(self):
        o_event = CombineEventHandler(parent=self)
        if self.visualize_flag:
            self.ui.setEnabled(False)
            o_event.update_list_of_folders_to_use()
            o_event.combine_folders()
            o_event.display_profile()
            self.ui.setEnabled(True)
            self.ui.combine_widget.setEnabled(True)
        o_event.check_widgets()

    def time_spectra_preview_clicked(self):
        TimeSpectraLauncher(parent=self)

    def combine_algorithm_changed(self):
        if self.visualize_flag:
            o_event = CombineEventHandler(parent=self)
            o_event.combine_algorithm_changed()
            o_event.display_profile()

    def combine_xaxis_changed(self):
        o_event = CombineEventHandler(parent=self)
        o_event.display_profile()

    def combine_roi_changed(self):
        if self.visualize_flag:
            o_event = CombineEventHandler(parent=self)
            o_event.combine_roi_changed()
            o_event.display_profile()

    def mouse_moved_in_combine_image_preview(self):
        """Mouse moved in the combine pyqtgraph image preview (top right)"""
        pass

    # export images
    def export_combined_and_binned_images_clicked(self):
        pass
        # o_export = ExportImages(parent=self)
        # o_export.run()

    def combine_clicked(self):
        tof_combine_export_ui = TofCombineExportLauncher(
            parent=self, grand_parent=self.parent
        )
        tof_combine_export_ui.show()

    def combine_run(self, data_type_selected=DataType.none):
        self.ui.setEnabled(False)

        show_status_message(
            parent=self,
            message="Combining folders ...",
            status=StatusMessageStatus.working,
        )
        o_event = CombineEventHandler(parent=self)
        o_event.update_list_of_folders_to_use()
        o_event.combine_folders()
        o_export = ExportImages(parent=self, top_parent=self.parent)
        o_export.run()
        output_folder = o_export.output_folder

        show_status_message(
            parent=self,
            message="Combining folders ... Done!",
            status=StatusMessageStatus.ready,
            duration_s=5,
        )
        self.ui.setEnabled(True)
        return output_folder

    def reload_run_in_main_ui(
        self, data_type_selected=DataType.normalized, output_folder=None
    ):
        o_reload = Reload(parent=self, top_parent=self.parent)
        o_reload.run(data_type=data_type_selected, output_folder=output_folder)

    def closeEvent(self, event):
        logging.info(" #### Leaving combine TOF####")
        self.parent.tof_combine_ui = None
        self.close()
