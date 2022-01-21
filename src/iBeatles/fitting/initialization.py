from qtpy.QtWidgets import (QMainWindow, QApplication, QTableWidgetSelectionRange, QVBoxLayout, QHBoxLayout, QWidget,
                            QLabel, QSpacerItem, QSlider, QRadioButton, QSizePolicy)
from qtpy import QtCore
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph as pg
import logging
from qtpy.QtGui import QIcon

from .. import DataType
from ..utilities.table_handler import TableHandler
from .. import settings_icon


class Initialization:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def run_all(self):
        self.pyqtgraph()
        self.table_behavior()
        self.table_headers()
        self.labels()
        self.widgets()
        self.ui()

    def table_headers(self):

        o_kropff_high_tof = TableHandler(table_ui=self.parent.ui.high_lda_tableWidget)
        column_names = [u'row #',
                        u'column #',
                        u'a\u2080',
                        u'b\u2080',
                        u'a\u2080_error',
                        u'b\u2080_error']

        column_sizes = [80, 80, 100, 100, 100, 100]
        for _col_index, _col_name in enumerate(column_names):
            o_kropff_high_tof.insert_column(_col_index)
        o_kropff_high_tof.set_column_names(column_names=column_names)
        o_kropff_high_tof.set_column_sizes(column_sizes=column_sizes)

        o_kropff_low_tof = TableHandler(table_ui=self.parent.ui.low_lda_tableWidget)
        column_names = [u'row #',
                        u'column #',
                        u'a\u2095\u2096\u2097',
                        u'b\u2095\u2096\u2097',
                        u'a\u2095\u2096\u2097_error',
                        u'b\u2095\u2096\u2097_error']
        column_sizes = [80, 80, 100, 100, 100, 100]
        for _col_index, _col_name in enumerate(column_names):
            o_kropff_low_tof.insert_column(_col_index)
        o_kropff_low_tof.set_column_names(column_names=column_names)
        o_kropff_low_tof.set_column_sizes(column_sizes=column_sizes)

        o_kropff_bragg_edge = TableHandler(table_ui=self.parent.ui.bragg_edge_tableWidget)
        column_names = [u'row #',
                        u'column #',
                        u'\u03BB\u2095\u2096\u2097',
                        u'tau',
                        u'sigma',
                        u'\u03BB\u2095\u2096\u2097_error',
                        u'tau_error',
                        u'sigma_error']
        column_sizes = [80, 80, 100, 100, 100, 100, 100, 100]
        for _col_index, _col_name in enumerate(column_names):
            o_kropff_bragg_edge.insert_column(_col_index)
        o_kropff_bragg_edge.set_column_names(column_names=column_names)
        o_kropff_bragg_edge.set_column_sizes(column_sizes=column_sizes)

    def table_behavior(self):
        for _column, _width in enumerate(self.parent.header_table_columns_width):
            self.parent.ui.header_table.setColumnWidth(_column, _width)

        for _column, _width in enumerate(self.parent.fitting_table_columns_width):
            self.parent.ui.value_table.setColumnWidth(_column, _width)

        self.parent.hori_header_table = self.parent.ui.header_table.horizontalHeader()
        self.parent.hori_value_table = self.parent.ui.value_table.horizontalHeader()

        self.parent.hori_header_table.sectionResized.connect(self.parent.resizing_header_table)
        self.parent.hori_value_table.sectionResized.connect(self.parent.resizing_value_table)

        self.parent.hori_header_table.sectionClicked.connect(self.parent.column_header_table_clicked)
        self.parent.hori_value_table.sectionClicked.connect(self.parent.column_value_table_clicked)

    def pyqtgraph(self):

        if (len(self.grand_parent.data_metadata['normalized']['data_live_selection']) > 0) and \
                not (self.grand_parent.binning_line_view['pos'] is None):
            status = True
        else:
            status = False

        area = DockArea()
        self.parent.ui.area = area
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
        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        self.parent.image_view = image_view
        self.grand_parent.fitting_image_view = image_view
        image_view.scene.sigMouseMoved.connect(self.parent.mouse_moved_in_image_view)

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
        slider.valueChanged.connect(self.parent.slider_changed)
        self.parent.slider = slider
        transparency_layout.addWidget(slider)
        bottom_widget = QWidget()
        bottom_widget.setLayout(transparency_layout)

        top_widget.setLayout(vertical)
        d1.addWidget(top_widget)
        d1.addWidget(bottom_widget)

        # bragg edge plot (bottom plot)
        bragg_edge_plot = pg.PlotWidget(title='')
        bragg_edge_plot.plot()
        self.parent.bragg_edge_plot = bragg_edge_plot

        # plot all or individual bins
        buttons_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        buttons_layout.addItem(spacer)
        label = QLabel("Plot")
        buttons_layout.addWidget(label)

        # all bins button
        active_button = QRadioButton()
        active_button.setText("Active Bins")
        active_button.setChecked(True)
        active_button.pressed.connect(self.parent.active_button_pressed)
        self.parent.ui.active_bins_button = active_button

        # individual bin button
        buttons_layout.addWidget(active_button)
        locked_button = QRadioButton()
        locked_button.setText("Locked Bins")
        locked_button.setChecked(False)
        locked_button.pressed.connect(self.parent.lock_button_pressed)
        self.parent.ui.locked_bins_button = locked_button

        buttons_layout.addWidget(locked_button)
        bottom_widget = QWidget()
        bottom_widget.setLayout(buttons_layout)

        d2.addWidget(bragg_edge_plot)
        d2.addWidget(bottom_widget)

        vertical_layout.addWidget(area)
        self.parent.ui.widget.setLayout(vertical_layout)

        # kropff
        self.parent.ui.kropff_fitting = pg.PlotWidget(title="Fitting")
        fitting_layout = QVBoxLayout()
        fitting_layout.addWidget(self.parent.ui.kropff_fitting)
        self.parent.ui.kropff_widget.setLayout(fitting_layout)

    def labels(self):
        self.parent.ui.lambda_min_label.setText(u"\u03BB<sub>min</sub>")
        self.parent.ui.lambda_max_label.setText(u"\u03BB<sub>max</sub>")
        self.parent.ui.lambda_min_units.setText(u"\u212B")
        self.parent.ui.lambda_max_units.setText(u"\u212B")
        self.parent.ui.bragg_edge_units.setText(u"\u212B")
        self.parent.ui.material_groupBox.setTitle(self.grand_parent.selected_element_name)

    def widgets(self):
        """
        such as material h,k,l list according to material selected in normalized tab
        """

        kropff_session_dict = self.grand_parent.session_dict[DataType.fitting]['kropff']

        hkl_list = self.grand_parent.selected_element_hkl_array
        str_hkl_list = ["{},{},{}".format(_hkl[0], _hkl[1], _hkl[2]) for _hkl in hkl_list]
        self.parent.ui.hkl_list_ui.addItems(str_hkl_list)

        # Kropff
        a0 = kropff_session_dict['high tof']['a0']
        b0 = kropff_session_dict['high tof']['b0']
        high_tof_graph = kropff_session_dict['high tof']['graph']

        ahkl = kropff_session_dict['low tof']['ahkl']
        bhkl = kropff_session_dict['low tof']['bhkl']
        low_tof_graph = kropff_session_dict['low tof']['graph']

        lambda_hkl = kropff_session_dict['bragg peak']['lambda_hkl']
        tau = kropff_session_dict['bragg peak']['tau']
        sigma = kropff_session_dict['bragg peak']['sigma']
        bragg_peak_tof_graph = kropff_session_dict['bragg peak']['graph']

        self.parent.ui.kropff_high_lda_a0_init.setText(a0)
        self.parent.ui.kropff_high_lda_b0_init.setText(b0)
        if high_tof_graph == 'a0':
            self.parent.ui.kropff_a0_radioButton.setChecked(True)
        else:
            self.parent.ui.kropff_b0_radioButton.setChecked(True)

        self.parent.ui.kropff_low_lda_ahkl_init.setText(ahkl)
        self.parent.ui.kropff_low_lda_bhkl_init.setText(bhkl)
        if low_tof_graph == 'ahkl':
            self.parent.ui.kropff_ahkl_radioButton.setChecked(True)
        else:
            self.parent.ui.kropff_bhkl_radioButton.setChecked(True)

        self.parent.ui.kropff_bragg_peak_ldahkl_init.setText(lambda_hkl)
        self.parent.ui.kropff_bragg_peak_tau_init.setText(tau)
        index = self.parent.ui.kropff_bragg_peak_sigma_comboBox.findText(sigma)
        self.parent.ui.kropff_bragg_peak_sigma_comboBox.blockSignals(True)
        self.parent.ui.kropff_bragg_peak_sigma_comboBox.setCurrentIndex(index)
        self.parent.ui.kropff_bragg_peak_sigma_comboBox.blockSignals(False)
        if bragg_peak_tof_graph == 'lambda_hkl':
            self.parent.ui.kropff_lda_hkl_radioButton.setChecked(True)
        elif bragg_peak_tof_graph == 'tau':
            self.parent.ui.kropff_tau_radioButton.setChecked(True)
        else:
            self.parent.ui.kropff_sigma_radioButton.setChecked(True)

        if kropff_session_dict['automatic bragg peak threshold finder']:
            self.parent.ui.kropff_automatic_bragg_peak_threshold_finder_checkBox.setChecked(True)
        else:
            self.parent.ui.kropff_automatic_bragg_peak_threshold_finder_checkBox.setChecked(False)

        icon = QIcon(settings_icon)
        self.parent.ui.automatic_bragg_peak_threshold_finder_settings.setIcon(icon)

    def ui(self):
        ui_dict = self.grand_parent.session_dict[DataType.fitting]['ui']

        # splitters
        try:
            splitter_2_size = ui_dict['splitter_2']
            self.parent.ui.splitter_2.setSizes(splitter_2_size)

            splitter_size = ui_dict['splitter']
            self.parent.ui.splitter.setSizes(splitter_size)

            splitter_3_size = ui_dict['splitter_3']
            self.parent.ui.splitter_3.setSizes(splitter_3_size)

        except TypeError:
            logging.info("Splitters have not been set due to log file format error! This should only show up once.")
