from . import KropffTabSelected


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def tab_selected(self):
        tab_selected_index = self.parent.ui.kropff_tabWidget.currentIndex()
        if tab_selected_index == 0:
            tab_selected = KropffTabSelected.high_tof
        elif tab_selected_index == 1:
            tab_selected = KropffTabSelected.low_tof
        else:
            tab_selected = KropffTabSelected.bragg_peak
        return tab_selected
