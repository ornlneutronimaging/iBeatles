import numpy as np
import pyqtgraph as pg
from qtpy.QtGui import QBrush

from neutronbraggedge.experiment_handler.experiment import Experiment

from ibeatles import DataType, ScrollBarParameters, MATERIAL_BRAGG_PEAK_TO_DISPLAY_AT_THE_SAME_TIME, XAxisMode
import ibeatles.step1.utilities as utilities
from ibeatles.utilities.colors import pen_color, roi_group_color
from ibeatles.utilities.gui_handler import GuiHandler
from ibeatles.utilities.pyqrgraph import Pyqtgrah as PyqtgraphUtilities
from ibeatles.binning.binning_handler import BinningHandler
from ibeatles.fitting.fitting_handler import FittingHandler


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


class Step1Plot(object):
    data = []

    plot_ui = {DataType.sample: None,
               DataType.ob: None,
               DataType.normalized: None,
               'binning': None}

    def __init__(self, parent=None, data_type=None, data=[]):
        self.parent = parent

        if data_type is None:
            o_gui = GuiHandler(parent=parent)
            data_type = o_gui.get_active_tab()
        self.data_type = data_type

        if data == []:
            data = self.parent.data_metadata[data_type]['data']
        self.data = data

        self.plot_ui[DataType.sample] = self.parent.ui.bragg_edge_plot
        self.plot_ui[DataType.ob] = self.parent.ui.ob_bragg_edge_plot
        self.plot_ui[DataType.normalized] = self.parent.ui.normalized_bragg_edge_plot

    def all_plots(self):
        self.display_image()
        self.display_bragg_edge()

    def display_image(self, add_mean_radio_button_changed=False):
        """
        display the top right images + ROI boxes
        """

        _data = self.data
        _state = None
        self.parent.live_data = _data

        if _data == []:
            self.clear_plots(data_type=self.data_type)

        else:

            _data = np.array(_data)
            if self.data_type == DataType.sample:
                o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                            image_view=self.parent.ui.image_view,
                                            data_type=self.data_type,
                                            add_mean_radio_button_changed=add_mean_radio_button_changed)
                _state = o_pyqt.get_state()
                o_pyqt.save_histogram_level()

                self.parent.ui.area.setVisible(True)
                self.parent.ui.image_view.setImage(_data)
                self.add_origin_label(self.parent.ui.image_view)

                o_pyqt.set_state(_state)
                o_pyqt.reload_histogram_level()

            elif self.data_type == DataType.ob:
                o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                            image_view=self.parent.ui.ob_image_view,
                                            data_type=self.data_type,
                                            add_mean_radio_button_changed=add_mean_radio_button_changed)
                _state = o_pyqt.get_state()
                o_pyqt.save_histogram_level()
                self.parent.ui.ob_area.setVisible(True)
                self.parent.ui.ob_image_view.setImage(_data)
                self.add_origin_label(self.parent.ui.ob_image_view)
                o_pyqt.set_state(_state)
                o_pyqt.reload_histogram_level()

            elif self.data_type == DataType.normalized:
                o_pyqt = PyqtgraphUtilities(parent=self.parent,
                                            image_view=self.parent.ui.normalized_image_view,
                                            data_type=self.data_type,
                                            add_mean_radio_button_changed=add_mean_radio_button_changed)
                _state = o_pyqt.get_state()
                o_pyqt.save_histogram_level()
                self.parent.ui.normalized_area.setVisible(True)
                self.parent.ui.normalized_image_view.setImage(_data)
                self.add_origin_label(self.parent.ui.normalized_image_view)
                self.parent.data_metadata[DataType.normalized]['data_live_selection'] = _data
                o_pyqt.set_state(_state)
                o_pyqt.reload_histogram_level()

                # make sure that if we have the fitting window open, we have also at least the binning
                if not (self.parent.fitting_ui is None) and \
                        (self.parent.binning_ui is None):
                    self.parent.menu_view_binning_clicked()

                if not (self.parent.binning_ui is None):
                    o_binning = BinningHandler(parent=self.parent)
                    o_binning.display_image(data=_data)
                    self.parent.binning_ui.ui.groupBox.setEnabled(True)
                    self.parent.binning_ui.ui.groupBox_2.setEnabled(True)
                    self.parent.binning_ui.ui.left_widget.setVisible(True)
                if not (self.parent.fitting_ui is None):
                    o_fitting = FittingHandler(parent=self.parent)
                    o_fitting.display_image(data=_data)
                    o_fitting.display_roi()
                    self.parent.fitting_ui.ui.area.setVisible(True)
                    o_fitting.fill_table()
                if not (self.parent.rotate_ui is None):
                    o_rotate = self.parent.rotate_ui
                    o_rotate.display_rotated_images()

            self.parent.image_view_settings[self.data_type]['state'] = _state

    def initialize_default_roi(self):
        if self.data_type == DataType.sample:
            self.add_origin_roi(self.parent.ui.image_view, self.parent.ui.image_view_roi)
        elif self.data_type == DataType.ob:
            self.add_origin_roi(self.parent.ui.ob_image_view, self.parent.ui.ob_image_view_roi)
        elif self.data_type == DataType.normalized:
            self.add_origin_roi(self.parent.ui.normalized_image_view, self.parent.ui.normalized_image_view_roi)

    def add_origin_roi(self, image_view, roi_id):
        image_view.addItem(roi_id)
        self.parent.list_roi_id[self.data_type] = [roi_id]

    def add_origin_label(self, image_ui):
        # origin label
        text_id = pg.TextItem(html="<span style='color: yellow;'>(0,0)",
                              anchor=(1, 1))
        image_ui.addItem(text_id)
        text_id.setPos(-5, -5)

        # x and y arrows directions
        y_arrow = pg.ArrowItem(angle=-90, tipAngle=35, baseAngle=0,
                               headLen=20, tailLen=40, tailWidth=2, pen='y', brush=None)
        image_ui.addItem(y_arrow)
        y_arrow.setPos(0, 65)
        y_text = pg.TextItem(html="<span style='color: yellow;'>Y")
        image_ui.addItem(y_text)
        y_text.setPos(-30, 20)

        x_arrow = pg.ArrowItem(angle=180, tipAngle=35, baseAngle=0,
                               headLen=20, tailLen=40, tailWidth=2, pen='y', brush=None)
        image_ui.addItem(x_arrow)
        x_arrow.setPos(65, 0)
        x_text = pg.TextItem(html="<span style='color: yellow;'>X")
        image_ui.addItem(x_text)
        x_text.setPos(20, -30)

    def refresh_roi(self):
        pass

    def clear_image(self, data_type='sample'):
        if data_type == 'sample':
            self.parent.ui.image_view.clear()
        elif data_type == 'ob':
            self.parent.ui.ob_image_view.clear()
        elif data_type == 'normalized':
            self.parent.ui.normalized_image_view.clear()

    def clear_plots(self, data_type='sample'):
        if data_type == 'sample':
            self.parent.ui.image_view.clear()
            self.parent.ui.bragg_edge_plot.clear()
        elif data_type == 'ob':
            self.parent.ui.ob_image_view.clear()
            self.parent.ui.ob_bragg_edge_plot.clear()
        elif data_type == 'normalized':
            self.parent.ui.normalized_image_view.clear()
            self.parent.ui.normalized_bragg_edge_plot.clear()

    def display_general_bragg_edge(self, data_type=None):
        if data_type is None:
            o_gui = GuiHandler(parent=self.parent)
            data_type = o_gui.get_active_tab()

        data = self.parent.data_metadata[data_type]['data']
        self.data = data
        self.display_bragg_edge()

    def save_roi(self, label, x0, y0, x1, y1, group, data_type, index):
        _width = np.abs(x1 - x0)
        _height = np.abs(y1 - y0)

        _list_roi = self.parent.list_roi[data_type]
        if _list_roi == []:
            _label = "roi_label"
            _group = "0"
            _list_roi = [_label, str(x0), str(y0), str(_width), str(_height), _group]
            self.parent.list_roi[data_type] = [_list_roi]
        else:
            _label = label
            _group = group
            _list_roi = [_label, str(x0), str(y0), str(_width), str(_height), _group]
            self.parent.list_roi[data_type][index] = _list_roi

    def update_roi_editor(self, index):

        o_roi_editor = self.parent.roi_editor_ui[self.data_type]
        o_roi_editor.refresh(row=index)

        # o_roi = RoiHandler(parent=self.parent, data_type=self.data_type)
        # row_to_activate = o_roi.get_roi_index_that_changed()
        # o_roi_editor.activate_row(row_to_activate)

    def extract_data(self, list_data_group, data):
        list_data = {'0': [],
                     '1': [],
                     '2': [],
                     '3': []}

        for _group in list_data_group.keys():
            _list_roi = list_data_group[_group]
            if _list_roi == []:
                list_data[_group] = []
            else:
                for _data in data:
                    # nbr_roi = len(_list_roi)
                    _tmp_data = []
                    for _roi in _list_roi:
                        [x0, x1, y0, y1] = _roi

                        if self.parent.ui.roi_add_button.isChecked():
                            # _tmp_data.append(np.sum(_data[y0:y1, x0:x1]))
                            _tmp_data.append(np.nansum(_data[x0:x1, y0:y1]))
                        else:
                            # _tmp_data.append(np.mean(_data[y0:y1, x0:x1]))
                            _tmp_data.append(np.nanmean(_data[x0:x1, y0:y1]))

                    if self.parent.ui.roi_add_button.isChecked():
                        list_data[_group].append(np.nansum(_tmp_data))
                    else:
                        list_data[_group].append(np.mean(_tmp_data, axis=0))

        return list_data

    def get_row_parameters(self, roi_editor_ui, row):

        # # label
        _item = roi_editor_ui.tableWidget.item(row, 0)
        if _item is None:
            raise ValueError
        label = str(_item.text())

        # x0
        _item = roi_editor_ui.tableWidget.item(row, 1)
        if _item is None:
            raise ValueError
        x0 = int(str(_item.text()))

        # y0
        _item = roi_editor_ui.tableWidget.item(row, 2)
        if _item is None:
            raise ValueError
        y0 = int(str(_item.text()))

        # width
        _item = roi_editor_ui.tableWidget.item(row, 3)
        if _item is None:
            raise ValueError
        width = int(str(_item.text()))

        # height
        _item = roi_editor_ui.tableWidget.item(row, 4)
        if _item is None:
            raise ValueError
        height = int(str(_item.text()))

        # group
        _group_widget = roi_editor_ui.tableWidget.cellWidget(row, 5)
        if _group_widget is None:
            raise ValueError
        _index_selected = _group_widget.currentIndex()
        group = str(_index_selected)

        return [label, x0, y0, width, height, group]

    def clear_bragg_edge_plot(self):
        if self.data_type == 'sample':
            self.parent.ui.bragg_edge_plot.clear()
        elif self.data_type == 'ob':
            self.parent.ui.ob_bragg_edge_plot.clear()
        elif self.data_type == 'normalized':
            self.parent.ui.normalized_bragg_edge_plot.clear()

    def retrieve_list_data_group(self, mouse_selection=False):
        """
        this method looks at the current data_type and create a dictionary of the ROI selected
        for all the groups
        """

        list_roi_id = self.parent.list_roi_id[self.data_type]
        list_roi = self.parent.list_roi[self.data_type]

        # collect the right image_view and image_view_item to recover the ROI
        roi_editor_ui = self.parent.roi_editor_ui[self.data_type]
        if self.data_type == 'sample':
            _image_view = self.parent.ui.image_view
            _image_view_item = self.parent.ui.image_view.imageItem
        elif self.data_type == 'ob':
            _image_view = self.parent.ui.ob_image_view
            _image_view_item = self.parent.ui.ob_image_view.imageItem
        elif self.data_type == 'normalized':
            _image_view = self.parent.ui.normalized_image_view
            _image_view_item = self.parent.ui.normalized_image_view.imageItem

        # used here to group rois into their group for Bragg Edge plot
        list_data_group = {'0': [],
                           '1': [],
                           '2': [],
                           '3': []}

        for _index, roi in enumerate(list_roi_id):

            if mouse_selection:
                if type(self.parent.live_data) == type(list()):
                    self.parent.live_data = np.array(self.parent.live_data)

                try:
                    region = roi.getArraySlice(self.parent.live_data,
                                               _image_view_item)
                except IndexError:
                    return

                label = list_roi[_index][0]
                x0 = region[0][0].start
                x1 = region[0][0].stop - 1
                y0 = region[0][1].start
                y1 = region[0][1].stop - 1
                group = list_roi[_index][-1]

                if x1 == x0:
                    x1 += 1
                if y1 == y0:
                    y1 += 1

            else:
                if roi_editor_ui is None:
                    [label, x0, y0, w, h, group] = list_roi[_index]
                    x0 = int(x0)
                    y0 = int(y0)
                    w = int(w)
                    h = int(h)

                else:
                    try:
                        [label, x0, y0, w, h, group] = self.get_row_parameters(roi_editor_ui.ui,
                                                                               _index)
                    except ValueError:
                        return

                x1 = x0 + w
                y1 = y0 + h
                roi.setPos([x0, y0], update=False, finish=False)
                roi.setSize([w, h], update=False, finish=False)

            # display ROI boxes
            roi.setPen(pen_color[group])

            _text_array = self.parent.list_label_roi_id[self.data_type]
            if _text_array == []:
                text_id = pg.TextItem(
                    html='<div style="text-align: center"><span style="color: #ff0000;">' + label + '</span></div>',
                    anchor=(-0.3, 1.3),
                    border='w',
                    fill=(0, 0, 255, 50))
                _image_view.addItem(text_id)
                text_id.setPos(x0, y0)
                self.parent.list_label_roi_id[self.data_type].append(text_id)
            else:
                text_id = self.parent.list_label_roi_id[self.data_type][_index]
                # text_id.setText(label)
                text_id.setPos(x0, y0)
                text_id.setHtml('<div style="text-align: center"><span style="color: #ff0000;">' + label + ' \
                                                                                              ''</span></div>')

            list_data_group[group].append([x0, x1, y0, y1])

            self.save_roi(label, x0, y0, x1, y1, group, self.data_type, _index)

            if mouse_selection:
                if not (roi_editor_ui is None):
                    roi_editor_ui.ui.tableWidget.blockSignals(True)
                    self.update_roi_editor(_index)
                    roi_editor_ui.ui.tableWidget.blockSignals(False)

            return list_data_group

    def display_bragg_edge(self, mouse_selection=True):
        """
        Display the bottom right plot showing the bragg edges and the position of the material bragg peaks
        """

        _data = self.data

        if _data == []:  # clear data if no data
            self.clear_bragg_edge_plot()

        else:  # retrieve dictionaries of roi_id and roi data (label, x, y, w, h, group)

            list_data_group = self.retrieve_list_data_group(mouse_selection=mouse_selection)

            # work over groups
            data = self.parent.data_metadata[self.data_type]['data']
            bragg_edges = self.extract_data(list_data_group,
                                            data)

            # check if xaxis can be in lambda, or tof

            if self.data_type in [DataType.sample, DataType.ob]:
                time_spectra_file = self.parent.data_metadata[DataType.sample]['time_spectra']['filename']
            else:
                time_spectra_file = self.parent.data_metadata[self.data_type]['time_spectra']['filename']
            o_gui = GuiHandler(parent=self.parent)

            if time_spectra_file == "":
                o_gui.enable_xaxis_button(tof_flag=False)
                tof_array = []
                lambda_array = []

            else:
                o_gui.enable_xaxis_button(tof_flag=True)

                if self.data_type == 'normalized':
                    tof_array = self.parent.data_metadata['time_spectra']['normalized_data']
                    lambda_array = self.parent.data_metadata['time_spectra']['normalized_lambda']
                else:
                    tof_array = self.parent.data_metadata['time_spectra']['data']
                    lambda_array = self.parent.data_metadata['time_spectra']['lambda']
                    self.parent.normalized_lambda_bragg_edge_x_axis = lambda_array * 1e10

            # display of bottom bragg edge plot
            dictionary = self.plot_bragg_edge(tof_array=tof_array,
                                              lambda_array=lambda_array,
                                              bragg_edges=bragg_edges)

            x_axis = dictionary['x_axis']
            [linear_region_left, linear_region_right] = dictionary['linear_region']
            o_gui.xaxis_label()

            lr = pg.LinearRegionItem([linear_region_left, linear_region_right])
            lr.setZValue(-10)

            if self.data_type == 'sample':
                self.parent.ui.bragg_edge_plot.addItem(lr)
            elif self.data_type == 'ob':
                self.parent.ui.ob_bragg_edge_plot.addItem(lr)
            else:
                self.parent.ui.normalized_bragg_edge_plot.addItem(lr)
                self.parent.fitting_bragg_edge_x_axis = x_axis

            lr.sigRegionChangeFinished.connect(self.parent.bragg_edge_selection_changed)
            self.parent.list_bragg_edge_selection_id[self.data_type] = lr
            self.parent.current_bragg_edge_x_axis[self.data_type] = x_axis

    def plot_bragg_edge(self, tof_array=[], lambda_array=[], bragg_edges=[]):
        """
        plot the bragg edges
        """
        data_type = self.data_type
        plot_ui = self.plot_ui[data_type]
        plot_ui.clear()

        list_files_selected = self.parent.list_file_selected[self.data_type]
        linear_region_left_index = int(list_files_selected[0])
        linear_region_right_index = int(list_files_selected[-1])
        linear_region_left = linear_region_left_index
        linear_region_right = linear_region_right_index

        x_axis = []
        plot_ui.setLabel("left", "Total Counts")

        _symbol = 't'

        # use to check if bragg peaks scroll bar should be visible or not
        o_gui = GuiHandler(parent=self.parent)

        if tof_array == []:

            plot_ui.setLabel('bottom', 'File Index')

            for _key in bragg_edges.keys():
                _bragg_edge = bragg_edges[_key]
                if _bragg_edge == []:
                    continue
                curve = plot_ui.plot(_bragg_edge, symbolPen=None, pen=pen_color[_key], symbol=_symbol, symbolSize=5)
                x_axis = np.arange(len(_bragg_edge))

                curvePoint = pg.CurvePoint(curve)
                plot_ui.addItem(curvePoint)
                _text = pg.TextItem("Group {}".format(_key), anchor=(0.5, 0))
                _text.setParentItem(curvePoint)
                brush = QBrush()
                brush.setColor(roi_group_color[int(_key)])
                arrow = pg.ArrowItem(angle=0, brush=brush)
                arrow.setParentItem(curvePoint)
                curvePoint.setPos(x_axis[-1])

            o_gui.update_bragg_peak_scrollbar(force_hide_widgets=True)

        else:

            tof_array = tof_array * 1e6

            xaxis_choice = o_gui.get_xaxis_checked(data_type=self.data_type)
            o_gui.update_bragg_peak_scrollbar(xaxis_mode=xaxis_choice)

            first_index = True

            for _key in bragg_edges.keys():
                _bragg_edge = bragg_edges[_key]
                if _bragg_edge == []:
                    continue

                if xaxis_choice == 'file_index':
                    curve = plot_ui.plot(_bragg_edge, pen=pen_color[_key],
                                         symbolPen=None,
                                         symbolSize=5,
                                         symbol=_symbol)
                    x_axis = np.arange(len(_bragg_edge))

                elif xaxis_choice == 'tof':

                    curve = plot_ui.plot(tof_array, _bragg_edge,
                                         pen=pen_color[_key],
                                         symbolPen=None,
                                         symbolSize=5,
                                         symbol=_symbol)
                    x_axis = tof_array
                    linear_region_left = tof_array[linear_region_left_index]
                    linear_region_right = tof_array[linear_region_right_index]

                else:  # lambda

                    if first_index:
                        lambda_array = lambda_array * 1e10

                    curve = plot_ui.plot(lambda_array, _bragg_edge,
                                         pen=pen_color[_key],
                                         symbolPen=None,
                                         symbolSize=5,
                                         )
                    x_axis = lambda_array

                    linear_region_left = lambda_array[linear_region_left_index]
                    linear_region_right = lambda_array[linear_region_right_index]

                    if first_index:
                        self.display_selected_element_bragg_edges(plot_ui=plot_ui,
                                                                  lambda_range=[lambda_array[0], lambda_array[-1]],
                                                                  ymax=np.nanmax(_bragg_edge))
                        first_index = False

                curvePoint = pg.CurvePoint(curve)
                plot_ui.addItem(curvePoint)
                _text = pg.TextItem("Group {}".format(_key),
                                    anchor=(0.5, 0),
                                    color=pen_color[_key])
                _text.setParentItem(curvePoint)
                brush = QBrush()
                brush.setColor(roi_group_color[int(_key)])
                arrow = pg.ArrowItem(angle=0, brush=brush)
                arrow.setParentItem(curvePoint)

                if xaxis_choice == 'lambda':
                    last_position = x_axis[-1]
                else:
                    last_position = x_axis[-1]

                curvePoint.setPos(last_position)

        return {'x_axis': x_axis,
                'linear_region': [linear_region_left, linear_region_right]}

    def display_selected_element_bragg_edges(self, plot_ui=plot_ui, lambda_range=None, ymax=0):

        display_flag = self.parent.ui.material_display_checkbox.isChecked()
        if not display_flag:
            return

        _selected_element_bragg_edges_array = self.parent.selected_element_bragg_edges_array
        _selected_element_hkl_array = self.parent.selected_element_hkl_array

        # nbr_hkl_in_list = len(_selected_element_bragg_edges_array)
        # nbr_to_display_at_the_same_time = 4

        hkl_scrollbar_ui = self.parent.hkl_scrollbar_ui['widget'][self.data_type]
        max_value = self.parent.hkl_scrollbar_dict[ScrollBarParameters.maximum]
        hkl_scrollbar_ui.setMaximum(max_value)
        current_value = self.parent.hkl_scrollbar_dict[ScrollBarParameters.value]
        hkl_scrollbar_ui.setValue(current_value)

        list_to_display = np.arange(max_value - current_value, max_value - current_value +
                                    MATERIAL_BRAGG_PEAK_TO_DISPLAY_AT_THE_SAME_TIME)

        # # no need to enabled the scrollbar if the total number of hkl is smaller than the minimum to display
        # scollbar_max = nbr_hkl_in_list - 1 - nbr_to_display_at_the_same_time
        # if scollbar_max < nbr_to_display_at_the_same_time:
        #     hkl_scrollbar_ui.setEnabled(False)
        # else:
        #     hkl_scrollbar_ui.setEnabled(True)
        #
        # hkl_scrollbar_ui.setMinimum(0)
        # hkl_scrollbar_ui.setMaximum(nbr_hkl_in_list-1-nbr_to_display_at_the_same_time)
        # hkl_scrollbar_ui.setValue(nbr_hkl_in_list-1)
        # current_value = hkl_scrollbar_ui.value()
        # list_to_display = np.arange(current_value, current_value + nbr_to_display_at_the_same_time)

        for _index, _x in enumerate(_selected_element_bragg_edges_array):
            # if (_x >= lambda_range[0]) and (_x <= lambda_range[1]):

            if _x is None:
                continue

            _x = float(_x)

            if _index in list_to_display:

                # vertical line
                _item = pg.InfiniteLine(_x, pen=pg.mkPen("c"))
                plot_ui.addItem(_item)

                # label of line
                _hkl = _selected_element_hkl_array[_index]
                _hkl_formated = "{},{},{}".format(_hkl[0], _hkl[1], _hkl[2])
                _text = pg.TextItem(_hkl_formated,
                                    anchor=(0, 1),
                                    angle=45,
                                    color=pg.mkColor("c"))
                _text.setPos(_x, ymax)
                plot_ui.addItem(_text)
