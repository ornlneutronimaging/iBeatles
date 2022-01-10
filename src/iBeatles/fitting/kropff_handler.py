from .get import Get


class KropffHandler:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def update_fitting_plot(self):
        o_get = Get(parent=self.parent)
        tab_selected = o_get.tab_selected()

