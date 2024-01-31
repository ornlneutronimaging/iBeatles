from qtpy.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget, QProgressBar,
                            QLabel, QSpacerItem, QSlider, QSizePolicy,
                            QGroupBox)
import numpy as np
from qtpy import QtCore
import pyqtgraph as pg
import logging
from qtpy.QtGui import QIcon
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from src.ibeatles.icons import icons_rc

from src.ibeatles import DataType, interact_me_style
from src.ibeatles.utilities.table_handler import TableHandler
from src.ibeatles import settings_image
from src.ibeatles.fitting.kropff import KropffThresholdFinder
from src.ibeatles.fitting.kropff import SessionSubKeys as KropffSessionSubKeys
from src.ibeatles.fitting.kropff import BraggPeakInitParameters
from src.ibeatles.fitting import FittingTabSelected, KropffTabSelected
from src.ibeatles.utilities.mplcanvas import MplCanvas
from src.ibeatles.utilities.get import Get


class Initialization:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def run_all(self):
        self.pyqtgraph()
        self.data_format()
        self.table_behavior()
        self.table_headers()
        self.labels()
        self.widgets()
        self.splitter()
        self.ui()
        self.global_data()
        self.statusbar()
        self.matplotlib()
        self.tab()

    def data_format(self):
        # force all the bragg edges array to be float instead of string
        bragg_edges_array = self.grand_parent.selected_element_bragg_edges_array
        self.grand_parent.selected_element_bragg_edges_array = [float(_value) for _value in bragg_edges_array]

    def splitter(self):

        # march dollase vertical splitter
        self.parent.ui.splitter_2.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/vertical_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.splitter_2.setHandleWidth(15)

        # kropff
        self.parent.ui.kropff_top_horizontal_splitter.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/horizontal_splitter_handle.png");
                                     }
                                     """)

        self.parent.ui.splitter.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/horizontal_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.splitter.setHandleWidth(15)

        self.parent.ui.splitter_4.setSizes([500, 500])
        self.parent.ui.splitter_4.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/vertical_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.splitter_4.setHandleWidth(15)

        # self.parent.ui.area.setStyleSheet("""
        #                              QSplitter::handle{
        #                              image: url(":/MPL Toolbar/horizontal_splitter_handle.png");
        #                              }
        #                              """)

        self.parent.ui.splitter_3.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/horizontal_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.splitter_3.setHandleWidth(15)

    def tab(self):
        self.parent.ui.tabWidget.setCurrentIndex(1)   # show by default Kropff
        self.parent.ui.tabWidget.setTabEnabled(0, False)   # disable March-Dollase

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
        self.parent.setStyleSheet("QStatusBar{padding-left:8px;color:red;font-weight:bold;}")

    def global_data(self):
        x_axis = self.grand_parent.normalized_lambda_bragg_edge_x_axis
        self.parent.bragg_edge_data['x_axis'] = x_axis

        # self.parent.kropff_automatic_threshold_finder_algorithm = \
        #     self.grand_parent.kropff_automatic_threshold_finder_algorithm

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
                        u'\u03c4',
                        u'\u03c3',
                        u'\u03BB\u2095\u2096\u2097_error',
                        u'\u03c4_error',
                        u'\u03c3_error']
        column_sizes = [80, 80, 100, 100, 100, 100, 100, 100]
        for _col_index, _col_name in enumerate(column_names):
            o_kropff_bragg_edge.insert_column(_col_index)
        o_kropff_bragg_edge.set_column_names(column_names=column_names)
        o_kropff_bragg_edge.set_column_sizes(column_sizes=column_sizes)

        # kropff table summary
        o_kropff_summary = TableHandler(table_ui=self.parent.ui.kropff_summary_tableWidget)
        for _col in np.arange(3):
            o_kropff_summary.insert_empty_column(column=0)

        kropff_column_names = ['',
                               u'\u03BB\u2095\u2096\u2097',
                               u'\u03BB\u2095\u2096\u2097_error']
        kropff_column_sizes = [400, 200]
        for _col_index, _col_name in enumerate(kropff_column_names):
            o_kropff_summary.insert_column(_col_index)
        o_kropff_summary.set_column_names(kropff_column_names)
        o_kropff_summary.set_column_sizes(kropff_column_sizes)

        kropff_row_names = ['mean', 'median', 'std', '% of cells with a value',
                            '% of cells locked (error within constraints range)']

        for _row_index, _row_name in enumerate(kropff_row_names):
            o_kropff_summary.insert_empty_row(row=_row_index)
            o_kropff_summary.insert_item(row=_row_index, column=0, value=_row_name)

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

        # Kropff

        if (len(self.grand_parent.data_metadata['normalized']['data_live_selection']) > 0) and \
                not (self.grand_parent.binning_line_view['pos'] is None):
            status = True
        else:
            status = False

        # area = DockArea()
        # self.parent.ui.area = area
        # area.setVisible(status)
        # d1 = Dock("Image Preview", size=(200, 300))
        # d2 = Dock("Bragg Edge", size=(200, 100))

        # area.addDock(d1, 'left')
        # area.addDock(d2, 'right')

        preview_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)  # this improves display

        # LEFT WIDGET
        vertical_layout = QVBoxLayout()
        preview_widget.setLayout(vertical_layout)

        # image view (top plot)
        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()

        self.parent.image_view_vline = pg.InfiniteLine(angle=90, movable=False)
        self.parent.image_view_hline = pg.InfiniteLine(angle=0, movable=False)
        image_view.addItem(self.parent.image_view_vline)
        image_view.addItem(self.parent.image_view_hline)

        self.parent.image_view = image_view
        self.parent.image_view_item = image_view.getImageItem()
        self.parent.image_view_scene = self.parent.image_view_item.scene()
        self.parent.image_view_proxy = pg.SignalProxy(self.parent.image_view_scene.sigMouseMoved,
                                                      rateLimit=60,
                                                      slot=self.parent.mouse_moved_in_top_left_image_view)

        self.grand_parent.fitting_image_view = image_view
        image_view.scene.sigMouseMoved.connect(self.parent.mouse_moved_in_image_view)
        self.parent.image_view_scene.sigMouseClicked.connect(self.parent.mouse_clicked_in_top_left_image_view)

        # left_widget = QWidget()
        vertical = QVBoxLayout()
        vertical.addWidget(image_view)

        # cursor infos
        group_xy = QGroupBox()
        group_xy.setFixedHeight(60)
        group_xy.setTitle("Cursor")

        pos_x_label = QLabel("x:")
        pos_x_label.setFixedWidth(50)
        pos_x_label.setAlignment(QtCore.Qt.AlignRight)
        pos_x_value = QLabel("N/A")
        pos_x_value.setFixedWidth(50)
        pos_x_value.setAlignment(QtCore.Qt.AlignLeft)
        self.parent.ui.kropff_pos_x_value = pos_x_value

        pos_y_label = QLabel("y:")
        pos_y_label.setFixedWidth(50)
        pos_y_label.setAlignment(QtCore.Qt.AlignRight)
        pos_y_value = QLabel("N/A")
        pos_y_value.setFixedWidth(50)
        pos_y_value.setAlignment(QtCore.Qt.AlignLeft)
        self.parent.ui.kropff_pos_y_value = pos_y_value

        hori_layout = QHBoxLayout()
        hori_layout.addWidget(pos_x_label)
        hori_layout.addWidget(pos_x_value)
        hori_layout.addWidget(pos_y_label)
        hori_layout.addWidget(pos_y_value)
        group_xy.setLayout(hori_layout)

        # bin infos
        group_bin = QGroupBox()
        group_bin.setFixedHeight(60)
        group_bin.setTitle("Bin")

        bin_x_label = QLabel("x:")
        bin_x_label.setFixedWidth(50)
        bin_x_label.setAlignment(QtCore.Qt.AlignRight)
        bin_x_value = QLabel("N/A")
        bin_x_value.setFixedWidth(50)
        bin_x_value.setAlignment(QtCore.Qt.AlignLeft)
        self.parent.ui.kropff_bin_x_value = bin_x_value

        bin_y_label = QLabel("y:")
        bin_y_label.setFixedWidth(50)
        bin_y_label.setAlignment(QtCore.Qt.AlignRight)
        bin_y_value = QLabel("N/A")
        bin_y_value.setFixedWidth(50)
        bin_y_value.setAlignment(QtCore.Qt.AlignLeft)
        self.parent.ui.kropff_bin_y_value = bin_y_value

        bin_nbr_label = QLabel("#:")
        bin_nbr_label.setFixedWidth(50)
        bin_nbr_label.setAlignment(QtCore.Qt.AlignRight)
        bin_nbr_value = QLabel("N/A")
        bin_nbr_value.setFixedWidth(50)
        bin_nbr_value.setAlignment(QtCore.Qt.AlignLeft)
        self.parent.ui.kropff_bin_nbr_value = bin_nbr_value

        hori_layout = QHBoxLayout()
        hori_layout.addWidget(bin_x_label)
        hori_layout.addWidget(bin_x_value)
        hori_layout.addWidget(bin_y_label)
        hori_layout.addWidget(bin_y_value)
        hori_layout.addWidget(bin_nbr_label)
        hori_layout.addWidget(bin_nbr_value)
        group_bin.setLayout(hori_layout)

        groups_xy_bin = QWidget()
        groups_xh_bin_layout = QHBoxLayout()
        groups_xh_bin_layout.addWidget(group_xy)
        groups_xh_bin_layout.addWidget(group_bin)
        groups_xy_bin.setLayout(groups_xh_bin_layout)

        # bin transparency
        transparency_layout = QHBoxLayout()
        # spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        # transparency_layout.addItem(spacer)
        label = QLabel("Bin Transparency")
        transparency_layout.addWidget(label)
        slider = QSlider(QtCore.Qt.Horizontal)
        slider.setMaximum(100)
        slider.setMinimum(0)
        slider.setValue(50)
        slider.valueChanged.connect(self.parent.slider_changed)
        self.parent.slider = slider
        transparency_layout.addWidget(slider)
        transparency_widget = QWidget()
        transparency_widget.setLayout(transparency_layout)

        vertical.addWidget(groups_xy_bin)
        vertical.addWidget(transparency_widget)

        # bottom_vertical_layout = QVBoxLayout()
        # bottom_vertical_layout.addWidget(groups_xy_bin)
        # bottom_vertical_layout.addWidget(transparency_widget)
        # bottom_widget.setLayout(bottom_vertical_layout)
        # left_widget.setLayout(vertical)

        self.parent.ui.widget_kropff_left.setLayout(vertical)

        # d1.addWidget(top_widget)
        # d1.addWidget(bottom_widget)

        # RIGHT WIDGET
        bragg_edge_plot = pg.PlotWidget(title='')
        bragg_edge_plot.plot()
        self.parent.bragg_edge_plot = bragg_edge_plot

        # plot all or individual bins
        buttons_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        buttons_layout.addItem(spacer)
        label = QLabel("Plot")
        buttons_layout.addWidget(label)
        self.parent.ui.plot_label = label

        # d2.addWidget(bragg_edge_plot)
        right_vertical_layout = QVBoxLayout()
        right_vertical_layout.addWidget(bragg_edge_plot)
        self.parent.ui.widget_kropff_right.setLayout(right_vertical_layout)

        # vertical_layout.addWidget(area)
        # self.parent.ui.widget_kropff.setLayout(vertical_layout)

        # bottom right plot
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
        self.parent.ui.bragg_edge_infos_lambda_0_label.setText(u"\u03BB<sub>0</sub>")

        # material name
        o_get = Get(parent=self.grand_parent)
        material_name = o_get.get_material()
        self.parent.ui.material_groupBox.setTitle(material_name)

    def widgets(self):
        """
        such as material h,k,l list according to material selected in normalized tab
        """
        kropff_session_dict = self.grand_parent.session_dict[DataType.fitting][FittingTabSelected.kropff]

        def _retrieve_kropff_init_value(variable_key: KropffSessionSubKeys = KropffSessionSubKeys.lambda_hkl,
                                        key: BraggPeakInitParameters = BraggPeakInitParameters.fix_flag):
            """
            return the parameter in the kropff_session_dict[bragg_peak][variable_key][key]
            """
            if key is None:
                return ""

            if not kropff_session_dict.get(KropffSessionSubKeys.bragg_peak, None):
                return None

            if not kropff_session_dict[KropffSessionSubKeys.bragg_peak].get(variable_key, None):
                return None

            return kropff_session_dict[KropffSessionSubKeys.bragg_peak][variable_key].get(key, None)

        hkl_list = self.grand_parent.selected_element_hkl_array

        str_hkl_list = ["{},{},{}".format(_hkl[0], _hkl[1], _hkl[2]) for _hkl in hkl_list]
        self.parent.ui.hkl_list_ui.addItems(str_hkl_list)

        # Kropff - initial fitting parameters
        a0 = kropff_session_dict[KropffSessionSubKeys.high_tof][KropffSessionSubKeys.a0]
        b0 = kropff_session_dict[KropffSessionSubKeys.high_tof][KropffSessionSubKeys.b0]
        high_tof_graph = kropff_session_dict[KropffSessionSubKeys.high_tof][KropffSessionSubKeys.graph]
        self.parent.ui.kropff_high_lda_a0_init.setText(a0)
        self.parent.ui.kropff_high_lda_b0_init.setText(b0)
        if high_tof_graph == 'a0':
            self.parent.ui.kropff_a0_radioButton.setChecked(True)
        else:
            self.parent.ui.kropff_b0_radioButton.setChecked(True)

        ahkl = kropff_session_dict[KropffSessionSubKeys.low_tof][KropffSessionSubKeys.ahkl]
        bhkl = kropff_session_dict[KropffSessionSubKeys.low_tof][KropffSessionSubKeys.bhkl]
        low_tof_graph = kropff_session_dict[KropffSessionSubKeys.low_tof][KropffSessionSubKeys.graph]
        self.parent.ui.kropff_low_lda_ahkl_init.setText(ahkl)
        self.parent.ui.kropff_low_lda_bhkl_init.setText(bhkl)
        if low_tof_graph == 'ahkl':
            self.parent.ui.kropff_ahkl_radioButton.setChecked(True)
        else:
            self.parent.ui.kropff_bhkl_radioButton.setChecked(True)

        # lambda hkl
        lambda_hkl_fix_flag = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.lambda_hkl,
                                                          key=BraggPeakInitParameters.fix_flag)
        if lambda_hkl_fix_flag:
            self.parent.ui.lambda_hkl_fix_radioButton.setChecked(True)
        else:
            self.parent.ui.lambda_hkl_range_radioButton.setChecked(True)

        self.parent.kropff_initial_guess_lambda_hkl_fix_clicked()

        lambda_hkl_fix_value =_retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.lambda_hkl,
                                                          key=BraggPeakInitParameters.fix_value)
        self.parent.ui.lambda_hkl_fix_lineEdit.setText(str(lambda_hkl_fix_value))

        lambda_hkl_range_from = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.lambda_hkl,
                                                            key=BraggPeakInitParameters.range_from)
        self.parent.ui.lambda_hkl_from_lineEdit.setText(str(lambda_hkl_range_from))

        lambda_hkl_range_to = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.lambda_hkl,
                                                            key=BraggPeakInitParameters.range_to)
        self.parent.ui.lambda_hkl_to_lineEdit.setText(str(lambda_hkl_range_to))

        lambda_hkl_range_step = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.lambda_hkl,
                                                            key=BraggPeakInitParameters.range_step)
        self.parent.ui.lambda_hkl_step_lineEdit.setText(str(lambda_hkl_range_step))

        # tau
        tau_fix_flag = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.tau,
                                                   key=BraggPeakInitParameters.fix_flag)
        if tau_fix_flag:
            self.parent.ui.tau_fix_radioButton.setChecked(True)
        else:
            self.parent.ui.tau_range_radioButton.setChecked(True)
        self.parent.kropff_initial_guess_tau_fix_clicked()

        tau_fix_value = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.tau,
                                                           key=BraggPeakInitParameters.fix_value)
        self.parent.ui.tau_fix_lineEdit.setText(str(tau_fix_value))

        tau_range_from = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.tau,
                                                            key=BraggPeakInitParameters.range_from)
        self.parent.ui.tau_from_lineEdit.setText(str(tau_range_from))

        tau_range_to = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.tau,
                                                          key=BraggPeakInitParameters.range_to)
        self.parent.ui.tau_to_lineEdit.setText(str(tau_range_to))

        tau_range_step = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.tau,
                                                            key=BraggPeakInitParameters.range_step)
        self.parent.ui.tau_step_lineEdit.setText(str(tau_range_step))

        # sigma
        sigma_fix_flag = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.sigma,
                                                          key=BraggPeakInitParameters.fix_flag)
        if sigma_fix_flag:
            self.parent.ui.sigma_fix_radioButton.setChecked(True)
        else:
            self.parent.ui.sigma_range_radioButton.setChecked(True)
        self.parent.kropff_initial_guess_sigma_fix_clicked()

        sigma_fix_value = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.sigma,
                                                           key=BraggPeakInitParameters.fix_value)
        self.parent.ui.sigma_fix_lineEdit.setText(str(sigma_fix_value))

        sigma_range_from = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.sigma,
                                                            key=BraggPeakInitParameters.range_from)
        self.parent.ui.sigma_from_lineEdit.setText(str(sigma_range_from))

        sigma_range_to = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.sigma,
                                                          key=BraggPeakInitParameters.range_to)
        self.parent.ui.sigma_to_lineEdit.setText(str(sigma_range_to))

        sigma_range_step = _retrieve_kropff_init_value(variable_key=KropffSessionSubKeys.sigma,
                                                            key=BraggPeakInitParameters.range_step)
        self.parent.ui.sigma_step_lineEdit.setText(str(sigma_range_step))

        # lambda_hkl = kropff_session_dict[KropffSessionSubKeys.bragg_peak]['lambda_hkl']
        # tau = kropff_session_dict['bragg peak']['tau']
        # sigma = kropff_session_dict['bragg peak']['sigma']
        bragg_peak_tof_graph = kropff_session_dict[KropffTabSelected.bragg_peak]['graph']

        # self.parent.ui.kropff_bragg_peak_tau_init.setText(tau)
        # index = self.parent.ui.kropff_bragg_peak_sigma_comboBox.findText(sigma)
        # self.parent.ui.kropff_bragg_peak_sigma_comboBox.blockSignals(True)
        # self.parent.ui.kropff_bragg_peak_sigma_comboBox.setCurrentIndex(index)
        # self.parent.ui.kropff_bragg_peak_sigma_comboBox.blockSignals(False)
        if bragg_peak_tof_graph == KropffSessionSubKeys.lambda_hkl:
            self.parent.ui.kropff_lda_hkl_radioButton.setChecked(True)
        elif bragg_peak_tof_graph == KropffSessionSubKeys.tau:
            self.parent.ui.kropff_tau_radioButton.setChecked(True)
        else:
            self.parent.ui.kropff_sigma_radioButton.setChecked(True)

        self.parent.kropff_automatic_threshold_finder_algorithm = \
            kropff_session_dict.get(KropffSessionSubKeys.automatic_bragg_peak_threshold_algorithm,
                                    KropffThresholdFinder.sliding_average)

        icon = QIcon(settings_image)
        self.parent.ui.automatic_bragg_peak_threshold_finder_settings.setIcon(icon)

        self.parent.ui.kropff_fitting_conditions_pushButton.setIcon(icon)
        self.parent.ui.kropff_fitting_conditions_pushButton_1.setIcon(icon)

        self.parent.ui.automatic_bragg_peak_threshold_finder_pushButton.setStyleSheet(interact_me_style)
        self.parent.ui.automatic_kropff_fitting_pushButton.setStyleSheet(interact_me_style)

        self.parent.ui.fitting_kropff_bragg_peak_lambda_hkl_groupBox.setTitle(u"\u03BB\u2095\u2096\u2097")
        self.parent.ui.fitting_kropff_bragg_peak_tau_groupBox.setTitle(u"\u03c4")
        self.parent.ui.fitting_kropff_bragg_peak_sigma_groupBox.setTitle(u"\u03c3")

    def ui(self):
        ui_dict = self.grand_parent.session_dict[DataType.fitting]['ui']

        # splitters
        try:
            splitter_2_size = ui_dict['splitter_2']
            self.parent.ui.splitter_2.setSizes(splitter_2_size)

            splitter_size = ui_dict['splitter_4']
            self.parent.ui.splitter_4.setSizes(splitter_size)

            splitter_3_size = ui_dict['splitter_3']
            if splitter_3_size:
                self.parent.ui.splitter_3.setSizes(splitter_3_size)
            else:
                self.parent.ui.splitter_3.setSizes([150, 800])

            kropff_top_horizontal_splitter = ui_dict['kropff_top_horizontal_splitter']
            self.parent.ui.kropff_top_horizontal_splitter.setSizes(splitter_3_size)

        except TypeError:
            logging.info("Splitters have not been set due to log file format error! This should only show up once.")

    def matplotlib(self):

        def _matplotlib(parent=None, widget=None):
            sc = MplCanvas(parent, width=5, height=2, dpi=100)
            # sc.axes.plot([0,1,2,3,4,5], [10, 1, 20 ,3, 40, 50])
            toolbar = NavigationToolbar(sc, parent)
            layout = QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)
            widget.setLayout(layout)
            return sc

        self.parent.kropff_high_plot = _matplotlib(parent=self.parent,
                                                   widget=self.parent.ui.high_widget)
        self.parent.kropff_low_plot = _matplotlib(parent=self.parent,
                                                  widget=self.parent.ui.low_widget)
        self.parent.kropff_bragg_peak_plot = _matplotlib(parent=self.parent,
                                                         widget=self.parent.ui.bragg_peak_widget)
