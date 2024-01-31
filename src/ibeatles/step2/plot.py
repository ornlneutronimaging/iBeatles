from qtpy.QtWidgets import QTableWidgetItem, QCheckBox, QComboBox, QWidget, QLabel, QHBoxLayout
from qtpy import QtGui
import numpy as np
import pyqtgraph as pg

from neutronbraggedge.experiment_handler.experiment import Experiment

from src.ibeatles import RegionType, DataType
from src.ibeatles.utilities.gui_handler import GuiHandler
from src.ibeatles.utilities.colors import pen_color
from src.ibeatles.utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities

from src.ibeatles.step2.get import Get as Step2Get
from src.ibeatles.step2 import roi_label_color


class CustomAxis(pg.AxisItem):

    def __init__(self, gui_parent, *args, **kwargs):
        pg.AxisItem.__init__(self, *args, **kwargs)
        self.parent = gui_parent

    def tickStrings(self, values, scale, spacing):
        strings = []

        _distance_source_detector = float(str(self.parent.ui.distance_source_detector.text()))
        _detector_offset_micros = float(str(self.parent.ui.detector_offset.text()))

        tof_s = [float(time) * 1e-6 for time in values]

        _exp = Experiment(tof=tof_s,
                          distance_source_detector_m=_distance_source_detector,
                          detector_offset_micros=_detector_offset_micros)
        lambda_array = _exp.lambda_array

        for _lambda in lambda_array:
            strings.append("{:.4f}".format(_lambda * 1e10))

        return strings


