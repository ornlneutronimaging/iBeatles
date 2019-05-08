try:
    import PyQt4
    import PyQt4.QtCore as QtCore
    import PyQt4.QtGui as QtGui
except:
    import PyQt5
    import PyQt5.QtCore as QtCore
    import PyQt5.QtGui as QtGui

import pyqtgraph as pg
from pyqtgraph.dockarea import *

from ibeatles.step1.plot import Step1Plot
from ibeatles.utilities.retrieve_data_infos import RetrieveGeneralFileInfos, RetrieveSelectedFileDataInfos
import ibeatles.step1.math_utilities
from ibeatles.utilities.colors import pen_color
from ibeatles.utilities.gui_handler import GuiHandler

from neutronbraggedge.material_handler.retrieve_material_metadata import RetrieveMaterialMetadata
from neutronbraggedge.braggedge import BraggEdge

class CustomAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        if 0 in values:
            return []
        return ['{:.4f}'.format(1./i) for i in values]
                
class Step1GuiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def sync_instrument_widgets(self, source='load_data'):
        
        target = 'normalized'
        if source == 'normalized':
            target = 'load_data'
        
        list_ui = {'load_data' : {'distance': self.parent.ui.distance_source_detector,
                                  'beam': self.parent.ui.beam_rate,
                                  'detector': self.parent.ui.detector_offset},
                   'normalized': {'distance': self.parent.ui.distance_source_detector_2,
                                  'beam': self.parent.ui.beam_rate_2,
                                  'detector': self.parent.ui.detector_offset_2}}
        
        o_gui = GuiHandler(parent = self.parent)    
        distance_value = o_gui.get_text(ui = list_ui[source]['distance'])
        detector_value = o_gui.get_text(ui = list_ui[source]['detector'])
        beam_index = o_gui.get_index_selected(ui = list_ui[source]['beam'])

        o_gui.set_text(value = distance_value, ui = list_ui[target]['distance'])
        o_gui.set_text(value = detector_value, ui = list_ui[target]['detector'])
        o_gui.set_index_selected(index = beam_index, ui = list_ui[target]['beam'])


    def load_data_tab_changed(self, tab_index=0):
        data_type = 'sample'
        
        if tab_index == 0:
            data_preview_box_label = "Sample Image Preview"
            o_general_infos = RetrieveGeneralFileInfos(parent = self.parent, 
                                                       data_type = 'sample')
            o_selected_infos = RetrieveSelectedFileDataInfos(parent = self.parent,
                                                                  data_type = 'sample')
        else:
            data_preview_box_label = "Open Beam Image Preview"
            o_general_infos = RetrieveGeneralFileInfos(parent = self.parent, 
                                                       data_type = 'ob')
            o_selected_infos = RetrieveSelectedFileDataInfos(parent = self.parent,
                                                                  data_type = 'ob')
            data_type = 'ob'
        
        o_general_infos.update()            
        o_selected_infos.update()

        row_selected = self.row_selected(data_type=data_type)
        data = self.parent.data_metadata[data_type]['data']
        if not data == []:
            data = data[row_selected]
        o_gui = Step1Plot(parent = self.parent, 
                          data_type = data_type,
                          data = data)
        o_gui.all_plots()
        
    def row_selected(self, data_type='sample'):
        return self.parent.data_metadata[data_type]['list_widget_ui'].currentRow()
        
    def init_statusbar(self):
        self.parent.eventProgress = QtGui.QProgressBar(self.parent.ui.statusbar)
        self.parent.eventProgress.setMinimumSize(20, 14)
        self.parent.eventProgress.setMaximumSize(540, 100)
        self.parent.eventProgress.setVisible(False)
        self.parent.ui.statusbar.addPermanentWidget(self.parent.eventProgress)
        
        self.parent.setStyleSheet("QStatusBar{padding-left:8px;color:red;font-weight:bold;}")
