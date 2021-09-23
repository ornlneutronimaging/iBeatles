from qtpy.QtWidgets import (QProgressBar, QVBoxLayout, QPushButton, QHBoxLayout, QRadioButton, QWidget, QSpacerItem,
                            QSizePolicy)
from qtpy.QtGui import QIcon
from pyqtgraph.dockarea import DockArea, Dock
import pyqtgraph as pg

from neutronbraggedge.material_handler.retrieve_material_metadata import RetrieveMaterialMetadata
from neutronbraggedge.braggedge import BraggEdge

from .gui_handler import Step1GuiHandler as GuiHandler
from .. import DataType
from .roi import Roi


class Initialization:

    def __init__(self, parent=None):
        self.parent = parent

    def statusbar(self):
        self.parent.eventProgress = QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)

        self.parent.setStyleSheet("QStatusBar{padding-left:8px;color:red;font-weight:bold;}")

        #        self.parent.ui.statusbar.showMessage("this is an error", 2000)

    def gui(self):
        # define position and size
        rect = self.parent.geometry()
        self.parent.setGeometry(10, 10, rect.width(), rect.height())
        self.parent.ui.sample_ob_splitter.setSizes([850, 20])
        self.parent.ui.load_data_splitter.setSizes([200, 500])
        self.parent.ui.normalized_splitter.setSizes([150, 600])

        # make sure user load data first (before OB)
        self.parent.ui.import_open_beam_button.setEnabled(False)

        # reset buttons
        icon = QIcon(":/MPL Toolbar/reset_icon.png")
        self.parent.ui.reset_lattice_button.setIcon(icon)
        self.parent.ui.reset_lattice_button_2.setIcon(icon)
        self.parent.ui.reset_crystal_structure_button.setIcon(icon)
        self.parent.ui.reset_crystal_structure_button_2.setIcon(icon)

        # add shortcuts to menu button
        self.parent.ui.action1_load_data.setShortcut('Ctrl+1')
        self.parent.ui.action2_Normalization_2.setShortcut('Ctrl+2')
        self.parent.ui.action3_Normalized_Data.setShortcut('Ctrl+3')
        self.parent.ui.action3_Binning.setShortcut('Ctrl+4')
        self.parent.ui.action4_Fitting.setShortcut('Ctrl+5')
        self.parent.ui.action5_Results.setShortcut('Ctrl+6')

    def material_widgets(self):
        retrieve_material = RetrieveMaterialMetadata(material='all')
        list_returned = retrieve_material.full_list_material()
        self.parent.ui.list_of_elements.addItems(list_returned)
        self.parent.ui.list_of_elements_2.addItems(list_returned)

        o_gui = GuiHandler(parent=self.parent,
                           data_type=DataType.sample)
        _handler = BraggEdge(material=o_gui.get_element_selected())
        _crystal_structure = _handler.metadata['crystal_structure'][o_gui.get_element_selected()]
        _lattice = str(_handler.metadata['lattice'][o_gui.get_element_selected()])
        self.parent.ui.lattice_parameter.setText(_lattice)
        self.parent.ui.lattice_parameter_2.setText(_lattice)
        o_gui.set_crystal_structure(_crystal_structure)

    def labels(self):
        # micross
        self.parent.ui.micro_s.setText(u"\u00B5s")
        self.parent.ui.micro_s_2.setText(u"\u00B5s")
        # distance source detector
        self.parent.ui.distance_source_detector_label.setText("d<sub> source-detector</sub>")
        self.parent.ui.distance_source_detector_label_2.setText("d<sub> source-detector</sub>")
        # delta lambda
        self.parent.ui.delta_lambda_label.setText(u"\u0394\u03BB:")
        self.parent.ui.delta_lambda_label_2.setText(u"\u0394\u03BB:")
        # Angstroms
        self.parent.ui.angstroms_label.setText(u"\u212B")
        self.parent.ui.angstroms_label_2.setText(u"\u212B")

    def general_init_pyqtgrpah(self, roi_function,
                               base_widget,
                               add_function,
                               mean_function,
                               file_index_function,
                               tof_function,
                               lambda_function):

        area = DockArea()
        area.setVisible(False)
        d1 = Dock("Image Preview", size=(200, 300))
        d2 = Dock("Bragg Edge", size=(200, 100))

        area.addDock(d1, 'top')
        area.addDock(d2, 'bottom')

        preview_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)  # this improve display

        vertical_layout = QVBoxLayout()
        preview_widget.setLayout(vertical_layout)

        # image view
        image_view = pg.ImageView()
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
        add_button.setChecked(True)
        add_button.released.connect(add_function)
        line_layout.addWidget(add_button)

        mean_button = QRadioButton()
        mean_button.setText("Mean")
        mean_button.setChecked(False)
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
        bragg_edge_plot = pg.PlotWidget(title='')
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
        lambda_button.setText(u"\u03BB")
        lambda_button.pressed.connect(lambda_function)

        spacer1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hori_layout.addItem(spacer1)
        hori_layout.addWidget(file_index_button)
        hori_layout.addWidget(tof_button)
        hori_layout.addWidget(lambda_button)
        spacer2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        hori_layout.addItem(spacer2)

        d2.addWidget(bragg_edge_plot)
        d2.addWidget(button_widgets)

        vertical_layout.addWidget(area)
        base_widget.setLayout(vertical_layout)

        return [area, image_view, roi, bragg_edge_plot,
                caxis, roi_editor_button, add_button, mean_button,
                file_index_button, tof_button, lambda_button]

    def pyqtgraph(self):

        # sample
        [self.parent.ui.area,
         self.parent.ui.image_view,
         self.parent.ui.image_view_roi,
         self.parent.ui.bragg_edge_plot,
         self.parent.ui.caxis,
         self.parent.ui.roi_editor_button,
         self.parent.ui.roi_add_button,
         self.parent.ui.roi_mean_button,
         file_index_button,
         tof_button,
         lambda_button] = self.general_init_pyqtgrpah(self.parent.roi_image_view_changed,
                                                      self.parent.ui.preview_widget,
                                                      self.parent.roi_algorithm_is_add_clicked,
                                                      self.parent.roi_algorithm_is_mean_clicked,
                                                      self.parent.file_index_xaxis_button_clicked,
                                                      self.parent.tof_xaxis_button_clicked,
                                                      self.parent.lambda_xaxis_button_clicked)
        self.parent.list_roi_id['sample'].append(self.parent.ui.image_view_roi)
        self.parent.xaxis_button_ui['sample']['tof'] = tof_button
        self.parent.xaxis_button_ui['sample']['file_index'] = file_index_button
        self.parent.xaxis_button_ui['sample']['lambda'] = lambda_button

        # ob
        [self.parent.ui.ob_area,
         self.parent.ui.ob_image_view,
         self.parent.ui.ob_image_view_roi,
         self.parent.ui.ob_bragg_edge_plot,
         self.parent.ui.ob_caxis,
         self.parent.ui.ob_roi_editor_button,
         self.parent.ui.ob_roi_add_button,
         self.parent.ui.ob_roi_mean_button,
         file_index_button,
         tof_button,
         lambda_button] = self.general_init_pyqtgrpah(self.parent.roi_ob_image_view_changed,
                                                      self.parent.ui.ob_preview_widget,
                                                      self.parent.ob_roi_algorithm_is_add_clicked,
                                                      self.parent.ob_roi_algorithm_is_mean_clicked,
                                                      self.parent.ob_file_index_xaxis_button_clicked,
                                                      self.parent.ob_tof_xaxis_button_clicked,
                                                      self.parent.ob_lambda_xaxis_button_clicked)
        self.parent.list_roi_id['ob'].append(self.parent.ui.ob_image_view_roi)
        self.parent.xaxis_button_ui['ob']['tof'] = tof_button
        self.parent.xaxis_button_ui['ob']['file_index'] = file_index_button
        self.parent.xaxis_button_ui['ob']['lambda'] = lambda_button

        # normalized
        [self.parent.ui.normalized_area,
         self.parent.ui.normalized_image_view,
         self.parent.ui.normalized_image_view_roi,
         self.parent.ui.normalized_bragg_edge_plot,
         self.parent.ui.normalized_caxis,
         self.parent.ui.normalized_roi_editor_button,
         self.parent.ui.normalized_roi_add_button,
         self.parent.ui.normalized_roi_mean_button,
         file_index_button1,
         tof_button1,
         lambda_button1] = self.general_init_pyqtgrpah(self.parent.roi_normalized_image_view_changed,
                                                       self.parent.ui.normalized_preview_widget,
                                                       self.parent.normalized_roi_algorithm_is_add_clicked,
                                                       self.parent.normalized_roi_algorithm_is_mean_clicked,
                                                       self.parent.normalized_file_index_xaxis_button_clicked,
                                                       self.parent.normalized_tof_xaxis_button_clicked,
                                                       self.parent.normalized_lambda_xaxis_button_clicked)

        self.parent.list_roi_id['normalized'].append(self.parent.ui.normalized_image_view_roi)
        self.parent.xaxis_button_ui['normalized']['tof'] = tof_button1
        self.parent.xaxis_button_ui['normalized']['file_index'] = file_index_button1
        self.parent.xaxis_button_ui['normalized']['lambda'] = lambda_button1

    def connect_widgets(self):
        self.parent.ui.list_of_elements.currentIndexChanged.connect(self.parent.list_of_element_index_changed)
        self.parent.ui.list_of_elements_2.currentIndexChanged.connect(self.parent.list_of_element_2_index_changed)
