import pyqtgraph as pg

from neutronbraggedge.braggedge import BraggEdge

from ..step1.plot import Step1Plot
from ..utilities.retrieve_data_infos import RetrieveGeneralFileInfos, RetrieveGeneralDataInfos
from ..step1.math_utilities import calculate_delta_lambda
from ..utilities.gui_handler import GuiHandler
from .. import DataType
from .roi import Roi


class CustomAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        if 0 in values:
            return []
        return ['{:.4f}'.format(1. / i) for i in values]


class Step1GuiHandler(object):

    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type

    def initialize_rois_and_labels(self):
        """Reached when ROIs have not been manually initialized but loaded via a session"""
        list_roi = self.parent.list_roi[self.data_type]

        roi_function = None
        if self.data_type == DataType.sample:
            roi_function = self.parent.roi_image_view_changed
            image_view = self.parent.ui.image_view
            method = self.parent.roi_image_view_changed
        elif self.data_type == DataType.ob:
            roi_function = self.parent.roi_ob_image_view_changed
            image_view = self.parent.ui.ob_image_view
            method = self.parent.roi_ob_image_view_changed
        elif self.data_type == DataType.normalized:
            roi_function = self.parent.roi_normalized_image_view_changed
            image_view = self.parent.ui.normalized_image_view
            method = self.parent.roi_normalized_image_view_changed

        already_existing_list_roi = self.parent.list_roi_id[self.data_type]
        already_existing_list_label_roi = self.parent.list_label_roi_id[self.data_type]
        for _roi_id, _label_id in zip(already_existing_list_roi, already_existing_list_label_roi):
            image_view.removeItem(_roi_id)
            image_view.removeItem(_label_id)

        list_roi_id = Roi.setup_roi_id(list_roi=list_roi, roi_function=roi_function)
        self.parent.list_roi_id[self.data_type] = list_roi_id

        list_label_roi_id = []

        for _roi, _roi_id in zip(list_roi, list_roi_id):
            label = _roi[0]
            x0 = int(_roi[1])
            y0 = int(_roi[2])

            # label roi
            label_roi = pg.TextItem(
                    html='<div style="text-align: center"><span style="color: #ff0000;">' + label + '</span></div>',
                    anchor=(-0.3, 1.3),
                    border='w',
                    fill=(0, 0, 255, 50))

            # # roi region in image
            # roi = pg.ROI([x0, y0], [width, height])
            # roi.addScaleHandle([1, 1], [0, 0])
            image_view.addItem(_roi_id)
            image_view.addItem(label_roi)
            label_roi.setPos(x0, y0)
            _roi_id.sigRegionChanged.connect(method)

            list_label_roi_id.append(label_roi)

        self.parent.list_label_roi_id[self.data_type] = list_label_roi_id

    def sync_instrument_widgets(self, source='load_data'):

        target = 'normalized'
        if source == 'normalized':
            target = 'load_data'

        list_ui = {'load_data': {'distance': self.parent.ui.distance_source_detector,
                                 'beam': self.parent.ui.beam_rate,
                                 'detector': self.parent.ui.detector_offset},
                   'normalized': {'distance': self.parent.ui.distance_source_detector_2,
                                  'beam': self.parent.ui.beam_rate_2,
                                  'detector': self.parent.ui.detector_offset_2}}

        o_gui = GuiHandler(parent=self.parent)
        distance_value = o_gui.get_text(ui=list_ui[source]['distance'])
        detector_value = o_gui.get_text(ui=list_ui[source]['detector'])
        beam_index = o_gui.get_index_selected(ui=list_ui[source]['beam'])

        o_gui.set_text(value=distance_value, ui=list_ui[target]['distance'])
        o_gui.set_text(value=detector_value, ui=list_ui[target]['detector'])
        o_gui.set_index_selected(index=beam_index, ui=list_ui[target]['beam'])

    def load_data_tab_changed(self, tab_index=0):
        data_type = 'sample'

        if tab_index == 0:
            # data_preview_box_label = "Sample Image Preview"
            o_general_infos = RetrieveGeneralFileInfos(parent=self.parent,
                                                       data_type='sample')
            o_selected_infos = RetrieveGeneralDataInfos(parent=self.parent,
                                                        data_type='sample')
        else:
            # data_preview_box_label = "Open Beam Image Preview"
            o_general_infos = RetrieveGeneralFileInfos(parent=self.parent,
                                                       data_type='ob')
            o_selected_infos = RetrieveGeneralDataInfos(parent=self.parent,
                                                        data_type='ob')
            data_type = 'ob'

        o_general_infos.update()
        o_selected_infos.update()

        row_selected = self.row_selected(data_type=data_type)
        data = self.parent.data_metadata[data_type]['data']
        if not data == []:
            data = data[row_selected]
        o_gui = Step1Plot(parent=self.parent,
                          data_type=data_type,
                          data=data)
        o_gui.all_plots()

    def row_selected(self, data_type='sample'):
        return self.parent.data_metadata[data_type]['list_widget_ui'].currentRow()

    def get_element_selected(self, source='load_data'):
        if source == 'load_data':
            return str(self.parent.ui.list_of_elements.currentText())
        else:
            return str(self.parent.ui.list_of_elements_2.currentText())

    def set_crystal_structure(self, new_crystal_structure):
        nbr_item = self.parent.ui.crystal_structure.count()
        for _row in range(nbr_item):
            _item_of_row = self.parent.ui.crystal_structure.itemText(_row)
            if _item_of_row == new_crystal_structure:
                self.parent.ui.crystal_structure.setCurrentIndex(_row)
                self.parent.ui.crystal_structure_2.setCurrentIndex(_row)

    def retrieve_handler_from_local_bragg_edge_list(self, material=None):
        '''
        Look if the material is in the local list of Bragg edge and if it is,
        return the dictionary of that material
        '''
        if material is None:
            return None

        _local_bragg_edge_list = self.parent.local_bragg_edge_list
        if material in _local_bragg_edge_list.keys():
            return _local_bragg_edge_list[material]

    def add_element_to_local_bragg_edge_list(self, material=None):
        '''
        Add a new material into the local bragg edge list
        new entry will be
        'material': {'crystal_structure': '', 'lattice': -1}
        '''
        if material is None:
            return None

        o_gui = GuiHandler(parent=self.parent)
        _crystal_structure = o_gui.get_text_selected(ui=self.parent.ui.crystal_structure)
        _lattice = o_gui.get_text(ui=self.parent.ui.lattice_parameter)

        self.parent.local_bragg_edge_list[material] = {'crystal_structure': _crystal_structure,
                                                       'lattice': _lattice}

    def update_lattice_and_crystal_when_index_selected(self, source='load_data',
                                                       fill_lattice_flag=True,
                                                       fill_crystal_structure_flag=True):
        _element = self.get_element_selected(source=source)
        try:
            _handler = BraggEdge(material=_element)
            _crystal_structure = _handler.metadata['crystal_structure'][_element]
            _lattice = str(_handler.metadata['lattice'][_element])

        except KeyError:

            # look for element in local list of element
            _handler = self.retrieve_handler_from_local_bragg_edge_list(material=_element)
            _crystal_structure = _handler['crystal_structure']
            _lattice = _handler['lattice']

        if source == 'load_data':
            _index = self.parent.ui.list_of_elements.currentIndex()
            self.parent.ui.list_of_elements_2.setCurrentIndex(_index)
        else:
            _index = self.parent.ui.list_of_elements_2.currentIndex()
            self.parent.ui.list_of_elements.setCurrentIndex(_index)

        if fill_lattice_flag:
            self.parent.ui.lattice_parameter.setText(_lattice)
            self.parent.ui.lattice_parameter_2.setText(_lattice)

        if fill_crystal_structure_flag:
            self.set_crystal_structure(_crystal_structure)

    def select_load_data_row(self, data_type='sample', row=0):
        if data_type == 'sample':
            self.parent.ui.list_sample.setCurrentRow(row)
        elif data_type == 'ob':
            self.parent.ui.list_open_beam.setCurrentRow(row)
        elif data_type == 'normalized':
            self.parent.ui.list_normalized.setCurrentRow(row)

    def update_delta_lambda(self):
        distance_source_detector = float(str(self.parent.ui.distance_source_detector.text()))
        frequency = float(str(self.parent.ui.beam_rate.currentText()))

        delta_lambda = calculate_delta_lambda(
            distance_source_detector=distance_source_detector,
            frequency=frequency)

        self.parent.ui.delta_lambda_value.setText("{:.2f}".format(delta_lambda))
        self.parent.ui.delta_lambda_value_2.setText("{:.2f}".format(delta_lambda))

    def check_step1_widgets(self):
        if self.parent.data_metadata[self.data_type]['data']:
            self.parent.ui.toolBox.setItemEnabled(1, True)
            self.parent.ui.tabWidget.setTabEnabled(1, True)

    def check_time_spectra_widgets(self):
        time_spectra_data = self.parent.data_metadata['time_spectra']['data']
        if self.parent.ui.material_display_checkbox.isChecked():
            if time_spectra_data == []:
                _display_error_label = True
            else:
                _display_error_label = False
        else:
            _display_error_label = False

        self.parent.ui.display_warning.setVisible(_display_error_label)

    def block_instrument_widgets(self, status=True):
        self.parent.ui.detector_offset.blockSignals(status)
        self.parent.ui.detector_offset_2.blockSignals(status)
        self.parent.ui.distance_source_detector.blockSignals(status)
        self.parent.ui.distance_source_detector_2.blockSignals(status)
        self.parent.ui.beam_rate.blockSignals(status)
        self.parent.ui.beam_rate_2.blockSignals(status)
