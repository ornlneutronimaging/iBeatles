from qtpy.QtWidgets import (QMainWindow, QApplication, QTableWidgetSelectionRange, QVBoxLayout, QHBoxLayout, QWidget,
                            QLabel, QSpacerItem, QSlider, QRadioButton, QSizePolicy)
from qtpy import QtCore
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph as pg
import numpy as np

# from iBeatles.py.utilities.colors import pen_color
from ..utilities.array_utilities import find_nearest_index

from ..fitting.fitting_handler import FittingHandler
from ..fitting.value_table_handler import ValueTableHandler
from ..fitting.selected_bin_handler import SelectedBinsHandler
# from iBeatles.py.table_dictionary.table_dictionary_handler import TableDictionaryHandler
from ..fitting.filling_table_handler import FillingTableHandler
from ..fitting.fitting_initialization_handler import FittingInitializationHandler
from ..fitting.create_fitting_story_launcher import CreateFittingStoryLauncher
from .. import load_ui


class FittingLauncher(object):

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.fitting_ui is None:
            fitting_window = FittingWindow(parent=parent)
            fitting_window.show()
            self.parent.fitting_ui = fitting_window
            o_fitting = FittingHandler(parent=self.parent)
            o_fitting.display_image()
            o_fitting.display_roi()
            o_fitting.fill_table()
            fitting_window.check_advanced_table_status()
        else:
            self.parent.fitting_ui.setFocus()
            self.parent.fitting_ui.activateWindow()


