import numpy as np
import pyqtgraph as pg

from ..utilities import colors
from ..fitting.filling_table_handler import FillingTableHandler
from ..table_dictionary.table_dictionary_handler import TableDictionaryHandler
from .selected_bin_handler import SelectedBinsHandler
from ..utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities


class FittingHandler:

    def __init__(self, grand_parent=None, parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def display_image(self, data=[]):
        _state, _view_box = PyqtgraphUtilities.get_state(self.parent.image_view)
        o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                    image_view=self.parent.image_view,
                                    data_type=self.data_type)
        o_pyqt.save_histogram_level()

        if not (data == []):
            self.parent.data = data
            self.parent.image_view.setImage(data)
        else:
            if not self.grand_parent.data_metadata['normalized']['data_live_selection'] == []:
                data = np.array(self.grand_parent.data_metadata['normalized']['data_live_selection'])
                if len(data) == 0:
                    return
                else:
                    self.parent.image_view.setImage(data)
                    self.parent.data = data

        _view_box.setState(_state)
        o_pyqt.reload_histogram_level()

    def display_roi(self):
        if len(np.array(self.grand_parent.data_metadata['normalized']['data_live_selection'])) == 0:
            return

        pos = self.grand_parent.binning_line_view['pos']
        adj = self.grand_parent.binning_line_view['adj']
        lines = self.grand_parent.binning_line_view['pen']

        if pos is None:
            return

        self.grand_parent.there_is_a_roi = True

        # define new transparency of roi
        transparency = self.parent.slider.value()
        self.grand_parent.fitting_transparency_slider_value = transparency
        lines = colors.set_alpha_value(lines=lines, transparency=transparency)

        if self.parent.line_view_fitting:
            self.parent.image_view.removeItem(self.parent.line_view_fitting)

        line_view_fitting = pg.GraphItem()
        self.parent.line_view_fitting = line_view_fitting
        self.parent.image_view.addItem(line_view_fitting)
        self.parent.line_view = line_view_fitting

        self.parent.line_view.setData(pos=pos,
                                      adj=adj,
                                      pen=lines,
                                      symbol=None,
                                      pxMode=False)

    def fill_table(self):

        if len(np.array(self.grand_parent.data_metadata['normalized']['data_live_selection'])) == 0:
            return

        if not self.grand_parent.there_is_a_roi:
            return

        o_table = TableDictionaryHandler(grand_parent=self.grand_parent,
                                         parent=self.parent)
        o_table.create_table_dictionary()

        refresh_image_view = False
        if self.grand_parent.table_loaded_from_session:
            o_table.initialize_parameters_from_session()
            refresh_image_view = True

        o_fill_table = FillingTableHandler(grand_parent=self.grand_parent,
                                           parent=self.parent)
        o_fill_table.fill_table()

        if refresh_image_view:
            o_bin_handler = SelectedBinsHandler(parent=self.parent,
                                                grand_parent=self.grand_parent)
            o_bin_handler.update_bins_locked()
            o_bin_handler.update_bins_selected()
            o_bin_handler.update_bragg_edge_plot()
            self.parent.min_or_max_lambda_manually_changed()
            self.parent.check_status_widgets()
