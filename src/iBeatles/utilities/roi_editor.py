from qtpy.QtWidgets import QMainWindow, QTableWidgetItem, QComboBox, QTableWidgetSelectionRange, QApplication
import pyqtgraph as pg
from qtpy import QtCore

from ..utilities.gui_handler import GuiHandler
from ..utilities import colors
from ..step1.plot import Step1Plot
from .. import load_ui
from ..step1.roi import DEFAULT_ROI


class RoiEditor(object):

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):

        o_gui = GuiHandler(parent=self.parent)
        active_tab = o_gui.get_active_tab()

        list_roi_editor_ui = self.parent.roi_editor_ui
        _roi_ui = list_roi_editor_ui[active_tab]
        if _roi_ui is None:
            _interface = RoiEditorInterface(parent=self.parent, title=active_tab)
            _interface.show()

            # save ui id
            list_roi_editor_ui[active_tab] = _interface
            self.parent.roi_editor_ui = list_roi_editor_ui

        else:
            _interface = list_roi_editor_ui[active_tab]
            _interface.activateWindow()


class RoiEditorInterface(QMainWindow):
    col_width = [130, 35, 35, 43, 43]

    def __init__(self, parent=None, title='sample'):

        self.parent = parent
        self.title = title

        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_roiEditor.ui', baseinstance=self)
        # self.ui = UiMainWindow()
        # self.ui.setupUi(self)
        self.setWindowTitle("{} ROI Editor".format(title))

        self.initialize_table()
        self.fill_table()

        # QtCore.QObject.connect(self.ui.tableWidget, QtCore.SIGNAL("cellChanged(int, int"), self.cell_changed)

    def initialize_table(self):
        for _index, _width in enumerate(self.col_width):
            self.ui.tableWidget.setColumnWidth(_index, _width)

        nbr_groups = len(colors.roi_group_color)
        self.list_name_groups = ['group {}'.format(index) for index in range(nbr_groups)]

    def get_item(self, text, color):
        _item = QTableWidgetItem(str(text))
        _item.setForeground(color)

        return _item

    def fill_table(self):
        list_roi = self.parent.list_roi[self.title]

        # no ROI already define
        if list_roi == []:
            return

        self.ui.remove_roi_button.setEnabled(True)

        for _row, _roi in enumerate(list_roi):
            [label, x0, y0, width, height, group] = _roi
            self.ui.tableWidget.insertRow(_row)
            # _color = colors.roi_group_color[int(group)]
            self.set_row(_row, label, x0, y0, width, height, int(group))

        # QtCore.QObject.connect(self.ui.tableWidget, QtCore.SIGNAL("cellChanged(int, int)"), self.cell_changed)
        self.ui.tableWidget.cellChanged.connect(self.cell_changed)

    def set_row(self, _row, label, x0, y0, width, height, group):

        _color = colors.roi_group_color[int(group)]

        # label
        _item = self.get_item(label, _color)
        self.ui.tableWidget.setItem(_row, 0, _item)

        # x0
        _item = self.get_item(x0, _color)
        self.ui.tableWidget.setItem(_row, 1, _item)

        # y0
        _item = self.get_item(y0, _color)
        self.ui.tableWidget.setItem(_row, 2, _item)

        # width
        _item = self.get_item(width, _color)
        self.ui.tableWidget.setItem(_row, 3, _item)

        # height
        _item = self.get_item(height, _color)
        self.ui.tableWidget.setItem(_row, 4, _item)

        # group
        _widget = QComboBox()
        _widget.addItems(self.list_name_groups)
        _widget.setCurrentIndex(int(group))
        _widget.currentIndexChanged.connect(self.changed_group)
        self.ui.tableWidget.setCellWidget(_row, 5, _widget)

    def get_row(self, row=0):

        # label
        _item = self.ui.tableWidget.item(row, 0)
        if _item is None:
            raise ValueError
        label = str(_item.text())

        # x0
        _item = self.ui.tableWidget.item(row, 1)
        if _item is None:
            raise ValueError
        x0 = str(_item.text())

        # y0
        _item = self.ui.tableWidget.item(row, 2)
        if _item is None:
            raise ValueError
        y0 = str(_item.text())

        # width
        _item = self.ui.tableWidget.item(row, 3)
        if _item is None:
            raise ValueError
        width = str(_item.text())

        # height
        _item = self.ui.tableWidget.item(row, 4)
        if _item is None:
            raise ValueError
        height = str(_item.text())

        # group
        _group_widget = self.ui.tableWidget.cellWidget(row, 5)
        if _group_widget is None:
            raise ValueError
        _index_selected = _group_widget.currentIndex()
        group = str(_index_selected)

        return [label, x0, y0, width, height, group]

    def changed_group(self, _ignore):
        _nbr_row = self.ui.tableWidget.rowCount()
        for _row in range(_nbr_row):
            _group_widget = self.ui.tableWidget.cellWidget(_row, 5)
            _index_selected = _group_widget.currentIndex()

            _color = colors.roi_group_color[_index_selected]

            _item = self.ui.tableWidget.item(_row, 0)
            _item.setForeground(_color)

            _item = self.ui.tableWidget.item(_row, 1)
            _item.setForeground(_color)

            _item = self.ui.tableWidget.item(_row, 2)
            _item.setForeground(_color)

            _item = self.ui.tableWidget.item(_row, 3)
            _item.setForeground(_color)

            _item = self.ui.tableWidget.item(_row, 4)
            _item.setForeground(_color)

    def closeEvent(self, event=None):
        o_gui = GuiHandler(parent=self.parent)
        active_tab = o_gui.get_active_tab()
        self.parent.roi_editor_ui[active_tab] = None

    def add_roi_button_clicked(self):

        # self.ui.tableWidget.blockSignals(True)

        _row_selected = self.get_row_selected()
        if _row_selected == -1:
            _new_row_index = 0
        else:
            _new_row_index = _row_selected

        self.ui.tableWidget.insertRow(_new_row_index)

        list_roi = self.parent.list_roi[self.title]
        list_roi_id = self.parent.list_roi_id[self.title]
        list_label_roi_id = self.parent.list_label_roi_id[self.title]
        _nbr_row = len(list_roi)

        init_roi = DEFAULT_ROI
        [label, x0, y0, width, height, group] = init_roi
        x0 = int(x0)
        y0 = int(y0)
        width = int(width)
        height = int(height)

        # label roi
        label_roi = pg.TextItem(
            html='<div style="text-align: center"><span style="color: #ff0000;">' + label + '</span></div>',
            anchor=(-0.3, 1.3),
            border='w',
            fill=(0, 0, 255, 50))

        # roi region in image
        roi = pg.ROI([x0, y0], [width, height])
        roi.addScaleHandle([1, 1], [0, 0])
        if self.title == 'sample':
            self.parent.ui.image_view.addItem(roi)
            self.parent.ui.image_view.addItem(label_roi)
            roi.sigRegionChanged.connect(self.parent.roi_image_view_changed)
        elif self.title == 'ob':
            self.parent.ui.ob_image_view.addItem(roi)
            self.parent.ui.ob_image_view.addItem(label_roi)
            roi.sigRegionChanged.connect(self.parent.roi_ob_image_view_changed)
        elif self.title == 'normalized':
            self.parent.ui.normalized_image_view.addItem(roi)
            self.parent.ui.normalized_image_view.addItem(label_roi)
            roi.sigRegionChanged.connect(self.parent.roi_normalized_image_view_changed)

        label_roi.setPos(x0, y0)

        new_list_roi = []
        new_list_roi_id = []
        new_list_label_roi_id = []
        if _nbr_row == 0:
            new_list_roi.append(init_roi)
            new_list_roi_id.append(roi)
            new_list_label_roi_id.append(label_roi)
        else:
            for _index in range(_nbr_row):
                if _index == _new_row_index:
                    new_list_roi.append(init_roi)
                    new_list_roi_id.append(roi)
                    new_list_label_roi_id.append(label_roi)

                new_list_roi.append(list_roi[_index])
                new_list_roi_id.append(list_roi_id[_index])
                new_list_label_roi_id.append(list_label_roi_id[_index])

        self.parent.list_roi[self.title] = new_list_roi
        self.parent.list_roi_id[self.title] = new_list_roi_id
        self.parent.list_label_roi_id[self.title] = new_list_label_roi_id

        # nbr_groups = len(colors.roi_group_color)
        # list_name_groups = ['group {}'.format(index) for index in range(nbr_groups)]

        # _color = colors.roi_group_color[0]
        _row = _new_row_index

        self.set_row(_row, label, x0, y0, width, height, int(group))
        self.ui.remove_roi_button.setEnabled(True)

        # self.ui.tableWidget.blockSignals(False)

    def remove_roi_button_clicked(self):
        _row_selected = self.get_row_selected()
        if _row_selected == -1:
            return

        self.ui.tableWidget.removeRow(_row_selected)

        list_roi = self.parent.list_roi[self.title]
        list_roi_id = self.parent.list_roi_id[self.title]
        list_label_roi_id = self.parent.list_label_roi_id[self.title]

        new_list_roi = []
        new_list_roi_id = []
        new_list_label_roi_id = []
        roi_to_remove = None
        for _index, _array in enumerate(list_roi):
            if _index == _row_selected:
                roi_to_remove = list_roi_id[_index]
                roi_label_to_remove = list_label_roi_id[_index]
                continue
            new_list_roi.append(_array)
            new_list_roi_id.append(list_roi_id[_index])
            new_list_label_roi_id.append(list_label_roi_id[_index])

        if new_list_roi == []:
            self.ui.remove_roi_button.setEnabled(False)

        self.parent.list_roi[self.title] = new_list_roi
        self.parent.list_roi_id[self.title] = new_list_roi_id
        self.parent.list_label_roi_id[self.title] = new_list_label_roi_id

        if self.title == 'sample':
            self.parent.ui.image_view.removeItem(roi_to_remove)
            self.parent.ui.image_view.removeItem(roi_label_to_remove)
        elif self.title == 'ob':
            self.parent.ui.ob_image_view.removeItem(roi_to_remove)
            self.parent.ui.ob_image_view.removeItem(roi_label_to_remove)
        elif self.title == 'normalized':
            self.parent.ui.normalized_image_view.removeItem(roi_to_remove)
            self.parent.ui.normalized_image_view.removeItem(roi_label_to_remove)

        self.cell_changed(0, 0)

    def get_row_selected(self):
        try:
            _row_selected = self.ui.tableWidget.selectedRanges()[0].bottomRow()
        except IndexError:
            _row_selected = -1

        return _row_selected

    def refresh(self, row):
        [label, x0, y0, width, height, group] = self.parent.list_roi[self.title][row]
        self.set_row(row, label, x0, y0, width, height, group)

    def activate_row(self, row):
        if row == -1:
            return

        nbr_column = self.ui.tableWidget.columnCount()
        nbr_row = self.ui.tableWidget.rowCount()
        full_range = QTableWidgetSelectionRange(0, 0, nbr_row, nbr_column - 1)
        self.ui.tableWidget.setRangeSelected(full_range, False)

        range_selected = QTableWidgetSelectionRange(row, 0, row, nbr_column - 1)
        self.ui.tableWidget.setRangeSelected(range_selected, True)
        QApplication.processEvents()

    def roi_editor_table_changed(self, row, column):
        _row = row
        try:
            row_variables = self.get_row(row=_row)
        except ValueError:
            return

        list_roi = self.parent.list_roi[self.title]
        list_roi[_row] = row_variables

        self.parent.list_roi[self.title] = list_roi

    def cell_changed(self, _i, _j):
        o_plot = Step1Plot(parent=self.parent, data_type=self.title)
        o_plot.display_bragg_edge(mouse_selection=False)

    def done_pushButton_clicked(self):
        self.close()