#        self.parent.ui.statusbar.showMessage("this is an error", 2000)
        
    def init_gui(self):
        # define position and size
        rect = self.parent.geometry()
        self.parent.setGeometry(10, 10, rect.width(), rect.height())
        self.parent.ui.sample_ob_splitter.setSizes([850, 20])
        self.parent.ui.load_data_splitter.setSizes([200, 500])
        self.parent.ui.normalized_splitter.setSizes([150, 600])
        
        # reset buttons
        icon = QtGui.QIcon(":/MPL Toolbar/reset_icon.png")
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

    def init_material_widgets(self):
        retrieve_material = RetrieveMaterialMetadata(material = 'all')
        list_returned = retrieve_material.full_list_material()
        self.parent.ui.list_of_elements.addItems(list_returned)
        self.parent.ui.list_of_elements_2.addItems(list_returned)
        
        _handler = BraggEdge(material= self.get_element_selected())
        _crystal_structure = _handler.metadata['crystal_structure'][self.get_element_selected()]
        _lattice = str(_handler.metadata['lattice'][self.get_element_selected()])
        self.parent.ui.lattice_parameter.setText(_lattice)
        self.parent.ui.lattice_parameter_2.setText(_lattice)
        self.set_crystal_structure(_crystal_structure)
        
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

        o_gui = GuiHandler(parent = self.parent)
        _crystal_structure = o_gui.get_text_selected(ui = self.parent.ui.crystal_structure)
        _lattice = o_gui.get_text(ui = self.parent.ui.lattice_parameter)
        
        self.parent.local_bragg_edge_list[material] = {'crystal_structure': _crystal_structure,
                                                       'lattice': _lattice}
        
    def update_lattice_and_crystal_when_index_selected(self, source='load_data', 
                                                       fill_lattice_flag=True, 
                                                       fill_crystal_structure_flag=True):
        _element = self.get_element_selected(source=source)
        try:
            _handler = BraggEdge(material = _element)
            _crystal_structure = _handler.metadata['crystal_structure'][_element]
            _lattice = str(_handler.metadata['lattice'][_element])

        except KeyError:

            # look for element in local list of element
            _handler = self.retrieve_handler_from_local_bragg_edge_list(material = _element)
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
        
    def init_labels(self):
        #micross
        self.parent.ui.micro_s.setText(u"\u00B5s")
        self.parent.ui.micro_s_2.setText(u"\u00B5s")
        #distance source detector
        self.parent.ui.distance_source_detector_label.setText("d<sub> source-detector</sub>")
        self.parent.ui.distance_source_detector_label_2.setText("d<sub> source-detector</sub>")
        #delta lambda
        self.parent.ui.delta_lambda_label.setText(u"\u0394\u03BB:")
        self.parent.ui.delta_lambda_label_2.setText(u"\u0394\u03BB:")
        #Angstroms
        self.parent.ui.angstroms_label.setText(u"\u212B")
        self.parent.ui.angstroms_label_2.setText(u"\u212B")

    def select_load_data_row(self, data_type='sample', row=0):
        if data_type == 'sample':
            self.parent.ui.list_sample.setCurrentRow(row)
        else:
            self.parent.ui.list_open_beam.setCurrentRow(row)
            
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
        pg.setConfigOptions(antialias=True) # this improve display
    
        vertical_layout = QtGui.QVBoxLayout()
        preview_widget.setLayout(vertical_layout)
        
        # image view
        image_view = pg.ImageView()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        roi = pg.ROI([0,0],[20,20], pen=pen_color['0'], scaleSnap=True)
        roi.addScaleHandle([1,1],[0,0])
        image_view.addItem(roi)
        roi.sigRegionChanged.connect(roi_function)

        roi_editor_button = QtGui.QPushButton("ROI editor ...")
        roi_editor_button.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        # self.parent.connect(roi_editor_button, QtCore.SIGNAL("clicked()"), self.parent.roi_editor_button)
        roi_editor_button.pressed.connect(self.parent.roi_editor_button_clicked)
        line_layout = QtGui.QHBoxLayout()
        line_layout.addWidget(roi_editor_button)

        add_button = QtGui.QRadioButton()
        add_button.setText("Add")
        add_button.setChecked(True)
        # self.parent.connect(add_button, QtCore.SIGNAL("clicked()"), add_function)
        add_button.pressed.connect(add_function)
        line_layout.addWidget(add_button)
        
        mean_button = QtGui.QRadioButton()
        mean_button.setText("Mean")
        mean_button.setChecked(False)
        # self.parent.connect(mean_button, QtCore.SIGNAL("clicked()"), mean_function)
        mean_button.pressed.connect(mean_function)
        line_layout.addWidget(mean_button)

        top_widget = QtGui.QWidget()
        top_widget.setLayout(line_layout)

        top_right_widget = QtGui.QWidget()
        vertical = QtGui.QVBoxLayout()
        vertical.addWidget(top_widget)

        vertical.addWidget(image_view)
        top_right_widget.setLayout(vertical)
        d1.addWidget(top_right_widget)
    
        # bragg edge plot
        bragg_edge_plot = pg.PlotWidget(title='')
        bragg_edge_plot.plot()

        #bragg_edge_plot.setLabel("top", "")
        #p1 = bragg_edge_plot.plotItem
        #p1.layout.removeItem(p1.getAxis('top'))
        #caxis = CustomAxis(orientation='top', parent=p1)
        #caxis.setLabel('')
        #caxis.linkToView(p1.vb)
        #p1.layout.addItem(caxis, 1, 1)
        caxis = None
        
        #add file_index, TOF, Lambda x-axis buttons
        hori_layout = QtGui.QHBoxLayout()
        button_widgets = QtGui.QWidget()
        button_widgets.setLayout(hori_layout)
        
        #file index
        file_index_button = QtGui.QRadioButton()
        file_index_button.setText("File Index")
        file_index_button.setChecked(True)
        # self.parent.connect(file_index_button, QtCore.SIGNAL("clicked()"), file_index_function)
        file_index_button.pressed.connect(file_index_function)

        #tof
        tof_button = QtGui.QRadioButton()
        tof_button.setText("TOF")
        # self.parent.connect(tof_button, QtCore.SIGNAL("clicked()"), tof_function)
        tof_button.pressed.connect(tof_function)

        #lambda
        lambda_button = QtGui.QRadioButton()
        lambda_button.setText(u"\u03BB")
        # self.parent.connect(lambda_button, QtCore.SIGNAL("clicked()"), lambda_function)
        lambda_button.pressed.connect(lambda_function)

        spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        hori_layout.addItem(spacer)
        hori_layout.addWidget(file_index_button)
        hori_layout.addWidget(tof_button)
        hori_layout.addWidget(lambda_button)
        hori_layout.addItem(spacer)

        d2.addWidget(bragg_edge_plot)
        d2.addWidget(button_widgets)
    
        vertical_layout.addWidget(area)
        base_widget.setLayout(vertical_layout)
    
        return [area, image_view, roi, bragg_edge_plot, 
                caxis, roi_editor_button, add_button, mean_button, 
                file_index_button, tof_button, lambda_button]
                  
    def init_pyqtgraph(self):

        #sample
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

        #ob
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
        
        #normalized
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

    def update_delta_lambda(self):
        distance_source_detector = float(str(self.parent.ui.distance_source_detector.text()))
        frequency = float(str(self.parent.ui.beam_rate.currentText()))
        
        delta_lambda = ibeatles.step1.math_utilities.calculate_delta_lambda(distance_source_detector = distance_source_detector,
                                                                            frequency = frequency)

        self.parent.ui.delta_lambda_value.setText("{:.2f}".format(delta_lambda))
        self.parent.ui.delta_lambda_value_2.setText("{:.2f}".format(delta_lambda))
        
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
        
    def connect_widgets(self):
        # self.parent.connect(self.parent.ui.list_of_elements, QtCore.SIGNAL("currentIndexChanged(int)"), self.parent.list_of_element_index_changed)
        self.parent.ui.list_of_elements.currentIndexChanged.connect(self.parent.list_of_element_index_changed)
        # self.parent.connect(self.parent.ui.list_of_elements_2, QtCore.SIGNAL("currentIndexChanged(int)"), self.parent.list_of_element_2_index_changed)
        self.parent.ui.list_of_elements_2.currentIndexChanged.connect(self.parent.list_of_element_2_index_changed)