class Step2Plot:
    sample = []
    ob = []
    normalization = []

    def __init__(self, parent=None, sample=[], ob=[], normalized=[]):
        self.parent = parent
        self.sample = sample
        self.ob = ob
        self.normalized = normalized

    def prepare_data(self):
        if len(self.sample) == 0:
            sample = self.parent.data_metadata['sample']['data']

        # still no sample data
        if len(sample) == 0:
            return

        if len(self.ob) == 0:
            ob = self.parent.data_metadata['ob']['data']

        if len(self.normalized) == 0:
            normalized = self.parent.data_metadata['normalized']['data']

        if len(self.parent.data_metadata['normalization']['data']) == 0:
            normalization = np.mean(np.array(sample), axis=0)
            self.parent.data_metadata['normalization']['axis'] = normalization
            self.parent.data_metadata['normalization']['data'] = normalization
        else:
            normalization = self.parent.data_metadata['normalization']['data']

        self.sample = sample
        self.ob = ob
        self.normalization = normalization
        self.normalized = normalized

    def clear_image(self):
        self.parent.step2_ui['image_view'].clear()

    def clear_roi_from_image(self):
        list_roi_id = self.parent.list_roi_id['normalization']
        for roi_id in list_roi_id:
            self.parent.step2_ui['image_view'].removeItem(roi_id)

    def display_image(self):
        _data = self.normalization

        o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                    image_view=self.parent.step2_ui['image_view'],
                                    data_type=DataType.normalization)
        _state = o_pyqt.get_state()
        o_pyqt.save_histogram_level()

        if len(_data) == 0:
            self.clear_plots()
            self.parent.step2_ui['area'].setVisible(False)
        else:
            self.parent.step2_ui['area'].setVisible(True)
            self.parent.step2_ui['image_view'].setImage(_data)

        o_pyqt.set_state(_state)
        o_pyqt.reload_histogram_level()

    def display_roi(self):
        list_roi_id = self.parent.list_roi_id['normalization']
        list_label_roi_id = self.parent.list_label_roi_id['normalization']
        roi = self.parent.list_roi['normalization']

        if len(list_roi_id) == 0:
            return

        self.clear_roi_from_image()

        for index, roi_id in enumerate(list_roi_id):
            [_, x0, y0, width, height, region_type] = roi[index]

            x0 = int(x0)
            y0 = int(y0)

            roi_id.setPos([x0, y0], update=False, finish=False)
            roi_id.setSize([width, height], update=False, finish=False)

            _label_roi_id = list_label_roi_id[index]
            _label_roi_id.setPos(x0, y0)
            _label_roi_id.setHtml('<div style="text-align: center"><span style="color: '
                                     '#ff0000;">' + region_type + '</span></div>')

    def display_bragg_edge(self):

        def set_curve_point(text=RegionType.sample, parent_curve=None):
            curve_point = pg.CurvePoint(parent_curve)
            _plot_ui.addItem(curve_point)
            _text = pg.TextItem(text, anchor=(0.5, 0))
            _text.setParentItem(curve_point)
            arrow = pg.ArrowItem(angle=0)
            arrow.setParentItem(curve_point)
            curve_point.setPos(x_axis[-1])

        _plot_ui = self.parent.step2_ui['bragg_edge_plot']
        _plot_ui.clear()

        list_roi_id = self.parent.list_roi_id['normalization']
        # list_roi = self.parent.list_roi['normalization']

        o_get = Step2Get(parent=self.parent)
        list_sample_roi = []
        list_background_roi = []
        for _row_index, roi in enumerate(list_roi_id):

            [flag, x0, y0, width, height, region_type] = o_get.roi_table_row(row=_row_index)
            if flag is False:
                continue

            if region_type == RegionType.sample:
                list_sample_roi.append([x0, y0, width, height])
            else:
                list_background_roi.append([x0, y0, width, height])

        data_to_plot = self.extract_data_from_roi(list_sample_roi=list_sample_roi,
                                                  list_background_roi=list_background_roi)

        if data_to_plot is None:
            return

        if (not data_to_plot[RegionType.sample]) and (not data_to_plot[RegionType.background]):
            return

        o_gui = GuiHandler(parent=self.parent)
        xaxis_choice = o_gui.get_step2_xaxis_checked()
        if xaxis_choice == 'file_index':
            if data_to_plot[RegionType.sample]:
                x_axis = np.arange(len(data_to_plot[RegionType.sample]))
            else:
                x_axis = np.arange(len(data_to_plot[RegionType.background]))
            _plot_ui.setLabel("bottom", "File Index")

        elif xaxis_choice == 'tof':
            tof_array = self.parent.data_metadata['time_spectra']['data']
            tof_array = tof_array * 1e6
            _plot_ui.setLabel("bottom", u"TOF (\u00B5s)")
            x_axis = tof_array

        else:
            lambda_array = self.parent.data_metadata['time_spectra']['lambda']
            lambda_array = lambda_array * 1e10
            _plot_ui.setLabel("bottom", u'\u03BB (\u212B)')
            x_axis = lambda_array

        if data_to_plot[RegionType.sample]:
            # display the profile for the sample
            curve = _plot_ui.plot(x_axis,
                                  data_to_plot[RegionType.sample],
                                  symbolPen=None, pen=pen_color['0'],
                                  symbol='t',
                                  symbolSize=5)
            set_curve_point(text=RegionType.sample, parent_curve=curve)

        if data_to_plot[RegionType.background]:
            # display the profile for the background
            curve = _plot_ui.plot(x_axis,
                                  data_to_plot[RegionType.background],
                                  symbolPen=None, pen=pen_color['1'],
                                  symbol='t',
                                  symbolSize=5)
            set_curve_point(text=RegionType.background, parent_curve=curve)

    def extract_data_from_roi(self, list_sample_roi=None, list_background_roi=None):
        data_to_plot = {RegionType.sample: None,
                        RegionType.background: None}

        data = self.parent.data_metadata[DataType.sample]['data']

        if list_sample_roi:

            sample_y_profile = []
            for _index_data, _data in enumerate(data):

                total_counts = 0
                total_pixel = 0
                for _roi in list_sample_roi:
                    [x0, y0, width, height] = _roi

                    x0 = int(x0)
                    y0 = int(y0)
                    width = int(width)
                    height = int(height)

                    total_counts += np.sum(_data[x0:x0+width, y0:y0+height])
                    total_pixel += (width * height)

                sample_y_profile.append(total_counts/total_pixel)

            data_to_plot[RegionType.sample] = sample_y_profile

        if list_background_roi:

            background_y_profile = []
            for _data in data:

                total_counts = 0
                total_pixel = 0
                for _roi in list_background_roi:
                    [x0, y0, width, height] = _roi

                    x0 = int(x0)
                    y0 = int(y0)
                    width = int(width)
                    height = int(height)

                    total_counts += np.sum(_data[x0:x0 + width, y0:y0 + height])
                    total_pixel += (width * height)

                if total_pixel == 0:
                    return None

                background_y_profile.append(total_counts / total_pixel)

            data_to_plot[RegionType.background] = background_y_profile

        return data_to_plot

    def calculate_mean_counts(self, data, list_roi=None):
        if len(data) == 0:
            return data

        data = np.array(data)
        final_array = []
        _first_array_added = True
        nbr_roi = len(list_roi)

        if len(list_roi) == 0:
            final_array = np.mean(data, axis=(1, 2))

        else:
            for _index, _roi in enumerate(list_roi):
                [x0, y0, width, height] = _roi

                _x_from = int(x0)
                _x_to = _x_from + int(width) + 1

                _y_from = int(y0)
                _y_to = _y_from + int(height) + 1

                _mean = np.mean(data[:, _x_from: _x_to, _y_from: _y_to], axis=(1, 2))
                if _first_array_added:
                    final_array = _mean
                    _first_array_added = False
                else:
                    final_array += _mean

            final_array /= nbr_roi

        return final_array

    def init_roi_table(self):
        # clear table
        for _row in np.arange(self.parent.ui.normalization_tableWidget.rowCount()):
            self.parent.ui.normalization_tableWidget.removeRow(0)

        list_roi = self.parent.list_roi['normalization']
        self.parent.ui.normalization_tableWidget.blockSignals(True)
        for _row, _roi in enumerate(list_roi):
            self.parent.ui.normalization_tableWidget.insertRow(_row)
            self.set_row(_row, _roi)
        self.parent.ui.normalization_tableWidget.blockSignals(False)

    def update_label_roi(self):
        list_roi = self.parent.list_roi['normalization']
        list_label_roi_id = self.parent.list_label_roi_id['normalization']

        for _row, _roi in enumerate(list_roi):
            [status_row, x0, y0, width, height, region_type] = _roi
            x0 = int(x0)
            y0 = int(y0)
            _label_roi_id = list_label_roi_id[_row]
            _label_roi_id.setPos(x0, y0)
            _label_roi_id.setHtml(f'<div style="text-align: center"><span style="color: '
                                  f'{roi_label_color[region_type]};">' + region_type +
                                  '</span></div>')

    def check_error_in_roi_table(self):
        list_roi = self.parent.list_roi['normalization']

        for _row, _roi in enumerate(list_roi):
            [status_row, x0, y0, width, height, region_type] = _roi
            width = int(width)
            height = int(height)

            if (width == 0) or (height == 0):
                are_all_cells_ok = False
            else:
                are_all_cells_ok = True

            self._set_roi_row_background(are_all_cells_ok=are_all_cells_ok,
                                         row=_row)

    def _set_roi_row_background(self, are_all_cells_ok=True, row=0):
        if are_all_cells_ok:
            color = QtGui.QColor(255, 255, 255)
        else:
            color = QtGui.QColor(255, 0, 0)

        for _col in np.arange(1, 5):
            _item = self.parent.ui.normalization_tableWidget.item(row, _col)
            _item.setBackground(color)

    def update_roi_table(self):
        # if self.sample == []:
        #     return

        list_roi = self.parent.list_roi['normalization']
        for _row, _roi in enumerate(list_roi):
            self.update_row(_row, _roi)

    def get_item(self, text):
        _item = QTableWidgetItem(text)
        return _item

    def set_row(self, row_index, roi_array):

        # region type is either 'sample' or 'background'
        [status_row, x0, y0, width, height, region_type] = roi_array

        # button
        _widget = QCheckBox()
        _widget.setChecked(bool(status_row))
        self.parent.ui.normalization_tableWidget.setCellWidget(row_index, 0, _widget)
        self.parent.ui.normalization_tableWidget.blockSignals(True)

        # x0
        _item1 = self.get_item(str(x0))
        self.parent.ui.normalization_tableWidget.setItem(row_index, 1, _item1)

        # y0
        _item2 = self.get_item(str(y0))
        self.parent.ui.normalization_tableWidget.setItem(row_index, 2, _item2)

        # width
        _item3 = self.get_item(str(width))
        self.parent.ui.normalization_tableWidget.setItem(row_index, 3, _item3)

        # height
        _item4 = self.get_item(str(height))
        self.parent.ui.normalization_tableWidget.setItem(row_index, 4, _item4)

        _widget.stateChanged.connect(self.parent.normalization_row_status_changed)
        self.parent.ui.normalization_tableWidget.blockSignals(False)

        # region type
        _widget = QComboBox()
        _widget.addItems([RegionType.sample, RegionType.background])
        index = 0 if (region_type == RegionType.sample) else 1
        _widget.setCurrentIndex(index)
        _widget.currentIndexChanged.connect(self.parent.normalization_row_status_region_type_changed)
        self.parent.ui.normalization_tableWidget.setCellWidget(row_index, 5, _widget)

    def update_row(self, row_index, roi_array):
        [status_row, x0, y0, width, height, _] = roi_array

        # button
        _widget = self.parent.ui.normalization_tableWidget.cellWidget(row_index, 0)
        _widget.setChecked(bool(status_row))

        # x0
        _item = self.parent.ui.normalization_tableWidget.item(row_index, 1)
        _item.setText(str(x0))

        # y0
        _item = self.parent.ui.normalization_tableWidget.item(row_index, 2)
        _item.setText(str(y0))

        # width
        _item = self.parent.ui.normalization_tableWidget.item(row_index, 3)
        _item.setText(str(width))

        # height
        _item = self.parent.ui.normalization_tableWidget.item(row_index, 4)
        _item.setText(str(height))

    def clear_plots(self):
        self.parent.step2_ui['image_view'].clear()
        self.parent.step2_ui['bragg_edge_plot'].clear()
        # self.parent.step2_ui['normalized_profile_plot'].clear()

    def clear_counts_vs_file(self):
        self.parent.step2_ui['bragg_edge_plot'].clear()

    def multiply_array_by_coeff(self, data=None, coeff=None):
        if len(data) == len(coeff):
            return data * coeff
        else:
            return []
