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

from neutronbraggedge.material_handler.retrieve_material_metadata import RetrieveMaterialMetadata
from neutronbraggedge.braggedge import BraggEdge

class CustomAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return ['{:.4f}'.format(1./i) for i in values]
                
                
class Step1GuiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
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
        
    def init_gui(self):
        # define position and size
        rect = self.parent.geometry()
        self.parent.setGeometry(10, 10, rect.width(), rect.height())
        self.parent.ui.sample_ob_splitter.setSizes([850, 20])
        self.parent.ui.load_data_splitter.setSizes([200, 500])
        self.parent.ui.normalized_splitter.setSizes([150, 600])

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
        
    def get_element_selected(self):
        return str(self.parent.ui.list_of_elements.currentText())

    def set_crystal_structure(self, new_crystal_structure):
        nbr_item = self.parent.ui.crystal_structure.count()
        for _row in range(nbr_item):
            _item_of_row = self.parent.ui.crystal_structure.itemText(_row)
            if _item_of_row == new_crystal_structure:
                self.parent.ui.crystal_structure.setCurrentIndex(_row)
                self.parent.ui.crystal_structure_2.setCurrentIndex(_row)
       
    def update_lattice_and_crystal_when_index_selected(self):
        _handler = BraggEdge(material= self.get_element_selected())
        _crystal_structure = _handler.metadata['crystal_structure'][self.get_element_selected()]
        _lattice = str(_handler.metadata['lattice'][self.get_element_selected()])
        self.parent.ui.lattice_parameter.setText(_lattice)
        self.parent.ui.lattice_parameter_2.setText(_lattice)
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
                               base_widget):

        area = DockArea()
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
        roi = pg.ROI([0,0],[1,1])
        roi.addScaleHandle([1,1],[0,0])
        image_view.addItem(roi)
        roi.sigRegionChanged.connect(roi_function)
        d1.addWidget(image_view)
    
        # bragg edge plot
        bragg_edge_plot = pg.PlotWidget()
        bragg_edge_plot.plot()

#        bragg_edge_plot.setLabel("top", "")
        p1 = bragg_edge_plot.plotItem
        p1.layout.removeItem(p1.getAxis('top'))
        caxis = CustomAxis(orientation='top', parent=p1)
        caxis.setLabel('')
        caxis.linkToView(p1.vb)
        p1.layout.addItem(caxis, 1, 1)
        
        d2.addWidget(bragg_edge_plot)
    
        vertical_layout.addWidget(area)
        base_widget.setLayout(vertical_layout)
    
        return [image_view, roi, bragg_edge_plot, caxis]
                  

    def init_pyqtgraph(self):


        #sample
        [self.parent.ui.image_view, 
         self.parent.ui.image_view_roi, 
         self.parent.ui.bragg_edge_plot,
         self.parent.ui.caxis] = self.general_init_pyqtgrpah(self.parent.roi_image_view_changed,
                                    self.parent.ui.preview_widget)

        #ob
        [self.parent.ui.ob_image_view,
        self.parent.ui.ob_image_view_roi,
        self.parent.ui.ob_bragg_edge_plot,
        self.parent.ui.ob_caxis] = self.general_init_pyqtgrpah(self.parent.roi_ob_image_view_changed,
                                    self.parent.ui.ob_preview_widget)
        
        #normalized
        [self.parent.ui.normalized_image_view,
        self.parent.ui.normalized_image_view_roi,
        self.parent.ui.normalized_bragg_edge_plot,
        self.parent.ui.normalized_caxis] = self.general_init_pyqtgrpah(self.parent.roi_normalized_image_view_changed,
                                    self.parent.ui.normalized_preview_widget)


    def update_delta_lambda(self):
        distance_source_detector = float(str(self.parent.ui.distance_source_detector.text()))
        frequency = float(str(self.parent.ui.beam_rate.currentText()))
        
        delta_lambda = ibeatles.step1.math_utilities.calculate_delta_lambda(distance_source_detector = distance_source_detector,
                                                                            frequency = frequency)

        self.parent.ui.delta_lambda_value.setText("{:.2f}".format(delta_lambda))