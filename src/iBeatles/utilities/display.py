import pyqtgraph as pg

from iBeatles.utilities.math_tools import is_float, is_nan


class Display:

    def __init__(self, ui=None):
        self.ui = ui

    def vertical_line(self, x_position=0, item=None, label=u"\u03BB\u2080", pen=pg.mkPen(color='b', width=1.5)):

        if item:
            self.ui.removeItem(item)

        if is_nan(x_position):
            return

        if not is_float(x_position):
            return

        new_item = pg.InfiniteLine(pos=x_position,
                                   movable=False,
                                   pen=pen,
                                   labelOpts={'position': 0.9},
                                   label=label)
        self.ui.addItem(new_item)

        return new_item
