import pyqtgraph as pg

from src.iBeatles.utilities.math_tools import is_float


class Display:

    def __init__(self, ui=None):
        self.ui = ui

    def vertical_line(self, x_position=0, item=None):
        if item:
            self.ui.removeItem(item)

        if not is_float(x_position):
            return

        pen = pg.mkPen(color='b', width=2.5)
        new_item = pg.InfiniteLine(pos=x_position,
                                   movable=False,
                                   pen=pen,
                                   label=u"\u03BB0")
        self.ui.addItem(new_item)

        return new_item
