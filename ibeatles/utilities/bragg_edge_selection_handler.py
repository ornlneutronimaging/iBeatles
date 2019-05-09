from qtpy.QtWidgets import QAbstractItemView

from ibeatles.utilities.array_utilities import find_nearest_index


class BraggEdgeSelectionHandler(object):

    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type

    def update_dropdown(self):

        lr = self.parent.list_bragg_edge_selection_id[self.data_type]
        x_axis = self.parent.current_bragg_edge_x_axis[self.data_type]

        selection = list(lr.getRegion())

        left_index = find_nearest_index(array=x_axis, value=selection[0])
        right_index = find_nearest_index(array=x_axis, value=selection[1])

        list_selected = range(left_index, right_index + 1)

        if self.data_type == 'sample':
            _ui_list = self.parent.ui.list_sample
        elif self.data_type == 'ob':
            _ui_list = self.parent.ui.list_open_beam
        else:
            _ui_list = self.parent.ui.list_normalized

        first_item = True

        nbr_item = _ui_list.count()
        for _row in range(nbr_item):
            item = _ui_list.item(_row)
            if _row in list_selected:
                if first_item:
                    first_item = False
                    _ui_list.scrollToItem(item, QtGui.QAbstractItemView.PositionAtTop)
                select_flag = True
            else:
                select_flag = False
            _ui_list.setItemSelected(item, select_flag)
