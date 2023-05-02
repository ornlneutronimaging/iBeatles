from qtpy.QtWidgets import QVBoxLayout, QHBoxLayout, QRadioButton, QSpacerItem, QWidget, QSizePolicy
import pyqtgraph as pg
from pyqtgraph.dockarea import DockArea, Dock

from ibeatles.utilities.colors import pen_color
from ibeatles import DataType, DEFAULT_NORMALIZATION_ROI
from ibeatles.icons import icons_rc
from ibeatles.step2 import roi_label_color


class Initialization:
    col_width = [70, 50, 50, 50, 50]

    def __init__(self, parent=None):
        self.parent = parent

    def all(self):
        self.table()
        self.pyqtgraph()
        self.splitter()

    def splitter(self):
        self.parent.step2_ui['area'].setStyleSheet("""
                                     QSplitter::handle{
                                     image: url(":/MPL Toolbar/vertical_splitter_handle.png");
                                     }
                                     """)

    def table(self):
        for _index, _width in enumerate(self.col_width):
            self.parent.ui.normalization_tableWidget.setColumnWidth(_index, _width)

    def pyqtgraph(self):
        area = DockArea()
        area.setVisible(False)
        d1 = Dock("Sample", size=(200, 300))
        d2 = Dock("STEP1: Background normalization", size=(200, 100))
        # d3 = Dock("STEP2: Working Range Selection", size=(200, 100))

        area.addDock(d1, 'top')
        # area.addDock(d3, 'bottom')
        area.addDock(d2, 'bottom')
        # area.moveDock(d2, 'above', d3)

        # preview_widget = pg.GraphicsLayoutWidget()
        pg.setConfigOptions(antialias=True)

        vertical_layout = QVBoxLayout()
        # preview_widget.setLayout(vertical_layout)

        # image view
        image_view = pg.ImageView(view=pg.PlotItem())
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()

        # vertical_layout.addWidget(image_view)
        # top_right_widget = QWidget()
        d1.addWidget(image_view)

        # bragg edge plot
        bragg_edge_plot = pg.PlotWidget()
        bragg_edge_plot.plot()

        # # bragg_edge_plot.setLabel("top", "")
        # p1 = bragg_edge_plot.plotItem
        # p1.layout.removeItem(p1.getAxis('top'))
        # caxis = CustomAxis(orientation='top', parent=p1)
        # caxis.setLabel('')
        # caxis.linkToView(p1.vb)
        # p1.layout.addItem(caxis, 1, 1)

        # add file_index, TOF, Lambda x-axis buttons
        hori_layout = QHBoxLayout()
        button_widgets = QWidget()
        button_widgets.setLayout(hori_layout)

        # file index
        file_index_button = QRadioButton()
        file_index_button.setText("File Index")
        file_index_button.setChecked(True)
        # self.parent.connect(file_index_button, QtCore.SIGNAL("clicked()"),
        #                     self.parent.step2_file_index_radio_button_clicked)
        file_index_button.pressed.connect(self.parent.step2_file_index_radio_button_clicked)

        # tof
        tof_button = QRadioButton()
        tof_button.setText("TOF")
        # self.parent.connect(tof_button, QtCore.SIGNAL("clicked()"),
        #                     self.parent.step2_tof_radio_button_clicked)
        tof_button.pressed.connect(self.parent.step2_tof_radio_button_clicked)

        # lambda
        lambda_button = QRadioButton()
        lambda_button.setText(u"\u03BB")
        # self.parent.connect(lambda_button, QtCore.SIGNAL("clicked()"),
        #                     self.parent.step2_lambda_radio_button_clicked)
        lambda_button.pressed.connect(self.parent.step2_lambda_radio_button_clicked)

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
        self.parent.ui.normalization_left_widget.setLayout(vertical_layout)

        self.parent.step2_ui['area'] = area
        self.parent.step2_ui['image_view'] = image_view
        self.parent.step2_ui['bragg_edge_plot'] = bragg_edge_plot
        # self.parent.step2_ui['normalized_profile_plot'] = normalized_profile_plot
        # self.parent.step2_ui['caxis'] = caxis
        self.parent.step2_ui['xaxis_file_index'] = file_index_button
        self.parent.step2_ui['xaxis_lambda'] = lambda_button
        self.parent.step2_ui['xaxis_tof'] = tof_button

        self.parent.xaxis_button_ui['normalization']['tof'] = tof_button
        self.parent.xaxis_button_ui['normalization']['file_index'] = file_index_button
        self.parent.xaxis_button_ui['normalization']['lambda'] = lambda_button

    def roi(self):
        image_view = self.parent.step2_ui['image_view']

        if self.parent.list_roi[DataType.normalization]:

            for _roi_id in self.parent.list_roi_id[DataType.normalization]:
                image_view.removeItem(_roi_id)
            for _label_roi_id in self.parent.list_label_roi_id[DataType.normalization]:
                image_view.removeItem(_label_roi_id)

            list_roi = self.parent.list_roi[DataType.normalization]
            list_roi_id = []
            list_label_roi_id = []

            for _roi in list_roi:
                [is_visible, x0, y0, width, height, region_type] = _roi
                x0 = int(x0)
                y0 = int(y0)
                width = int(width)
                height = int(height)

                roi = pg.ROI([x0, y0], [width, height], pen=pen_color['0'])
                roi.addScaleHandle([1, 1], [0, 0])
                image_view.addItem(roi)
                roi.sigRegionChanged.connect(self.parent.normalization_manual_roi_changed)

                label_roi = pg.TextItem(html=f'<div style="text-align: center"><span style="color: '
                                             f'{roi_label_color[str(region_type)]};">' + region_type +
                                             '</span></div>',
                                        anchor=(-0.3, 1.3),
                                        border='w',
                                        fill=(0, 0, 255, 50))
                label_roi.setPos(x0, y0)
                image_view.addItem(label_roi)

                label_roi.setVisible(is_visible)
                roi.setVisible(is_visible)

                list_roi_id.append(roi)
                list_label_roi_id.append(label_roi)

            self.parent.list_roi_id[DataType.normalization] = list_roi_id
            self.parent.list_label_roi_id[DataType.normalization] = list_label_roi_id

        else:

            self.parent.list_roi[DataType.normalization] = DEFAULT_NORMALIZATION_ROI
            [_, x0, y0, width, height, region_type] = DEFAULT_NORMALIZATION_ROI
            x0 = int(x0)
            y0 = int(y0)
            width = int(width)
            height = int(height)

            roi = pg.ROI([x0, y0], [width, height], pen=pen_color['0'])
            roi.addScaleHandle([1, 1], [0, 0])
            image_view.addItem(roi)
            roi.sigRegionChanged.connect(self.parent.normalization_manual_roi_changed)

            label_roi = pg.TextItem(html=f'<div style="text-align: center"><span style="color: '
                                         f'{roi_label_color[region_type]};">' + region_type + '</span></div>',
                                    anchor=(-0.3, 1.3),
                                    border='w',
                                    fill=(0, 0, 255, 50))
            label_roi.setPos(x0, y0)
            image_view.addItem(label_roi)
            self.parent.list_roi_id[DataType.normalization] = [roi]
            self.parent.list_label_roi_id[DataType.normalization] = [label_roi]
