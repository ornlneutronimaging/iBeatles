from qtpy.QtWidgets import QProgressBar, QVBoxLayout, QHBoxLayout, QRadioButton
from qtpy.QtWidgets import QSpacerItem, QSizePolicy, QWidget
from qtpy.QtGui import QIcon
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph as pg

from ibeatles.tools.tof_combine.utilities.table_handler import TableHandler
from ibeatles.tools.tof_combine import MICRO, LAMBDA, ANGSTROMS
from ibeatles.tools.tof_combine import settings_image


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.pyqtgraph_combine()
        self.statusbar()
        self.splitter()
        self.table()
        self.tab()
        self.labels()
        self.widgets()

    def tab(self):
        self.parent.ui.combine_bottom_tabWidget.setTabIcon(2, QIcon(settings_image))

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
        self.parent.setStyleSheet("QStatusBar{padding-left:8px;color:red;font-weight:bold;}")

    def splitter(self):
        self.parent.ui.combine_horizontal_splitter.setSizes([100, 0])
        self.parent.ui.combine_horizontal_splitter.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/horizontal_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.combine_horizontal_splitter.setHandleWidth(15)

    def table(self):
        # combine table
        o_table = TableHandler(table_ui=self.parent.ui.combine_tableWidget)
        column_sizes = [100, 100, 500]
        o_table.set_column_sizes(column_sizes=column_sizes)

    def labels(self):
        # combine tab
        self.parent.ui.combine_detector_offset_units.setText(MICRO + "s")

    def pyqtgraph_combine(self):
        area = DockArea()
        self.parent.ui.area = area
        d1 = Dock("Image Preview", size=(200, 300))
        d2 = Dock("ROI profile", size=(200, 100))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')

        # preview - top widget
        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        self.parent.combine_image_view = image_view
        image_view.scene.sigMouseMoved.connect(self.parent.mouse_moved_in_combine_image_preview)
        d1.addWidget(image_view)

        # plot and x-axis radio buttons - bottom widgets
        profile = pg.PlotWidget(title="")
        profile.plot()
        self.parent.combine_profile_view = profile
        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(profile)
        # xaxis radio buttons
        spacer_left = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        file_index_radio_button = QRadioButton("File Index")
        file_index_radio_button.setChecked(True)
        self.parent.combine_file_index_radio_button = file_index_radio_button
        self.parent.combine_file_index_radio_button.clicked.connect(self.parent.combine_xaxis_changed)
        tof_radio_button = QRadioButton("TOF (" + MICRO + "s)")
        self.parent.tof_radio_button = tof_radio_button
        self.parent.tof_radio_button.clicked.connect(self.parent.combine_xaxis_changed)
        lambda_radio_button = QRadioButton(LAMBDA + " (" + ANGSTROMS + ")")
        self.parent.lambda_radio_button = lambda_radio_button
        self.parent.lambda_radio_button.clicked.connect(self.parent.combine_xaxis_changed)
        spacer_right = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        axis_layout = QHBoxLayout()
        axis_layout.addItem(spacer_left)
        axis_layout.addWidget(file_index_radio_button)
        axis_layout.addWidget(tof_radio_button)
        axis_layout.addWidget(lambda_radio_button)
        axis_layout.addItem(spacer_right)
        bottom_widget = QWidget()
        bottom_widget.setLayout(axis_layout)
        bottom_layout.addWidget(bottom_widget)
        widget = QWidget()
        widget.setLayout(bottom_layout)
        d2.addWidget(widget)

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(area)
        self.parent.ui.combine_widget.setLayout(vertical_layout)
        self.parent.ui.combine_widget.setEnabled(False)

    def widgets(self):
        self.parent.ui.combine_refresh_top_folder_pushButton.setEnabled(False)
