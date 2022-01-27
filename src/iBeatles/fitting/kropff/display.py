import pyqtgraph as pg

from src.iBeatles.fitting.get import Get


class Display:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def display_bragg_peak_threshold(self):
        # clear all previously display bragg peak threshold
        if not (self.parent.kropff_threshold_current_item is None):
            self.parent.ui.kropff_fitting.removeItem(self.parent.kropff_threshold_current_item)
            self.parent.kropff_threshold_current_item = None

        # get list of row selected
        o_kropff = Get(parent=self.parent)
        row_selected = str(o_kropff.kropff_row_selected()[0])

        kropff_table_dictionary = self.grand_parent.kropff_table_dictionary
        kropff_table_of_row_selected = kropff_table_dictionary[row_selected]
        # retrieve value of threshold range
        left = kropff_table_of_row_selected['bragg peak threshold']['left']
        right = kropff_table_of_row_selected['bragg peak threshold']['right']

        if left is None:
            return

        # display item and make it enabled or not according to is_manual mode or not
        lr = pg.LinearRegionItem(values=[left, right],
                                 orientation='vertical',
                                 brush=None,
                                 movable=True,
                                 bounds=None)
        lr.setZValue(-10)
        lr.sigRegionChangeFinished.connect(self.parent.kropff_bragg_edge_threshold_changed)
        self.parent.ui.kropff_fitting.addItem(lr)
        self.parent.kropff_threshold_current_item = lr
