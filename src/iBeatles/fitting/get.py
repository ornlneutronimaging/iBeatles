from . import KropffTabSelected
from ..utilities.table_handler import TableHandler


class Get:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def tab_selected(self):
        tab_selected_index = self.parent.ui.kropff_tabWidget.currentIndex()
        if tab_selected_index == 0:
            tab_selected = KropffTabSelected.high_tof
        elif tab_selected_index == 1:
            tab_selected = KropffTabSelected.low_tof
        else:
            tab_selected = KropffTabSelected.bragg_peak
        return tab_selected

    def table_ui_selected(self):
        tab_selected = self.tab_selected()
        if tab_selected == KropffTabSelected.high_tof:
            return self.parent.ui.high_lda_tableWidget
        elif tab_selected == KropffTabSelected.low_tof:
            return self.parent.ui.low_lda_tableWidget
        elif tab_selected == KropffTabSelected.bragg_peak:
            return self.parent.ui.bragg_edge_tableWidget
        else:
            raise ValueError("Tab Selected is invalid!")

    def y_axis_for_given_rows_selected(self):
        table_ui_selected = self.table_ui_selected()
        row_selected = self.row_selected_for_this_table_ui(table_ui=table_ui_selected)
        table_dictionary = self.grand_parent.kropff_table_dictionary
        for _row in row_selected:
            _bin_entry = table_dictionary[str(_row)]
            _bin_x0 = _bin_entry['bin_coordinates']['x0']
            _bin_x1 = _bin_entry['bin_coordinates']['x1']
            _bin_y0 = _bin_entry['bin_coordinates']['y0']
            _bin_y1 = _bin_entry['bin_coordinates']['y1']
            print(f"for _row:{_row} x0:{_bin_x0} x1:{_bin_x1} y0:{_bin_y0} y1:{_bin_y1}")

    def row_selected_for_this_table_ui(self, table_ui=None):
        if table_ui is None:
            return []

        o_table = TableHandler(table_ui=table_ui)
        row_selected = o_table.get_rows_of_table_selected()
        return row_selected
