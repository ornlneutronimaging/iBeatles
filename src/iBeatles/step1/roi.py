import pyqtgraph as pg

from .. import DataType
from ..utilities.colors import pen_color
from .. import RegionType

DEFAULT_ROI = ['default', '0', '0', '20', '20', '0']
DEFAULT_NORMALIZATION_ROI = ['default', '0', '0', '20', '20', RegionType.background]


class Roi:

    def __init__(self, parent=None, data_type=DataType.sample):
        self.parent = parent

    @staticmethod
    def get_roi(roi=DEFAULT_ROI):
        """roi is formatted as DEFAULT_ROI"""
        roi = pg.ROI([roi[1], roi[2]],
                     [roi[3], roi[4]], pen=pen_color['0'], scaleSnap=True)
        roi.addScaleHandle([1, 1], [0, 0])
        return roi

    @staticmethod
    def get_default_roi():
        roi = Roi.get_roi(roi=DEFAULT_ROI)
        return roi

    @staticmethod
    def setup_roi_id(list_roi=[DEFAULT_ROI], roi_function=None):
        list_roi_id = []
        for _roi in list_roi:
            roi_id = Roi.get_roi(roi=_roi)
            roi_id.sigRegionChanged.connect(roi_function)
            list_roi_id.append(roi_id)
        return list_roi_id
