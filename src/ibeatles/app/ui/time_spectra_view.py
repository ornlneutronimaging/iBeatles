from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QSizePolicy, QMessageBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from ibeatles.app.utils.ui_loader import load_ui


class TimeSpectraView(QMainWindow):
    def __init__(self, presenter):
        super().__init__()
        self.presenter = presenter
        self.ui = load_ui("time_spectra_view.ui", baseinstance=self)
        self.initialize_view()

    def initialize_view(self):
        graphics_view_layout = QVBoxLayout()
        self.ui.time_spectra_view.setLayout(graphics_view_layout)
        self.ui.time_spectra_plot = MatplotlibView(self)
        graphics_view_layout.addWidget(self.ui.time_spectra_plot)

    def plot_data(self, x_axis, y_axis, x2_axis):
        self.ui.time_spectra_plot.ax1.clear()
        self.ui.time_spectra_plot.ax1.plot(x_axis, y_axis, ".")
        self.ui.time_spectra_plot.ax1.set_xlabel(r"$TOF  (\mu s)$")
        self.ui.time_spectra_plot.ax1.set_ylabel("Counts")
        self.ui.time_spectra_plot.figure.subplots_adjust(top=0.9, left=0.1)
        self.ui.time_spectra_plot.draw()

    def set_window_title(self, title):
        self.setWindowTitle(title)

    def set_text_content(self, content):
        self.ui.time_spectra_text.setText(content)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)

    def closeEvent(self, event):
        self.presenter.on_view_closed()
        super().closeEvent(event)


class MatplotlibView(FigureCanvas):
    def __init__(self, parent):
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
