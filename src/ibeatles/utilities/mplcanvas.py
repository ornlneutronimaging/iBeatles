import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Qt5Agg")


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.fig = fig
        super(MplCanvas, self).__init__(fig)


class MplCanvasColorbar(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        # fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig, self.axes = plt.subplots()

        # self.axes = fig.add_subplot(111)
        # self.fig = fig
        super(MplCanvasColorbar, self).__init__(self.fig)

        # self.fig = Figure(figsize=(width, height), dpi=dpi)
        #
        # self.axes = plt.subplot2grid((3, 3), (0, 0), colspan=2)
        # self.cax = plt.subplot2grid((3, 3), (0, 1))
        #
        # super(MplCanvasColorbar, self).__init__(self.fig)
