import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from qtpy.QtWidgets import QVBoxLayout

from ibeatles import ANGSTROMS, LAMBDA, SUB_0
from ibeatles import DataType
from ibeatles.utilities.mplcanvas import MplCanvasColorbar
from ibeatles.step6 import ParametersToDisplay
from ibeatles.step6.get import Get
from ibeatles.session import SessionSubKeys, SessionKeys
from ibeatles.widgets.qrangeslider import QRangeSlider
from ibeatles.step6 import INTERPOLATION_METHODS, DEFAULT_INTERPOLATION_INDEX, CMAPS, DEFAULT_CMAP_INDEX


class Initialization:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent

    def all(self):
        self.labels()
        self.parameters()
        # self.pyqtgraph()
        self.matplotlib()
        self.data()
        self.combobox()

    def combobox(self):
        self.parent.ui.interpolation_comboBox.blockSignals(True)
        self.parent.ui.interpolation_comboBox.addItems(INTERPOLATION_METHODS)
        self.parent.ui.interpolation_comboBox.setCurrentIndex(DEFAULT_INTERPOLATION_INDEX)
        self.parent.ui.interpolation_comboBox.blockSignals(False)
        self.parent.ui.interpolation_groupBox.setVisible(True)

        self.parent.ui.cmap_comboBox.blockSignals(True)
        self.parent.ui.cmap_comboBox.addItems(CMAPS)
        self.parent.ui.cmap_comboBox.setCurrentIndex(DEFAULT_CMAP_INDEX)
        self.parent.ui.cmap_comboBox.blockSignals(False)

    def labels(self):
        self.parent.ui.range_selected_from_units_label.setText(ANGSTROMS)
        self.parent.ui.range_selected_to_units_label.setText(ANGSTROMS)
        self.parent.ui.d0_units1_label.setText(ANGSTROMS)
        self.parent.ui.d0_units2_label.setText(ANGSTROMS)
        self.parent.ui.reference_material_lambda0_units_label.setText(ANGSTROMS)
        self.parent.ui.reference_material_lambda0_label.setText(LAMBDA + SUB_0)

    def range_slider(self):
        layout = QVBoxLayout()
        self.parent.ui.range_slider = QRangeSlider(splitterWidth=100,
                                                   vertical=True,
                                                   min_at_the_bottom=True)

        self.parent.ui.range_slider.setMin(self.parent.slider_min)
        self.parent.ui.range_slider.setMax(self.parent.slider_max)

        o_get = Get(parent=self.parent)
        parameter_displayed = o_get.parameter_to_display()

        real_min = self.parent.min_max[parameter_displayed]['min']
        real_max = self.parent.min_max[parameter_displayed]['max']

        self.parent.ui.max_range_lineEdit.setText(f"{real_max:.5f}")
        self.parent.ui.min_range_lineEdit.setText(f"{real_min:.5f}")

        self.parent.ui.range_slider.setRealMin(real_min)
        self.parent.ui.range_slider.setRealMax(real_max)

        self.parent.ui.range_slider.setRealRange(real_min + 1e-10, real_max)    # trick to display full range #BUG

        self.parent.ui.range_slider.startValueChanged.connect(
            self.parent.range_slider_start_value_changed)
        self.parent.ui.range_slider.endValueChanged.connect(
            self.parent.range_slider_end_value_changed)

        layout.addWidget(self.parent.ui.range_slider)
        self.parent.ui.vertical_range_slider_widget.setLayout(layout)

        self.parent.ui.range_slider.setBackgroundStyle('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ddd, stop:1 #333);')
        self.parent.ui.range_slider.handle.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #282, stop:1 #222);')

    def parameters(self):
        from_lambda = self.grand_parent.fitting_ui.ui.lambda_min_lineEdit.text()
        to_lambda = self.grand_parent.fitting_ui.ui.lambda_max_lineEdit.text()
        hkl_selected = self.grand_parent.fitting_ui.ui.hkl_list_ui.currentText()
        lambda_0 = float(self.grand_parent.fitting_ui.ui.bragg_edge_calculated.text())
        element = self.grand_parent.fitting_ui.ui.material_groupBox.title()

        self.parent.ui.from_lambda.setText(from_lambda)
        self.parent.ui.to_lambda.setText(to_lambda)
        self.parent.ui.hkl_value.setText(hkl_selected)
        self.parent.ui.d0_value.setText("{:.03f}".format(lambda_0 / 2.))
        self.parent.ui.material_name.setText(element)
        self.parent.ui.lambda_0.setText("{:.03f}".format(lambda_0))
        self.parent.ui.d0_user_value.setText("{:.03f}".format(lambda_0 / 2.))

        self.parent.bin_size = self.grand_parent.session_dict[SessionKeys.bin][SessionSubKeys.bin_size]

    def data(self):
        live_data = self.grand_parent.data_metadata[DataType.normalized]['data']
        integrated_image = np.mean(live_data, 0)
        self.parent.integrated_image = np.transpose(integrated_image)
        [self.parent.image_size['height'], self.parent.image_size['width']] = np.shape(integrated_image)

    # def pyqtgraph(self):
    #     image_view = pg.ImageView(view=pg.PlotItem())
    #     image_view.ui.roiBtn.hide()
    #     image_view.ui.menuBtn.hide()
    #     self.parent.image_view = image_view

    def matplotlib(self):

        def _matplotlib(parent=None, widget=None):
            sc = MplCanvasColorbar(parent, width=5, height=2, dpi=100)
            # sc.axes.plot([0,1,2,3,4,5], [10, 1, 20 ,3, 40, 50])
            toolbar = NavigationToolbar(sc, parent)
            layout = QVBoxLayout()
            layout.addWidget(toolbar)
            layout.addWidget(sc)
            widget.setLayout(layout)
            return sc

        self.parent.matplotlib_plot = _matplotlib(parent=self.parent,
                                                  widget=self.parent.ui.matplotlib_widget)

        self.parent.matplotlib_interpolation_plot = _matplotlib(parent=self.parent,
                                                                widget=self.parent.ui.matplotlib_interpolation_widget)

    def min_max_values(self):

        [_, x0, y0, width, height, bin_size] = self.grand_parent.session_dict[DataType.bin][
            SessionSubKeys.roi]

        max_row_index = self.grand_parent.session_dict[SessionKeys.bin][SessionSubKeys.nbr_row]
        max_col_index = self.grand_parent.session_dict[SessionKeys.bin][SessionSubKeys.nbr_column]

        d_array = self.parent.d_array
        d_array_roi = d_array[y0: y0 + (max_row_index * bin_size),
                              x0: x0 + (max_col_index * bin_size)]
        self.parent.min_max[ParametersToDisplay.d] = {'min': np.nanmin(d_array_roi),
                                                      'max': np.nanmax(d_array_roi),
                                                      'global_min': np.nanmin(d_array_roi),
                                                      'global_max': np.nanmax(d_array_roi)}

        # self.parent.min_max[ParametersToDisplay.d] = {'min': np.min(d_array_roi),
        #                                               'max': np.max(d_array_roi),
        #                                               'global_min': np.min(d_array),
        #                                               'global_max': np.max(d_array)}

        o_get = Get(parent=self.parent)
        strain_mapping = o_get.strain_mapping()
        strain_mapping_roi = strain_mapping[y0: y0 + (max_row_index * bin_size),
                                            x0: x0 + (max_col_index * bin_size)]
        self.parent.min_max[ParametersToDisplay.strain_mapping] = {'min': np.nanmin(strain_mapping_roi),
                                                                   'max': np.nanmax(strain_mapping_roi),
                                                                   'global_min': np.nanmin(strain_mapping_roi),
                                                                   'global_max': np.nanmax(strain_mapping_roi)}

        # self.parent.min_max[ParametersToDisplay.strain_mapping] = {'min': np.min(strain_mapping_roi),
        #                                                            'max': np.max(strain_mapping_roi),
        #                                                            'global_min': np.min(strain_mapping),
        #                                                            'global_max': np.max(strain_mapping)}
