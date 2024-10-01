from ibeatles.app.models.time_spectra_model import TimeSpectraModel
from ibeatles.app.ui.time_spectra_view import TimeSpectraView
from ibeatles.utilities.file_handler import FileHandler


class TimeSpectraPresenter:
    def __init__(self, parent):
        self.parent = parent
        self.model = TimeSpectraModel()
        self.view = TimeSpectraView(self)

    def load_data(
        self,
        file_path: str,
        distance_source_detector_m: float,
        detector_offset_micros: float,
    ):
        try:
            self.model.load_data(
                file_path, distance_source_detector_m, detector_offset_micros
            )
            self.update_view()
        except FileNotFoundError:
            self.view.show_error(
                "File not found", f"The file {file_path} could not be found."
            )
        except Exception as e:
            self.view.show_error("Error loading data", str(e))

    def update_view(self):
        data = self.model.get_data()
        self.view.plot_data(
            data["tof_array"], data["counts_array"], data["lambda_array"]
        )
        self.view.set_window_title(data["short_filename"])
        file_content = FileHandler.retrieve_ascii_contain(data["filename"])
        self.view.set_text_content(file_content)

    def show_view(self):
        self.view.show()

    def on_view_closed(self):
        self.parent.time_spectra_ui = None
