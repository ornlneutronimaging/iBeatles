from ibeatles.core.io.data_loading import load_time_spectra


class TimeSpectraModel:
    def __init__(self):
        self.data = {}

    def load_data(
        self,
        file_path: str,
        distance_source_detector_m: float,
        detector_offset_micros: float,
    ):
        self.data = load_time_spectra(
            file_path, distance_source_detector_m, detector_offset_micros
        )

    def get_data(self):
        return self.data
