from qtpy.QtWidgets import QProgressBar, QVBoxLayout, QHBoxLayout, QRadioButton
from qtpy.QtWidgets import QSpacerItem, QSizePolicy, QWidget
from qtpy.QtGui import QIcon
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph as pg

from src.ibeatles import interact_me_style
from src.ibeatles.utilities.table_handler import TableHandler
from src.ibeatles.utilities.matplotlibview import MatplotlibView
from src.ibeatles import MICRO, LAMBDA, ANGSTROMS, DELTA
from src.ibeatles import auto_image, manual_image, settings_image, more_infos_image
from src.ibeatles import stats_table_image, stats_plot_image


class Initialization:

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent

    def all(self):
        self.pyqtgraph_bin()
        self.plot_widgets()
        self.statusbar()
        self.splitter()
        self.table()
        self.labels()
        self.tab()
        self.combobox()
        self.widgets()

    def setup(self):
        distance_source_detector = self.top_parent.ui.distance_source_detector.text()
        self.parent.ui.distance_source_detector_label.setText(distance_source_detector)

        detector_offset = self.top_parent.ui.detector_offset.text()
        self.parent.ui.detector_offset_label.setText(detector_offset)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
        self.parent.setStyleSheet("QStatusBar{padding-left:8px;color:red;font-weight:bold;}")

    def splitter(self):
        self.parent.ui.bin_horizontal_splitter.setSizes([300, 800])
        self.parent.ui.bin_horizontal_splitter.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/horizontal_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.bin_horizontal_splitter.setHandleWidth(15)

        self.parent.ui.bin_vertical_splitter.setSizes([500, 50])
        self.parent.ui.bin_vertical_splitter.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/vertical_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.bin_vertical_splitter.setHandleWidth(15)

    def combobox(self):
        list_of_options = ['mean', 'median', 'std', 'min', 'max']
        self.parent.ui.bin_stats_comboBox.blockSignals(True)
        self.parent.ui.bin_stats_comboBox.addItems(list_of_options)
        self.parent.ui.bin_stats_comboBox.blockSignals(False)

    def table(self):

        # bin auto table
        o_table = TableHandler(table_ui=self.parent.ui.bin_auto_tableWidget)
        column_sizes = [40, 35, 60, 115, 115]
        o_table.set_column_sizes(column_sizes=column_sizes)
        column_names = ['use?',
                        'bin #',
                        'file #',
                        'tof range (' + MICRO + "s)",
                        LAMBDA + " range (" + ANGSTROMS + ")"]
        o_table.set_column_names(column_names=column_names)

        # bin manual table
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        column_sizes = [35, 80, 130, 130]
        o_table.set_column_sizes(column_sizes=column_sizes)
        column_names = column_names[1:]
        o_table.set_column_names(column_names=column_names)

        # statistics
        o_table = TableHandler(table_ui=self.parent.ui.statistics_tableWidget)
        column_names = ['bin #',
                        'file #',
                        'tof range (' + MICRO + "s)",
                        LAMBDA + " range (" + ANGSTROMS + ")",
                        'mean',
                        'median',
                        'std',
                        'min',
                        'max',
                        ]
        o_table.set_column_names(column_names=column_names)
        column_sizes = [35, 80, 130, 130, 130, 130, 130, 130, 130]
        o_table.set_column_sizes(column_sizes=column_sizes)

    def labels(self):
        self.parent.ui.bin_auto_log_file_index_radioButton.setText(DELTA + "file_index/file_index")
        self.parent.ui.bin_auto_log_tof_radioButton.setText(DELTA + "tof")
        self.parent.ui.bin_auto_log_lambda_radioButton.setText(DELTA + LAMBDA + "/" + LAMBDA)

        self.parent.ui.auto_linear_file_index_radioButton.setText(DELTA + " file index")
        self.parent.ui.auto_linear_tof_radioButton.setText(DELTA + " tof")
        self.parent.ui.auto_linear_lambda_radioButton.setText(DELTA + LAMBDA)
        self.parent.ui.bin_auto_linear_tof_units_label.setText(MICRO + 's')
        self.parent.ui.bin_auto_linear_lambda_units_label.setText(ANGSTROMS)

    def tab(self):
        self.parent.ui.bin_tabWidget.setTabIcon(0, QIcon(auto_image))
        self.parent.ui.bin_tabWidget.setTabIcon(1, QIcon(manual_image))
        self.parent.ui.stats_tabWidget.setTabIcon(0, QIcon(stats_table_image))
        self.parent.ui.stats_tabWidget.setTabIcon(1, QIcon(stats_plot_image))
        self.parent.ui.bin_bottom_tabWidget.setTabIcon(2, QIcon(settings_image))
        self.parent.ui.image_tabWidget.setCurrentIndex(1)

    def plot_widgets(self):
        graphics_view_layout = QVBoxLayout()
        statistics_plot = MatplotlibView(self.parent)
        graphics_view_layout.addWidget(statistics_plot)
        self.parent.ui.statistics_plot_widget.setLayout(graphics_view_layout)
        self.parent.statistics_plot = statistics_plot

    def pyqtgraph_bin(self):
        # integrated image
        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        self.parent.integrated_view = image_view
        # image_view.scene.sigMouseMoved.connect(self.parent.mouse_moved_in_integrated_view)
        layout = QVBoxLayout()
        layout.addWidget(image_view)
        self.parent.ui.integrated_image_widget.setLayout(layout)

        # profile
        bin_view = pg.PlotWidget(title="")
        bin_view.plot()
        self.parent.bin_profile_view = bin_view
        layout = QVBoxLayout()
        layout.addWidget(bin_view)
        self.parent.ui.bin_widget.setLayout(layout)

    def widgets(self):
        self.parent.ui.visualize_auto_bins_axis_generated_pushButton.setIcon(QIcon(more_infos_image))
        self.parent.ui.visualize_auto_bins_axis_generated_pushButton.setToolTip("Display full original bin axis")
        self.parent.ui.select_folder_pushButton.setStyleSheet(interact_me_style)
