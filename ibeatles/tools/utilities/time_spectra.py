import glob
import os
from pathlib import Path
from qtpy.QtWidgets import QVBoxLayout, QMainWindow, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ibeatles.utilities.file_handler import FileHandler
from ibeatles.tools.utilities import TimeSpectraKeys
from ibeatles import load_ui

from neutronbraggedge.experiment_handler.tof import TOF
from neutronbraggedge.experiment_handler.experiment import Experiment

TIME_SPECTRA_NAME_FORMAT = '*_Spectra.txt'


class GetTimeSpectraFilename:
    __slots__ = ['parent', 'file_found', 'time_spectra', 'time_spectra_name_format', 'folder']

    def __init__(self, parent=None, folder=None):
        self.parent = parent
        self.file_found = False
        self.time_spectra = ''
        self.time_spectra_name_format = '*_Spectra.txt'
        self.folder = folder

    def retrieve_file_name(self):
        time_spectra = glob.glob(self.folder + '/' + TIME_SPECTRA_NAME_FORMAT)
        if time_spectra and os.path.exists(time_spectra[0]):
            return f"{time_spectra[0]}"

        else:
            return ""


class TimeSpectraHandler:
    tof_array = []
    lambda_array = []
    counts_array = []
    full_file_name = ''

    def __init__(self, parent=None, time_spectra_file_name=None):
        self.tof_array = []
        self.parent = parent

        filename = time_spectra_file_name

        self.short_file_name = Path(filename).name
        self.full_file_name = Path(filename)

    def load(self):
        if self.full_file_name.is_file():

            _tof_handler = TOF(filename=str(self.full_file_name))
            _tof_array_s = _tof_handler.tof_array
            # self.tof_array = _tof_array_s * 1e6
            self.tof_array = _tof_array_s
            self.counts_array = _tof_handler.counts_array

    def calculate_lambda_scale(self):
        distance_source_detector = float(self.parent.ui.distance_source_detector_label.text())
        detector_offset = float(self.parent.ui.detector_offset_label.text())

        _exp = Experiment(tof=self.tof_array,
                          distance_source_detector_m=distance_source_detector,
                          detector_offset_micros=detector_offset)
        self.lambda_array = _exp.lambda_array


class TimeSpectraLauncher:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.time_spectra[TimeSpectraKeys.tof_array] is None:
            return

        short_file_name = os.path.basename(self.parent.time_spectra[TimeSpectraKeys.file_name])
        full_file_name = self.parent.time_spectra[TimeSpectraKeys.file_name]
        x_axis = self.parent.time_spectra[TimeSpectraKeys.tof_array]
        y_axis = self.parent.time_spectra[TimeSpectraKeys.counts_array]
        x2_axis = self.parent.time_spectra[TimeSpectraKeys.lambda_array]

        _time_spectra_window = TimeSpectraDisplay(parent=self.parent,
                                                  short_filename=short_file_name,
                                                  full_filename=full_file_name,
                                                  x_axis=x_axis,
                                                  y_axis=y_axis,
                                                  x2_axis=x2_axis)
        _time_spectra_window.show()


class TimeSpectraDisplay(QMainWindow):

    def __init__(self, parent=None, short_filename='', full_filename='',
                 x_axis=[], y_axis=[], x2_axis=[]):
        self.parent = parent
        self.x_axis = x_axis
        self.x2_axis = x2_axis
        self.y_axis = y_axis
        self.full_filename = full_filename

        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_time_spectra_preview.ui', baseinstance=self)

        self.initialize_view()
        self.setWindowTitle(short_filename)
        self.populate_text()
        self.plot_data()

    def initialize_view(self):
        graphics_view_layout = QVBoxLayout()
        self.ui.time_spectra_view.setLayout(graphics_view_layout)
        self.ui.time_spectra_plot = MatplotlibView(self.parent)
        graphics_view_layout.addWidget(self.ui.time_spectra_plot)

    def populate_text(self):
        _file_contain = FileHandler.retrieve_ascii_contain(self.full_filename)
        self.ui.time_spectra_text.setText(_file_contain)

    def plot_data(self):
        self.ui.time_spectra_plot.ax1.plot(self.x_axis, self.y_axis, '.')

        # if not self.x2_axis == []:
        #     ax2 = self.ui.time_spectra_plot.canvas.ax.twiny()
        #     ax2.plot(self.x2_axis, np.ones(len(self.x2_axis)), '.')
        #     ax2.cla()
        #     ax2.set_xlabel(r"$Lambda  (\AA)$")

        self.ui.time_spectra_plot.ax1.set_xlabel(r"$TOF  (\mu s)$")
        self.ui.time_spectra_plot.ax1.set_ylabel("Counts")
        self.ui.time_spectra_plot.figure.subplots_adjust(top=0.9,
                                                         left=0.1)

        self.ui.time_spectra_plot.draw()


class MatplotlibView(FigureCanvas):

    def __init__(self, parent):
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)