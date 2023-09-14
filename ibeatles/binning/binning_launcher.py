from qtpy.QtWidgets import QMainWindow, QVBoxLayout, QApplication
from qtpy import QtCore

import pyqtgraph as pg
import numpy as np

from ibeatles.utilities import colors

from ibeatles.fitting.fitting_handler import FittingHandler
from ibeatles.fitting.fitting_launcher import FittingLauncher
from ibeatles.fitting.filling_table_handler import FillingTableHandler
from ibeatles.binning.binning_handler import BinningHandler
from ibeatles import load_ui, BINNING_LINE_COLOR, DataType, DEFAULT_BIN, DEFAULT_ROI
from ibeatles.session import SessionKeys, SessionSubKeys


class BinningLauncher:

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.binning_ui is None:
            binning_window = BinningWindow(parent=parent)
            binning_window.show()
            self.parent.binning_ui = binning_window
            o_binning = BinningHandler(parent=self.parent)
            o_binning.display_image()
        else:
            self.parent.binning_ui.setFocus()
            self.parent.binning_ui.activateWindow()


class BinningWindow(QMainWindow):
    default_bins_settings = {'x0': 0,
                             'y0': 0,
                             'width': 20,
                             'height': 20,
                             'bin_size': 10}

    image_view = None
    line_view = None
    data = []
    widgets_ui = {'x_value': None,
                  'y_value': None,
                  'intensity_value': None,
                  'roi': None}

    def __init__(self, parent=None):

        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_binningWindow.ui', baseinstance=self)
        self.setWindowTitle("4. Binning")

        self.load_data()
        self.init_pyqtgraph()
        self.init_widgets()
        self.roi_selection_widgets_modified()
        self.parent.there_is_a_roi = True
        self.parent.data_metadata[DataType.bin]['ui_accessed'] = True
        self.roi_changed_finished()

    def load_data(self):
        self.data = np.array(self.parent.data_metadata['normalized']['data_live_selection'])

    def init_widgets(self):
        if self.parent.binning_roi:
            [_, x0, y0, width, height, bin_size] = self.parent.binning_roi
            self.ui.selection_x0.setText(str(x0))
            self.ui.selection_y0.setText(str(y0))
            self.ui.selection_width.setText(str(width))
            self.ui.selection_height.setText(str(height))
            self.ui.bin_size_horizontalSlider.setValue(int(bin_size))

    def fitting_steps_clicked(self):
        FittingLauncher(parent=self.parent)

    def bin_slider_value_changed(self, new_value):
        self.roi_selection_widgets_modified()

    def roi_changed_finished(self):
        self.roi_selection_widgets_modified()

    def roi_changed(self):

        if self.parent.binning_line_view['ui']:
            _image_view = self.parent.binning_line_view['image_view']
            _image_view.removeItem(self.parent.binning_line_view['ui'])
            self.parent.binning_line_view['ui'] = None
        else:
            _image_view = self.parent.binning_line_view['image_view']

        roi = self.parent.binning_line_view['roi']
        if len(self.data) == 0:
            return
        region = roi.getArraySlice(self.data, _image_view.imageItem)

        x0 = region[0][0].start
        x1 = region[0][0].stop - 1
        y0 = region[0][1].start
        y1 = region[0][1].stop - 1

        width = np.abs(x0 - x1)
        height = np.abs(y0 - y1)

        self.ui.selection_x0.setText("{}".format(x0))
        self.ui.selection_y0.setText("{}".format(y0))
        self.ui.selection_width.setText("{}".format(width))
        self.ui.selection_height.setText("{}".format(height))

    def init_pyqtgraph(self):

        if len(self.data) == 0:
            status = False
        else:
            status = True

        self.ui.groupBox.setEnabled(status)
        self.ui.groupBox_2.setEnabled(status)
        self.ui.bin_size_horizontalSlider.setEnabled(status)

        pg.setConfigOptions(antialias=True)

        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        self.parent.binning_line_view['image_view'] = image_view

        if self.parent.binning_roi is None:
            [_, x0, y0, width, height, _] = self.parent.list_roi[DataType.normalized][0]
            self.parent.binning_roi = [DEFAULT_ROI[0], x0, y0, width, height, DEFAULT_BIN[-1]]

        binning_roi = self.parent.binning_roi

        x0 = binning_roi[1]
        y0 = binning_roi[2]
        width = binning_roi[3]
        height = binning_roi[4]

        roi = pg.ROI([int(x0), int(y0)],
                     [int(width), int(height)],
                     pen=colors.pen_color['0'],
                     scaleSnap=True)

        roi.addScaleHandle([1, 1], [0, 0])
        roi.sigRegionChanged.connect(self.roi_changed)
        roi.sigRegionChangeFinished.connect(self.roi_changed_finished)
        self.parent.binning_line_view['roi'] = roi
        image_view.addItem(roi)
        line_view = pg.GraphItem()
        image_view.addItem(line_view)
        self.parent.binning_line_view['ui'] = line_view

        # put everything back into the main GUI
        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(image_view)

        self.ui.left_widget.setLayout(vertical_layout)
        self.ui.left_widget.setVisible(status)

    def get_correct_widget_value(self, ui='', variable_name=''):
        s_variable = str(ui.text())
        if s_variable == '':
            s_variable = str(self.default_bins_settings[variable_name])
            ui.setText(s_variable)
        return int(s_variable)

    def roi_selection_widgets_modified(self):

        if len(self.data) == 0:
            return

        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        self.parent.table_dictionary = {}

        if self.parent.binning_line_view['ui']:
            _image_view = self.parent.binning_line_view['image_view']
            _image_view.removeItem(self.parent.binning_line_view['ui'])
            self.parent.binning_line_view['ui'] = None

        x0 = self.get_correct_widget_value(ui=self.ui.selection_x0,
                                           variable_name='x0')
        y0 = self.get_correct_widget_value(ui=self.ui.selection_y0,
                                           variable_name='y0')
        width = self.get_correct_widget_value(ui=self.ui.selection_width,
                                              variable_name='width')
        height = self.get_correct_widget_value(ui=self.ui.selection_height,
                                               variable_name='height')
        bin_size = self.ui.bin_size_horizontalSlider.value()
        self.ui.bin_size_label.setText(str(bin_size))

        # self.parent.binning_bin_size = bin_size
        self.parent.binning_done = True

        self.parent.binning_line_view['roi'].setPos([x0, y0], update=False, finish=False)
        self.parent.binning_line_view['roi'].setSize([width, height], update=False, finish=False)

        pos_adj_dict = self.calculate_matrix_of_pixel_bins(bin_size=bin_size,
                                                           x0=x0,
                                                           y0=y0,
                                                           width=width,
                                                           height=height)

        pos = pos_adj_dict['pos']
        adj = pos_adj_dict['adj']

        line_color = BINNING_LINE_COLOR
        lines = np.array([line_color for n in np.arange(len(pos))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])

        self.parent.binning_line_view['pos'] = pos
        self.parent.binning_line_view['adj'] = adj
        self.parent.binning_line_view['pen'] = lines

        self.update_binning_bins()

        if self.parent.fitting_ui:

            self.parent.fitting_ui.update_selected_bins_plot()
            self.parent.fitting_ui.check_status_widgets()

            o_table = FittingHandler(parent=self.parent.fitting_ui,
                                     grand_parent=self.parent)
            o_table.create_table_dictionary()

            # self.parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)

            o_handler = FittingHandler(parent=self.parent.fitting_ui,
                                       grand_parent=self.parent)
            o_handler.display_roi()
            o_handler.display_locked_active_bins()

            o_fitting = FillingTableHandler(parent=self.parent.fitting_ui,
                                            grand_parent=self.parent)
            o_fitting.fill_table()

        self.record_roi()
        QApplication.restoreOverrideCursor()

    def update_binning_bins(self):
        '''
        this method takes from the parent file the information necessary to display the selection with
        bins in the binning window
        '''

        pos = self.parent.binning_line_view['pos']
        adj = self.parent.binning_line_view['adj']
        lines = self.parent.binning_line_view['pen']

        line_view_binning = pg.GraphItem()
        self.parent.binning_line_view['image_view'].addItem(line_view_binning)
        line_view = line_view_binning
        line_view.setData(pos=pos,
                          adj=adj,
                          pen=lines,
                          symbol=None,
                          pxMode=False)

        self.parent.binning_line_view['ui'] = line_view
        self.record_roi()

    def calculate_matrix_of_pixel_bins(self, bin_size=2,
                                       x0=0,
                                       y0=0,
                                       width=20,
                                       height=20):

        pos_adj_dict = {}

        nbr_height_bins = float(height) / float(bin_size)
        real_height = y0 + int(nbr_height_bins) * int(bin_size)

        nbr_width_bins = float(width) / float(bin_size)
        read_width = x0 + int(nbr_width_bins) * int(bin_size)

        # pos (each matrix is one side of the lines)
        pos = []
        adj = []

        # vertical lines
        x = x0
        index = 0
        while (x <= x0 + width):
            one_edge = [x, y0]
            other_edge = [x, real_height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            x += bin_size
            index += 2

        # horizontal lines
        y = y0
        while (y <= y0 + height):
            one_edge = [x0, y]
            other_edge = [read_width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index + 1])
            y += bin_size
            index += 2

        pos_adj_dict['pos'] = np.array(pos)
        pos_adj_dict['adj'] = np.array(adj)

        return pos_adj_dict

    def closeEvent(self, event=None):
        self.parent.binning_ui = None

        if len(self.data) > 0:
            self.record_roi()

        else:
            # reset everything if we quit with no data plotted
            binning_line_view = {'ui': None,
                                 'pos': None,
                                 'adj': None,
                                 'pen': None,
                                 'image_view': None,
                                 'roi': None}
            self.parent.binning_line_view = binning_line_view

    def record_roi(self):
        x0 = int(str(self.ui.selection_x0.text()))
        y0 = int(str(self.ui.selection_y0.text()))
        width = int(str(self.ui.selection_width.text()))
        height = int(str(self.ui.selection_height.text()))
        bin_size = self.ui.bin_size_horizontalSlider.value()
        self.parent.session_dict[DataType.bin][SessionSubKeys.roi] = [DEFAULT_ROI[0], x0, y0, width, height, bin_size]
        # self.parent.binning_roi = [DEFAULT_ROI[0], x0, y0, width, height, bin_size]

    def ok_button_clicked(self):
        self.close()
