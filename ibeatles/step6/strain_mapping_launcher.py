try:
    import PyQt4
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QMainWindow
    from PyQt4.QtGui import QApplication         
except:
    import PyQt5
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QApplication

from pyqtgraph.dockarea import *
import pyqtgraph as pg
import numpy as np
    
from ibeatles.interfaces.ui_strainMapping import Ui_MainWindow as UiMainWindow

class StrainMappingLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.strain_mapping_ui == None:
            strain_mapping_window = StrainMappingWindow(parent=parent)
            strain_mapping_window.show()
            self.parent.strain_mapping_ui = strain_mapping_window
        else:
            self.parent.strain_mapping_ui.setFocus()
            self.parent.strain_mapping_ui.activateWindow()
            
class StrainMappingWindow(QMainWindow):        
    
    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("6. Strain Mapping")

        self.init_pyqtgraph()
        self.init_labels()
        #self.init_widgets()
        self.display_images_and_selection()
        
    def display_images_and_selection(self):
        
        _data = self.parent.data_metadata['normalized']['data_live_selection']
        if not _data == []:
            self.ui.strain_mapping_image.setImage(_data)
            self.ui.sigma_image.setImage(_data)
            self.ui.alpha_image.setImage(_data)

    def set_tab_widgets(self):
        image_view = pg.ImageView()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        #self.parent.binning_line_view['image_view'] = image_view
    
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(image_view)
        
        return {'layout': vertical_layout,
                'image_view': image_view}

    def init_pyqtgraph(self):
        
        pg.setConfigOptions(antialias=True)
        
        #tab1
        _dict = self.set_tab_widgets()
        self.ui.strain_mapping_image = _dict['image_view']
        self.ui.strain_mapping_tab.setLayout(_dict['layout'])
        
        #tab2
        _dict = self.set_tab_widgets()
        self.ui.sigma_image = _dict['image_view']
        self.ui.sigma_tab.setLayout(_dict['layout'])

        #tab1
        _dict = self.set_tab_widgets()
        self.ui.alpha_image = _dict['image_view']
        self.ui.alpha_tab.setLayout(_dict['layout'])

    def init_labels(self):
        self.ui.d0_label.setText(u"d<sub>0</sub>")
        self.ui.d0_units_label.setText(u"\u212B")

    def closeEvent(self, event=None):
        if self.parent.strain_mapping_ui:
            self.parent.strain_mapping_ui.close()
        self.parent.strain_mapping_ui = None
    