class FittingWindow(QMainWindow):
    data = []
    there_is_a_roi = False
    bragg_edge_active_button_status = True  # to make sure active/lock button worked correctly

    list_bins_selected_item = []
    list_bins_locked_item = []

    image_view = None
    bragg_edge_plot = None
    line_view = None

    line_view_fitting = None  # roi selected in binning window
    all_bins_button = None
    indi_bins_button = None

    header_value_tables_match = {0: [0],
                                 1: [1],
                                 2: [2],
                                 3: [3],
                                 4: [4],
                                 5: [5, 6],
                                 6: [7, 8],
                                 7: [9, 10],
                                 8: [11, 12],
                                 9: [13, 14],
                                 10: [15, 16],
                                 11: [17, 18],
                                 12: [19, 20]}

    para_cell_width = 110
    header_table_columns_width = [30, 30, 50, 50, 100,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width]
    fitting_table_columns_width = [header_table_columns_width[0],
                                   header_table_columns_width[1],
                                   header_table_columns_width[2],
                                   header_table_columns_width[3],
                                   header_table_columns_width[4],
                                   np.int(header_table_columns_width[5] / 2),
                                   np.int(header_table_columns_width[5] / 2),
                                   np.int(header_table_columns_width[6] / 2),
                                   np.int(header_table_columns_width[6] / 2),
                                   np.int(header_table_columns_width[7] / 2),
                                   np.int(header_table_columns_width[7] / 2),
                                   np.int(header_table_columns_width[8] / 2),
                                   np.int(header_table_columns_width[8] / 2),
                                   np.int(header_table_columns_width[9] / 2),
                                   np.int(header_table_columns_width[9] / 2),
                                   np.int(header_table_columns_width[10] / 2),
                                   np.int(header_table_columns_width[10] / 2),
                                   np.int(header_table_columns_width[11] / 2),
                                   np.int(header_table_columns_width[11] / 2),
                                   np.int(header_table_columns_width[12] / 2),
                                   np.int(header_table_columns_width[12] / 2)]

    # status of alpha and sigma initialization
    sigma_alpha_initialized = False
    initialization_table = {'d_spacing': np.NaN,
                            'alpha': np.NaN,
                            'sigma': np.NaN,
                            'a1': np.NaN,
                            'a2': np.NaN,
                            'a5': np.NaN,
                            'a6': np.NaN}

    bragg_edge_data = {'x_axis': [],
                       'y_axis': []}

    def __init__(self, parent=None):

        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        # self.ui = UiMainWindow()
        self.ui = load_ui('ui_fittingWindow.ui', baseinstance=self)
        # self.ui.setupUi(self)
        self.setWindowTitle("5. Fitting")

        self.init_pyqtgraph()
        self.init_labels()
        self.init_widgets()
        self.init_table_behavior()
        self.check_status_widgets()

    def re_fill_table(self):
        o_fitting = FittingHandler(parent=self.parent)
        o_fitting.fill_table()

    def init_table_behavior(self):
        for _column, _width in enumerate(self.header_table_columns_width):
            self.ui.header_table.setColumnWidth(_column, _width)

        for _column, _width in enumerate(self.fitting_table_columns_width):
            self.ui.value_table.setColumnWidth(_column, _width)

        self.hori_header_table = self.ui.header_table.horizontalHeader()
        self.hori_value_table = self.ui.value_table.horizontalHeader()

        self.hori_header_table.sectionResized.connect(self.resizing_header_table)
        self.hori_value_table.sectionResized.connect(self.resizing_value_table)

        self.hori_header_table.sectionClicked.connect(self.column_header_table_clicked)
        self.hori_value_table.sectionClicked.connect(self.column_value_table_clicked)

    def column_value_table_clicked(self, column):
        '''
        to make sure that if the val or err column is selected, or unselected, the other
        column behave the same
        '''
        if column < 5:
            return

        _item0 = self.parent.fitting_ui.ui.value_table.item(0, column)
        state_column_clicked = self.parent.fitting_ui.ui.value_table.isItemSelected(_item0)

        if column % 2 == 0:
            col1 = column - 1
            col2 = column
        else:
            col1 = column
            col2 = column + 1

        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()
        range_selected = QTableWidgetSelectionRange(0, col1, nbr_row - 1, col2)
        self.parent.fitting_ui.ui.value_table.setRangeSelected(range_selected,
                                                               state_column_clicked)

    def column_header_table_clicked(self, column):
        _value_table_column = self.header_value_tables_match.get(column, -1)
        nbr_row = self.parent.fitting_ui.ui.value_table.rowCount()

        # if both col already selected, unselect them
        col_already_selected = False
        _item1 = self.parent.fitting_ui.ui.value_table.item(0, _value_table_column[0])
        _item2 = self.parent.fitting_ui.ui.value_table.item(0, _value_table_column[-1])

        if _item1.isSelected() and _item2.isSelected():

        # if self.parent.fitting_ui.ui.value_table.isItemSelected(_item1) and \
        #         self.parent.fitting_ui.ui.value_table.isItemSelected(_item2):
            col_already_selected = True

        if column in [2, 3]:
            selection = self.parent.fitting_ui.ui.value_table.selectedRanges()
            col_already_selected = False
            for _select in selection:
                if column in [_select.leftColumn(), _select.rightColumn()]:
                    col_already_selected = True
                    break

        from_col = _value_table_column[0]
        to_col = _value_table_column[-1]

        range_selected = QTableWidgetSelectionRange(0, from_col,
                                                    nbr_row - 1, to_col)
        self.parent.fitting_ui.ui.value_table.setRangeSelected(range_selected,
                                                               not col_already_selected)

    def resizing_header_table(self, index_column, old_size, new_size):
        if index_column < 5:
            self.ui.value_table.setColumnWidth(index_column, new_size)
        else:
            new_half_size = np.int(new_size / 2)
            index1 = (index_column - 5) * 2 + 5
            index2 = index1 + 1
            self.ui.value_table.setColumnWidth(index1, new_half_size)
            self.ui.value_table.setColumnWidth(index2, new_half_size)

    def resizing_value_table(self, index_column, old_size, new_size):
        if index_column < 5:
            self.ui.header_table.setColumnWidth(index_column, new_size)
        else:
            if (index_column % 2) == 1:
                right_new_size = self.ui.value_table.columnWidth(index_column + 1)
                index_header = np.int(index_column - 5) / 2 + 5
                self.ui.header_table.setColumnWidth(index_header, new_size + right_new_size)

            else:
                left_new_size = self.ui.value_table.columnWidth(index_column - 1)
                index_header = np.int(index_column - 6) / 2 + 5
                self.ui.header_table.setColumnWidth(index_header, new_size + left_new_size)

    def init_widgets(self):
        '''
        such as material h,k,l list according to material selected in normalized tab
        '''
        hkl_list = self.parent.selected_element_hkl_array
        str_hkl_list = ["{},{},{}".format(_hkl[0], _hkl[1], _hkl[2]) for _hkl in hkl_list]
        self.ui.hkl_list_ui.addItems(str_hkl_list)

    def check_status_widgets(self):
        if (len(self.parent.data_metadata['normalized']['data_live_selection']) > 0) and \
                not (self.parent.binning_line_view['pos'] is None):
            status = True
        else:
            status = False

        self.ui.instructions_step1_button.setEnabled(status)

    def init_labels(self):
        self.ui.lambda_min_label.setText(u"\u03BB<sub>min</sub>")
        self.ui.lambda_max_label.setText(u"\u03BB<sub>max</sub>")
        self.ui.lambda_min_units.setText(u"\u212B")
        self.ui.lambda_max_units.setText(u"\u212B")
        self.ui.bragg_edge_units.setText(u"\u212B")
        self.ui.material_groupBox.setTitle(self.parent.selected_element_name)

    def init_pyqtgraph(self):

        if (len(self.parent.data_metadata['normalized']['data_live_selection']) > 0) and \
                not (self.parent.binning_line_view['pos'] is None):
            status = True
        else:
            status = False

        area = DockArea()
        self.ui.area = area
        area.setVisible(status)
        d1 = Dock("Image Preview", size=(200, 300))
        d2 = Dock("Bragg Edge", size=(200, 100))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')

        preview_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)  # this improve display

        vertical_layout = QVBoxLayout()
        preview_widget.setLayout(vertical_layout)

        # image view (top plot)
        image_view = pg.ImageView()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        self.image_view = image_view
        image_view.scene.sigMouseMoved.connect(self.mouse_moved_in_image_view)

        top_widget = QWidget()
        vertical = QVBoxLayout()
        vertical.addWidget(image_view)

        # bin transparency
        transparency_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        transparency_layout.addItem(spacer)
        label = QLabel("Bin Transparency")
        transparency_layout.addWidget(label)
        slider = QSlider(QtCore.Qt.Horizontal)
        slider.setMaximum(100)
        slider.setMinimum(0)
        slider.setValue(50)
        slider.valueChanged.connect(self.slider_changed)
        self.slider = slider
        transparency_layout.addWidget(slider)
        bottom_widget = QWidget()
        bottom_widget.setLayout(transparency_layout)

        top_widget.setLayout(vertical)
        d1.addWidget(top_widget)
        d1.addWidget(bottom_widget)

        # bragg edge plot (bottom plot)
        bragg_edge_plot = pg.PlotWidget(title='')
        bragg_edge_plot.plot()
        self.bragg_edge_plot = bragg_edge_plot

        # plot all or individual bins
        buttons_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        buttons_layout.addItem(spacer)
        label = QLabel("Plot")
        label.setEnabled(False)
        buttons_layout.addWidget(label)

        # all bins button
        active_button = QRadioButton()
        active_button.setText("Active Bins")
        active_button.setChecked(True)
        # active_button.setEnabled(False)
        active_button.pressed.connect(self.active_button_pressed)
        self.ui.active_bins_button = active_button

        # indi bin button
        buttons_layout.addWidget(active_button)
        locked_button = QRadioButton()
        locked_button.setText("Locked Bins")
        locked_button.setChecked(False)
        # locked_button.setEnabled(False)
        locked_button.pressed.connect(self.lock_button_pressed)
        self.ui.locked_bins_button = locked_button

        buttons_layout.addWidget(locked_button)
        bottom_widget = QWidget()
        bottom_widget.setLayout(buttons_layout)

        d2.addWidget(bragg_edge_plot)
        d2.addWidget(bottom_widget)

        vertical_layout.addWidget(area)
        self.ui.widget.setLayout(vertical_layout)

    def active_button_pressed(self):
        self.bragg_edge_active_button_status = True
        self.update_bragg_edge_plot()

    def lock_button_pressed(self):
        self.bragg_edge_active_button_status = False
        self.update_bragg_edge_plot()

    def mouse_moved_in_image_view(self):
        self.image_view.setFocus(True)

    def hkl_list_changed(self, hkl):
        bragg_edges_array = self.parent.selected_element_bragg_edges_array
        if bragg_edges_array:
            if str(hkl) == '':
                value = "N/A"
            else:
                hkl_array = self.parent.selected_element_hkl_array
                str_hkl_list = ["{},{},{}".format(_hkl[0], _hkl[1], _hkl[2]) for _hkl in hkl_array]
                hkl_bragg_edges = dict(zip(str_hkl_list, bragg_edges_array))
                value = "{:04.3f}".format(hkl_bragg_edges[str(hkl)])
        else:
            value = "N/A"
        self.ui.bragg_edge_calculated.setText(value)

    def slider_changed(self):
        o_fitting_handler = FittingHandler(parent=self.parent)
        o_fitting_handler.display_roi()

    def active_button_state_changed(self, status, row_clicked):
        '''
        status: 0: off
                2: on
        '''
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        update_lock_flag = False
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.ui.selection_table.blockSignals(True)

        if status == 0:
            status = False
        else:
            status = True

        # perform same status on all rows
        _selection = self.ui.value_table.selectedRanges()
        _this_column_is_selected = False
        for _select in _selection:
            if 3 in [_select.leftColumn(), _select.rightColumn()]:
                _this_column_is_selected = True
                break

        table_dictionary = self.parent.table_dictionary
        if _this_column_is_selected:
            # update_selection_flag = True  # we change the state so we need to update the selection
            for _index in table_dictionary:
                table_dictionary[_index]['active'] = status
                _widget_lock = self.ui.value_table.cellWidget(int(_index), 3)
                _widget_lock.blockSignals(True)
                _widget_lock.setChecked(status)
                _widget_lock.blockSignals(False)
                if status:
                    _widget = self.ui.value_table.cellWidget(int(_index), 2)
                    if _widget.isChecked():  # because we can not be active and locked at the same time
                        table_dictionary[_index]['lock'] = False
                        _widget.blockSignals(True)
                        _widget.setChecked(False)
                        _widget.blockSignals(False)
        else:
            table_dictionary[str(row_clicked)]['active'] = status
            if status:
                _widget = self.ui.value_table.cellWidget(row_clicked, 2)
                if _widget.isChecked():
                    table_dictionary[str(row_clicked)]['lock'] = False
                    _widget.blockSignals(True)
                    _widget.setChecked(False)
                    _widget.blockSignals(False)
                    update_lock_flag = True
            self.parent.table_dictionary = table_dictionary

        # hide this row if status is False and user only wants to see locked items
        o_filling_handler = FillingTableHandler(parent=self.parent)
        if (status is False) and (o_filling_handler.get_row_to_show_state() == 'active'):
            self.parent.fitting_ui.ui.value_table.hideRow(row_clicked)

        o_bin_handler = SelectedBinsHandler(parent=self.parent)
        o_bin_handler.update_bins_selected()
        self.update_bragg_edge_plot()
        o_bin_handler.update_bins_locked()

        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.update_selection_table()
            if update_lock_flag:
                self.parent.advanced_selection_ui.update_lock_table()
            self.parent.advanced_selection_ui.ui.selection_table.blockSignals(False)

        QApplication.restoreOverrideCursor()

    def lock_button_state_changed(self, status, row_clicked):
        """
        status: 0: off
                2: on

        we also need to make sure that if the button is lock, it can not be activated !
        """
        update_selection_flag = False

        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.ui.lock_table.blockSignals(True)

        if status == 0:
            status = False
        else:
            status = True

        # perform same status on all rows
        _selection = self.ui.value_table.selectedRanges()
        _this_column_is_selected = False
        for _select in _selection:
            if 2 in [_select.leftColumn(), _select.rightColumn()]:
                _this_column_is_selected = True
                break

        table_dictionary = self.parent.table_dictionary
        if _this_column_is_selected:
            update_selection_flag = True  # we change the state so we need to update the selection
            for _index in table_dictionary:
                table_dictionary[_index]['lock'] = status
                _widget_lock = self.ui.value_table.cellWidget(int(_index), 2)
                _widget_lock.blockSignals(True)
                _widget_lock.setChecked(status)
                _widget_lock.blockSignals(False)
                if status:
                    _widget = self.ui.value_table.cellWidget(int(_index), 3)
                    if _widget.isChecked():  # because we can not be active and locked at the same time
                        table_dictionary[_index]['active'] = False
                        _widget.blockSignals(True)
                        _widget.setChecked(False)
                        _widget.blockSignals(False)
        else:
            table_dictionary[str(row_clicked)]['lock'] = status
            if status:
                _widget = self.ui.value_table.cellWidget(row_clicked, 3)
                if _widget.isChecked():  # because we can not be active and locked at the same time
                    table_dictionary[str(row_clicked)]['active'] = False
                    _widget.blockSignals(True)
                    _widget.setChecked(False)
                    _widget.blockSignals(False)
                    update_selection_flag = True  # we change the state so we need to update the selection

        self.parent.table_dictionary = table_dictionary

        # hide this row if status is False and user only wants to see locked items
        o_filling_handler = FillingTableHandler(parent=self.parent)
        if (status is False) and (o_filling_handler.get_row_to_show_state() == 'lock'):
            self.parent.fitting_ui.ui.value_table.hideRow(row_clicked)

        o_bin_handler = SelectedBinsHandler(parent=self.parent)
        o_bin_handler.update_bins_locked()
        self.update_bragg_edge_plot()
        o_bin_handler.update_bins_selected()

        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.update_lock_table()
            if update_selection_flag:
                self.parent.advanced_selection_ui.update_selection_table()
            self.parent.advanced_selection_ui.ui.lock_table.blockSignals(False)

    def value_table_right_click(self, position):
        o_table_handler = ValueTableHandler(parent=self.parent)
        o_table_handler.right_click(position=position)

    def update_image_view_selection(self):
        o_bin_handler = SelectedBinsHandler(parent=self.parent)
        o_bin_handler.update_bins_selected()

    def update_image_view_lock(self):
        o_bin_handler = SelectedBinsHandler(parent=self.parent)
        o_bin_handler.update_bins_locked()

    def update_bragg_edge_plot(self, update_selection=True):
        o_bin_handler = SelectedBinsHandler(parent=self.parent)
        o_bin_handler.update_bragg_edge_plot()
        if update_selection:
            self.bragg_edge_linear_region_changing()

    def selection_in_value_table_of_rows_cell_clicked(self, row, column):
        # make sure the selection is right (val and err selected at the same time)
        if column > 4:
            _item0 = self.ui.value_table.item(0, column)
            _is_selected = self.ui.value_table.isItemSelected(_item0)
            if (column % 2) == 0:
                left_column = column - 1
                right_column = column
            else:
                left_column = column
                right_column = column + 1
            nbr_row = self.ui.value_table.rowCount()
            _selection = QTableWidgetSelectionRange(0, left_column,
                                                    nbr_row - 1, right_column)
            self.ui.value_table.setRangeSelected(_selection, _is_selected)

        self.update_bragg_edge_plot()

    def selection_in_value_table_changed(self):
        self.selection_in_value_table_of_rows_cell_clicked(-1, -1)

    def bragg_edge_linear_region_changing(self):
        # current xaxis is
        x_axis = self.parent.fitting_bragg_edge_x_axis
        _lr = self.parent.fitting_lr
        if _lr is None:
            return
        selection = list(_lr.getRegion())

        left_index = find_nearest_index(array=x_axis, value=selection[0])
        right_index = find_nearest_index(array=x_axis, value=selection[1])

        # display lambda left and right
        lambda_array = self.parent.data_metadata['time_spectra']['normalized_lambda'] * 1e10
        _lambda_min = lambda_array[left_index]
        _lambda_max = lambda_array[right_index]

        self.ui.lambda_min_lineEdit.setText("{:4.2f}".format(_lambda_min))
        self.ui.lambda_max_lineEdit.setText("{:4.2f}".format(_lambda_max))

    def bragg_edge_linear_region_changed(self):

        # current xaxis is
        x_axis = self.parent.normalized_lambda_bragg_edge_x_axis
        _lr = self.parent.fitting_lr
        if _lr is None:
            return
        selection = list(_lr.getRegion())

        left_index = find_nearest_index(array=x_axis, value=selection[0])
        right_index = find_nearest_index(array=x_axis, value=selection[1])

        list_selected = [left_index, right_index]
        self.parent.fitting_bragg_edge_linear_selection = list_selected

    def check_advanced_table_status(self):
        button_status = self.ui.advanced_table_checkBox.isChecked()
        self.advanced_table_clicked(button_status)

    def advanced_table_clicked(self, status):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        o_table_handler = FillingTableHandler(parent=self.parent)
        o_table_handler.set_mode(advanced_mode=status)
        QApplication.restoreOverrideCursor()

    def update_table(self):
        o_filling_table = FillingTableHandler(parent=self.parent)
        self.parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.parent.fitting_ui.ui.value_table.blockSignals(False)

    def min_or_max_lambda_manually_changed(self):
        min_lambda = float(str(self.ui.lambda_min_lineEdit.text()))
        max_lambda = float(str(self.ui.lambda_max_lineEdit.text()))

        lambda_array = self.parent.data_metadata['time_spectra']['normalized_lambda'] * 1e10

        left_index = find_nearest_index(array=lambda_array, value=min_lambda)
        right_index = find_nearest_index(array=lambda_array, value=max_lambda)

        self.parent.fitting_bragg_edge_linear_selection = [left_index, right_index]

        o_bin_handler = SelectedBinsHandler(parent=self.parent)
        o_bin_handler.update_bragg_edge_plot()

    def initialize_all_parameters_button_clicked(self):
        o_initialization = FittingInitializationHandler(parent=self.parent)
        o_initialization.make_all_active()
        o_initialization.run()

    def initialize_all_parameters_step2(self):
        o_initialization = FittingInitializationHandler(parent=self.parent)
        o_initialization.finished_up_initialization()

        # activate or not step4 (yes if we were able to initialize correctly all variables)
        self.ui.step4_groupBox.setEnabled(o_initialization.all_variables_initialized)

        self.update_bragg_edge_plot()

    def fit_table_active_cell_checked(self):
        pass

    def create_fitting_story_checked(self):
        CreateFittingStoryLauncher(parent=self.parent)

    def closeEvent(self, event=None):
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.close()
        if self.parent.fitting_set_variables_ui:
            self.parent.fitting_set_variables_ui.close()
        self.parent.fitting_ui = None
