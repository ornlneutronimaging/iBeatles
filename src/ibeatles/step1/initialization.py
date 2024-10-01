from qtpy.QtWidgets import (
    QProgressBar,
    QVBoxLayout,
    QPushButton,
    QHBoxLayout,
    QRadioButton,
    QWidget,
    QSpacerItem,
    QSizePolicy,
    QScrollBar,
    QLabel,
)
from qtpy.QtGui import QPixmap
from qtpy import QtCore
from qtpy.QtGui import QIcon
from qtpy.QtCore import QSize
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph as pg

from neutronbraggedge.material_handler.retrieve_material_metadata import (
    RetrieveMaterialMetadata,
)

from src.ibeatles import (
    fitting_image,
    pixel_binning_image,
    rotate_image,
    strain_mapping_image,
    tof_binning_image,
    tof_combine_image,
)
from src.ibeatles import (
    step1_icon,
    step2_icon,
    step3_icon,
    step4_icon,
    infos_file,
    preview_file,
    error_icon_file,
)
from src.ibeatles import DataType
from src.ibeatles.step1.roi import Roi
from src.ibeatles.utilities.table_handler import TableHandler

tab6_top_button_width = 250
tab6_top_button_height = 150

tab6_bottom_buttom_width = 250
tab6_bottom_button_height = 250


