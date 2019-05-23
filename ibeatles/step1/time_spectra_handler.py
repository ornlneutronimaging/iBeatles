import os
import numpy as np
from pathlib import Path
from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QSizePolicy
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from neutronbraggedge.experiment_handler.tof import TOF
from neutronbraggedge.experiment_handler.experiment import Experiment

from ibeatles.utilities.file_handler import FileHandler
import ibeatles.utilities.math_tools as math_tools
from ibeatles.utilities import load_ui


class TimeSpectraHandler(object):
    tof_array = []
    lambda_array = []
    counts_array = []
    full_file_name = ''

    def __init__(self, parent=None, data_type='sample'):
        self.tof_array = []
        self.parent = parent
        self.data_type = data_type

        filename = self.get_time_spectra_filename()

        self.short_file_name = Path(filename).name
        self.full_file_name = Path(filename)

    def get_time_spectra_filename(self):
        return self.parent.data_metadata[self.data_type]['time_spectra']['filename']

    def load(self):
        if self.full_file_name.is_file():
            _tof_handler = TOF(filename=str(self.full_file_name))
            _tof_array_s = _tof_handler.tof_array
            # self.tof_array = _tof_array_s * 1e6
            self.tof_array = _tof_array_s
            self.counts_array = _tof_handler.counts_array

    def calculate_lambda_scale(self):
        distance_source_detector = str(self.parent.ui.distance_source_detector.text())
        detector_offset = str(self.parent.ui.detector_offset.text())

        if (math_tools.is_float(distance_source_detector)) and \
                (math_tools.is_float(detector_offset)):
            distance_source_detector = float(distance_source_detector)
            detector_offset = float(detector_offset)

            _exp = Experiment(tof=self.tof_array,
                              distance_source_detector_m=distance_source_detector,
                              detector_offset_micros=detector_offset)
            self.lambda_array = _exp.lambda_array

        else:
            self.lambda_array = []

    def display(self):
        self.load()
        self.calculate_lambda_scale()
        if not self.tof_array == []:
            _time_spectra_window = TimeSpectraDisplay(parent=self.parent,
                                                      short_filename=str(self.short_file_name),
                                                      full_filename=self.full_file_name,
                                                      x_axis=self.tof_array,
                                                      y_axis=self.counts_array,
                                                      x2_axis=self.lambda_array)
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
        #
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
