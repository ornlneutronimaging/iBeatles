import numpy as np
import pyqtgraph as pg

from .plot import Step2Plot
from .get import Get


class CustomAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        values[values == 0] = np.NaN  # remove 0 before division
        return ['{:.4f}'.format(1. / i) for i in values]


class Step2GuiHandler(object):
    col_width = [70, 50, 50, 50, 50]

    def __init__(self, parent=None):
        self.parent = parent

    def update_widgets(self):
        o_step2_plot = Step2Plot(parent=self.parent)
        o_step2_plot.prepare_data()
        o_step2_plot.display_image()
        o_step2_plot.init_roi_table()
        self.check_run_normalization_button()

    def check_add_remove_roi_buttons(self):
        nbr_row = self.parent.ui.normalization_tableWidget.rowCount()
        if nbr_row == 0:
            _status_remove = False
        else:
            _status_remove = True

        self.parent.ui.normalization_remove_roi_button.setEnabled(_status_remove)

    def check_run_normalization_button(self):
        o_get = Get(parent=self.parent)
        _status = o_get.status_of_run_normalization_button()
        self.parent.ui.normalization_button.setEnabled(_status)

    def enable_xaxis_button(self, tof_flag=True):
        list_ui = [self.parent.step2_ui['xaxis_file_index'],
                   self.parent.step2_ui['xaxis_lambda'],
                   self.parent.step2_ui['xaxis_tof']]

        if tof_flag:
            for _ui in list_ui:
                _ui.setEnabled(True)
        else:
            list_ui[1].setEnabled(False)
            list_ui[2].setEnabled(False)
            list_ui[0].setChecked(True)