class Initialization:
    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.gui()
        self.labels()
        self.material_widgets()
        self.statusbar()
        self.pyqtgraph()
        self.icons()
        self.widgets()
        self.splitters()
        self.tabs()

    def tabs(self):
        self.parent.ui.tabWidget.setTabIcon(0, QIcon(step1_icon))
        self.parent.ui.tabWidget.setTabIcon(1, QIcon(step2_icon))
        self.parent.ui.tabWidget.setTabIcon(2, QIcon(step3_icon))
        self.parent.ui.tabWidget.setTabIcon(3, QIcon(step4_icon))

    def splitters(self):
        self.parent.ui.sample_ob_splitter.setSizes([100, 0])
        self.parent.ui.sample_ob_splitter.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/horizontal_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.sample_ob_splitter.setHandleWidth(15)

        self.parent.ui.horizontal_normalization_splitter.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/horizontal_splitter_handle.png");
                                     }
                                     """)

        self.parent.ui.normalized_splitter.setSizes([100, 0])
        self.parent.ui.normalized_splitter.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/horizontal_splitter_handle.png");
                                     }
                                     """)
        self.parent.ui.normalized_splitter.setHandleWidth(15)

        self.parent.ui.area.setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/vertical_splitter_handle.png");
                                     }
                                     """)

        self.parent.ui.ob_area.setStyleSheet("""
                                         QSplitter::handle{
                                         image: url(":/MPL Toolbar/vertical_splitter_handle.png");
                                         }
                                         """)
        self.parent.ui.normalized_area.setStyleSheet("""
                                         QSplitter::handle{
                                         image: url(":/MPL Toolbar/vertical_splitter_handle.png");
                                         }
                                         """)

    def widgets(self):
        # folder path of time spectra
        self.parent.ui.time_spectra_folder_2.setVisible(False)
        self.parent.ui.time_spectra_folder.setVisible(False)

        self.parent.ui.sample_infos_pushButton.setIcon(QIcon(infos_file))
        self.parent.ui.ob_infos_pushButton.setIcon(QIcon(infos_file))
        self.parent.ui.normalized_infos_pushButton.setIcon(QIcon(infos_file))

        column_sizes = [30, 30, 30, 60]
        o_table = TableHandler(table_ui=self.parent.ui.pre_defined_tableWidget)
        o_table.set_column_sizes(column_sizes=column_sizes)
        o_table = TableHandler(table_ui=self.parent.ui.method2_tableWidget)
        o_table.set_column_sizes(column_sizes=column_sizes)
        o_table = TableHandler(table_ui=self.parent.ui.method1_tableWidget)
        o_table.set_column_sizes(column_sizes=column_sizes)

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
        self.parent.setStyleSheet(
            "QStatusBar{padding-left:8px;color:red;font-weight:bold;}"
        )

    def gui(self):
        # define position and size
        rect = self.parent.geometry()
        self.parent.setGeometry(10, 10, rect.width(), rect.height())
        self.parent.ui.sample_ob_splitter.setSizes([850, 20])
        self.parent.ui.normalized_splitter.setSizes([150, 600])

        # ob tab
        self.parent.ui.load_data_tab.blockSignals(True)
        self.parent.ui.load_data_tab.setTabEnabled(1, False)
        self.parent.ui.load_data_tab.blockSignals(False)

        # normalized
        self.parent.ui.tabWidget.setTabEnabled(1, False)

        # add shortcuts to menu button
        self.parent.ui.action1_load_data.setShortcut("Ctrl+1")
        self.parent.ui.action2_Normalization_2.setShortcut("Ctrl+2")
        self.parent.ui.action3_Normalized_Data.setShortcut("Ctrl+3")
        self.parent.ui.action3_Binning.setShortcut("Ctrl+4")
        self.parent.ui.action4_Fitting.setShortcut("Ctrl+5")
        self.parent.ui.action5_Results.setShortcut("Ctrl+6")

    def material_widgets(self):
        retrieve_material = RetrieveMaterialMetadata(material="all")
        list_returned = retrieve_material.full_list_material()

        self.parent.ui.pre_defined_list_of_elements.blockSignals(True)
        self.parent.ui.user_defined_list_of_elements.blockSignals(True)
        self.parent.ui.pre_defined_list_of_elements.addItems(list_returned)
        extanded_list = list(list_returned)
        extanded_list.insert(0, "None")
        self.parent.ui.user_defined_list_of_elements.addItems(extanded_list)
        self.parent.ui.pre_defined_list_of_elements.blockSignals(False)
        self.parent.ui.user_defined_list_of_elements.blockSignals(False)

        # o_gui = GuiHandler(parent=self.parent,
        #                    data_type=DataType.sample)
        # _handler = BraggEdge(material=o_gui.get_element_selected())
        # _crystal_structure = _handler.metadata['crystal_structure'][o_gui.get_element_selected()]
        # _lattice = str(_handler.metadata['lattice'][o_gui.get_element_selected()])
        # self.parent.ui.lattice_parameter.setText(_lattice)
        # o_gui.set_crystal_structure(_crystal_structure)

        column_names = ["h", "k", "l", "\u03bb\u2090"]
        o_table = TableHandler(table_ui=self.parent.ui.pre_defined_tableWidget)
        o_table.set_column_names(column_names=column_names)
        o_table = TableHandler(table_ui=self.parent.ui.method1_tableWidget)
        o_table.set_column_names(column_names=column_names)

        self.parent.ui.method1_tableWidget.setEnabled(True)

        imgpix = QPixmap(error_icon_file)
        self.parent.ui.user_defined_name_error.setPixmap(imgpix)
        self.parent.ui.method1_lattice_error.setPixmap(imgpix)
        self.parent.ui.user_defined_method1_table_error.setPixmap(imgpix)
        self.parent.ui.user_defined_method2_table_error.setPixmap(imgpix)

    def labels(self):
        # micros
        self.parent.ui.micro_s.setText("\u00b5s")
        # distance source detector
        self.parent.ui.distance_source_detector_label.setText(
            "d<sub> source-detector</sub>"
        )
        # delta lambda
        self.parent.ui.delta_lambda_label.setText("\u0394\u03bb:")
        # Angstroms
        self.parent.ui.pre_defined_lattice_units.setText("\u212b")
        self.parent.ui.method1_lattice_units.setText("\u212b")

        # # tab 4
        # self.parent.ui.analysis_tab_arrow_label1.setStyleSheet(f"background-image: {right_blue_arrow}")
        # self.parent.ui.analysis_tab_arrow_label1.resize(200, 200)

    def general_init_pyqtgrpah(
        self,
        roi_function,
        base_widget,
        add_function,
        mean_function,
        file_index_function,
        tof_function,
        lambda_function,
        scroll_bar_function,
    ):
        area = DockArea()
        area.setVisible(False)
        d1 = Dock("Image Preview", size=(200, 200))
        d2 = Dock("Bragg Edge", size=(200, 200))

        area.addDock(d1, "top")
        area.addDock(d2, "bottom")

        preview_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)  # this improves the display

        vertical_layout = QVBoxLayout()
        preview_widget.setLayout(vertical_layout)

        # image view
        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        roi = Roi.get_default_roi()
        # image_view.addItem(roi)
        roi.sigRegionChanged.connect(roi_function)

        roi_editor_button = QPushButton("ROI editor ...")
        roi_editor_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        roi_editor_button.pressed.connect(self.parent.roi_editor_button_clicked)
        line_layout = QHBoxLayout()
        line_layout.addWidget(roi_editor_button)

        add_button = QRadioButton()
        add_button.setText("Add")
        add_button.setChecked(False)
        add_button.released.connect(add_function)
        line_layout.addWidget(add_button)

        mean_button = QRadioButton()
        mean_button.setText("Mean")
        mean_button.setChecked(True)
        mean_button.released.connect(mean_function)
        line_layout.addWidget(mean_button)

        top_widget = QWidget()
        top_widget.setLayout(line_layout)

        top_right_widget = QWidget()
        vertical = QVBoxLayout()
        vertical.addWidget(top_widget)

        vertical.addWidget(image_view)
        top_right_widget.setLayout(vertical)
        d1.addWidget(top_right_widget)

        # bragg edge plot
        bragg_edge_plot = pg.PlotWidget(title="")
        bragg_edge_plot.plot()

        # bragg_edge_plot.setLabel("top", "")
        # p1 = bragg_edge_plot.plotItem
        # p1.layout.removeItem(p1.getAxis('top'))
        # caxis = CustomAxis(orientation='top', parent=p1)
        # caxis.setLabel('')
        # caxis.linkToView(p1.vb)
        # p1.layout.addItem(caxis, 1, 1)
        caxis = None

        # add file_index, TOF, Lambda x-axis buttons
        hori_layout = QHBoxLayout()
        button_widgets = QWidget()
        button_widgets.setLayout(hori_layout)

        # file index
        file_index_button = QRadioButton()
        file_index_button.setText("File Index")
        file_index_button.setChecked(True)
        file_index_button.pressed.connect(file_index_function)

        # tof
        tof_button = QRadioButton()
        tof_button.setText("TOF")
        tof_button.pressed.connect(tof_function)

        # lambda
        lambda_button = QRadioButton()
        lambda_button.setText("\u03bb")
        lambda_button.pressed.connect(lambda_function)

        spacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hori_layout.addItem(spacer1)
        hori_layout.addWidget(file_index_button)
        hori_layout.addWidget(tof_button)
        hori_layout.addWidget(lambda_button)
        spacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hori_layout.addItem(spacer2)

        # hkl horizontal scroll widget
        scroll_hori_layout = QHBoxLayout()
        scroll_label = QLabel("Range of material Bragg peaks displayed:")
        scroll_hori_layout.addWidget(scroll_label)
        hori_scroll_widget = QScrollBar(QtCore.Qt.Horizontal)
        hori_scroll_widget.valueChanged.connect(scroll_bar_function)
        hori_scroll_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        scroll_hori_layout.addWidget(hori_scroll_widget)
        scroll_hori_widget = QWidget()
        scroll_hori_widget.setLayout(scroll_hori_layout)

        widget_vertical_layout = QVBoxLayout()
        widget_vertical_layout.addWidget(button_widgets)
        widget_vertical_layout.addWidget(scroll_hori_widget)

        bottom_widgets = QWidget()
        bottom_widgets.setLayout(widget_vertical_layout)

        d2.addWidget(bragg_edge_plot)
        d2.addWidget(bottom_widgets)

        vertical_layout.addWidget(area)
        base_widget.setLayout(vertical_layout)

        return [
            area,
            image_view,
            roi,
            bragg_edge_plot,
            caxis,
            roi_editor_button,
            add_button,
            mean_button,
            file_index_button,
            tof_button,
            lambda_button,
            scroll_label,
            hori_scroll_widget,
        ]

    def pyqtgraph(self):
        # sample
        [
            self.parent.ui.area,
            self.parent.ui.image_view,
            self.parent.ui.image_view_roi,
            self.parent.ui.bragg_edge_plot,
            self.parent.ui.caxis,
            self.parent.ui.roi_editor_button,
            self.parent.ui.roi_add_button,
            self.parent.ui.roi_mean_button,
            file_index_button,
            tof_button,
            lambda_button,
            self.parent.hkl_scrollbar_ui["label"][DataType.sample],
            self.parent.hkl_scrollbar_ui["widget"][DataType.sample],
        ] = self.general_init_pyqtgrpah(
            self.parent.roi_image_view_changed,
            self.parent.ui.preview_widget,
            self.parent.roi_algorithm_is_add_clicked,
            self.parent.roi_algorithm_is_mean_clicked,
            self.parent.file_index_xaxis_button_clicked,
            self.parent.tof_xaxis_button_clicked,
            self.parent.lambda_xaxis_button_clicked,
            self.parent.sample_hkl_scrollbar_changed,
        )

        self.parent.list_roi_id["sample"].append(self.parent.ui.image_view_roi)
        self.parent.xaxis_button_ui["sample"]["tof"] = tof_button
        self.parent.xaxis_button_ui["sample"]["file_index"] = file_index_button
        self.parent.xaxis_button_ui["sample"]["lambda"] = lambda_button

        # ob
        [
            self.parent.ui.ob_area,
            self.parent.ui.ob_image_view,
            self.parent.ui.ob_image_view_roi,
            self.parent.ui.ob_bragg_edge_plot,
            self.parent.ui.ob_caxis,
            self.parent.ui.ob_roi_editor_button,
            self.parent.ui.ob_roi_add_button,
            self.parent.ui.ob_roi_mean_button,
            file_index_button,
            tof_button,
            lambda_button,
            self.parent.hkl_scrollbar_ui["label"][DataType.ob],
            self.parent.hkl_scrollbar_ui["widget"][DataType.ob],
        ] = self.general_init_pyqtgrpah(
            self.parent.roi_ob_image_view_changed,
            self.parent.ui.ob_preview_widget,
            self.parent.ob_roi_algorithm_is_add_clicked,
            self.parent.ob_roi_algorithm_is_mean_clicked,
            self.parent.ob_file_index_xaxis_button_clicked,
            self.parent.ob_tof_xaxis_button_clicked,
            self.parent.ob_lambda_xaxis_button_clicked,
            self.parent.ob_hkl_scrollbar_changed,
        )

        self.parent.list_roi_id["ob"].append(self.parent.ui.ob_image_view_roi)
        self.parent.xaxis_button_ui["ob"]["tof"] = tof_button
        self.parent.xaxis_button_ui["ob"]["file_index"] = file_index_button
        self.parent.xaxis_button_ui["ob"]["lambda"] = lambda_button

        # normalized
        [
            self.parent.ui.normalized_area,
            self.parent.ui.normalized_image_view,
            self.parent.ui.normalized_image_view_roi,
            self.parent.ui.normalized_bragg_edge_plot,
            self.parent.ui.normalized_caxis,
            self.parent.ui.normalized_roi_editor_button,
            self.parent.ui.normalized_roi_add_button,
            self.parent.ui.normalized_roi_mean_button,
            file_index_button1,
            tof_button1,
            lambda_button1,
            self.parent.hkl_scrollbar_ui["label"][DataType.normalized],
            self.parent.hkl_scrollbar_ui["widget"][DataType.normalized],
        ] = self.general_init_pyqtgrpah(
            self.parent.roi_normalized_image_view_changed,
            self.parent.ui.normalized_preview_widget,
            self.parent.normalized_roi_algorithm_is_add_clicked,
            self.parent.normalized_roi_algorithm_is_mean_clicked,
            self.parent.normalized_file_index_xaxis_button_clicked,
            self.parent.normalized_tof_xaxis_button_clicked,
            self.parent.normalized_lambda_xaxis_button_clicked,
            self.parent.normalized_hkl_scrollbar_changed,
        )

        self.parent.list_roi_id["normalized"].append(
            self.parent.ui.normalized_image_view_roi
        )
        self.parent.xaxis_button_ui["normalized"]["tof"] = tof_button1
        self.parent.xaxis_button_ui["normalized"]["file_index"] = file_index_button1
        self.parent.xaxis_button_ui["normalized"]["lambda"] = lambda_button1

    def icons(self):
        # reset buttons
        preview_icon = QIcon(preview_file)
        self.parent.ui.preview_time_spectra_button.setIcon(preview_icon)
        self.parent.ui.preview_time_spectra_normalized_button.setIcon(preview_icon)

        # tab 6 - top buttons

        rotate_icon = QIcon(rotate_image)
        self.parent.ui.rotate_pushButton.setIcon(rotate_icon)
        self.parent.ui.rotate_pushButton.setIconSize(
            QSize(tab6_top_button_width, tab6_top_button_height)
        )

        tof_combine_icon = QIcon(tof_combine_image)
        self.parent.ui.tof_combine_pushButton.setIcon(tof_combine_icon)
        self.parent.ui.tof_combine_pushButton.setIconSize(
            QSize(tab6_top_button_width, tab6_top_button_height)
        )

        tof_binning_icon = QIcon(tof_binning_image)
        self.parent.ui.tof_binning_pushButton.setIcon(tof_binning_icon)
        self.parent.ui.tof_binning_pushButton.setIconSize(
            QSize(tab6_top_button_width, tab6_top_button_height)
        )

        # tab6 - bottom buttons

        pixel_binning_icon = QIcon(pixel_binning_image)
        self.parent.ui.roi_pixel_binning_pushButton.setIcon(pixel_binning_icon)
        self.parent.ui.roi_pixel_binning_pushButton.setIconSize(
            QSize(tab6_bottom_buttom_width, tab6_bottom_button_height)
        )

        fitting_icon = QIcon(fitting_image)
        self.parent.ui.fitting_pushButton.setIcon(fitting_icon)
        self.parent.ui.fitting_pushButton.setIconSize(
            QSize(tab6_bottom_buttom_width, tab6_bottom_button_height)
        )

        strain_mapping_icon = QIcon(strain_mapping_image)
        self.parent.ui.strain_mapping_pushButton.setIcon(strain_mapping_icon)
        self.parent.ui.strain_mapping_pushButton.setIconSize(
            QSize(tab6_bottom_buttom_width, tab6_bottom_button_height)
        )
