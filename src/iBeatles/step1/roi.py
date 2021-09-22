import pyqtgraph as pg

from .. import DataType
from ..utilities.colors import pen_color

DEFAULT_ROI = ['default', '0', '0', '20', '20', '0']

class Roi:

    def __init__(self, parent=None, data_type=DataType.sample):
        self.parent = parent

    @staticmethod
    def get_default_roi():
        roi = pg.ROI([DEFAULT_ROI[1], DEFAULT_ROI[2]],
                     [DEFAULT_ROI[3], DEFAULT_ROI[4]], pen=pen_color['0'], scaleSnap=True)
        roi.addScaleHandle([1, 1], [0, 0])
        return roi
