# import sys
# import numpy as np
# import matplotlib.pyplot as plt
# from matplotlib import cm
# import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from qtpy import QtGui
from qtpy.QtWidgets import QSizePolicy


class Qt4MplCanvas(FigureCanvas):

    def __init__(self, parent):
        self.fig = Figure()
        self.ax1 = self.fig.add_subplot(111)
        #        self.fig.tight_layout()

        #        gs = gridspec.GridSpec(1,10)
        #        self.ax1 = self.fig.add_subplot(gs[0:-2])
        #        self.ax2 = self.fig.add_subplot(gs[-1])
        #        self.ax2.get_xaxis().set_visible(False)
        #        self.fig.subplots_adjust(space=.1)

        #        self.fig.tight_layout()

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
