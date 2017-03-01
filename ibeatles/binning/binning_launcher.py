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
    
from ibeatles.interfaces.ui_binningWindow import Ui_MainWindow as UiMainWindow
from ibeatles.utilities import colors

from ibeatles.table_dictionary.table_dictionary_handler import TableDictionaryHandler
from ibeatles.fitting.fitting_handler import FittingHandler
from ibeatles.fitting.filling_table_handler import FillingTableHandler
from ibeatles.binning.binning_handler import BinningHandler


class BinningLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.binning_ui == None:
            binning_window = BinningWindow(parent=parent)
            binning_window.show()
            self.parent.binning_ui = binning_window
            o_binning = BinningHandler(parent=self.parent)
            o_binning.display_image()
#            o_binning.display_selection()
        else:
            self.parent.binning_ui.setFocus()
            self.parent.binning_ui.activateWindow()

class BinningWindow(QMainWindow):        

    default_bins_settings = {'x0': 0,
                             'y0': 0,
                             'width': 20,
                             'height': 20,
                             'bin_size': 10}
    
    image_view = None
    line_view = None
    data = []
    widgets_ui = {'x_value': None,
                  'y_value': None,
                  'intensity_value': None,
                  'roi': None}

    def __init__(self, parent=None):
        
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = UiMainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("4. Binning")
               
        self.load_data()
        self.init_pyqtgraph() 
        self.init_widgets()
        self.roi_selection_widgets_modified()
        
    def load_data(self):
        self.data = np.array(self.parent.data_metadata['normalized']['data_live_selection'])
        
    def init_widgets(self):
        if self.parent.binning_roi:
            [x0, y0, width, height, bin_size] = self.parent.binning_roi
            self.ui.selection_x0.setText(str(x0))
            self.ui.selection_y0.setText(str(y0))
            self.ui.selection_width.setText(str(width))
            self.ui.selection_height.setText(str(height))
            self.ui.pixel_bin_size.setText(str(bin_size))

    def roi_changed_finished(self):
        self.roi_selection_widgets_modified()        
        
    def roi_changed(self):

        if self.parent.binning_line_view['ui']:
            _image_view = self.parent.binning_line_view['image_view']
            _image_view.removeItem(self.parent.binning_line_view['ui'])
            self.parent.binning_line_view['ui'] = None
        else:
            _image_view = self.parent.binning_line_view['image_view']
        
        roi = self.parent.binning_line_view['roi']
        if len(self.data) == 0:
            return
        region = roi.getArraySlice(self.data, _image_view.imageItem)
        
        x0 = region[0][0].start
        x1 = region[0][0].stop-1
        y0 = region[0][1].start
        y1 = region[0][1].stop-1
        
        width = np.abs(x0-x1)
        height = np.abs(y0-y1)
                            
        self.ui.selection_x0.setText("{}".format(x0))
        self.ui.selection_y0.setText("{}".format(y0))
        self.ui.selection_width.setText("{}".format(width))
        self.ui.selection_height.setText("{}".format(height))

    def init_pyqtgraph(self):

        if len(self.data) == 0:
            status = False
        else:
            status = True
        
        self.ui.groupBox.setEnabled(status)
        self.ui.groupBox_2.setEnabled(status)
        
        pg.setConfigOptions(antialias=True)
        
        image_view = pg.ImageView()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        self.parent.binning_line_view['image_view'] = image_view
        roi = pg.ROI([0,0], [20, 20], pen=colors.pen_color['0'], scaleSnap=True)
        roi.addScaleHandle([1,1], [0,0])
        roi.sigRegionChanged.connect(self.roi_changed)
        roi.sigRegionChangeFinished.connect(self.roi_changed_finished)
        self.parent.binning_line_view['roi'] = roi
        image_view.addItem(roi)
        line_view = pg.GraphItem()
        image_view.addItem(line_view)
        self.parent.binning_line_view['ui'] = line_view

        # bottom x, y and counts labels
        hori_layout = QtGui.QHBoxLayout()
        spacer1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        x_label = QtGui.QLabel("X:")
        x_value = QtGui.QLabel("N/A")
        x_value.setFixedWidth(50)
        self.widgets_ui['x_value'] = x_value
        spacer2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        y_label = QtGui.QLabel("Y:")
        y_value = QtGui.QLabel("N/A")
        y_value.setFixedWidth(50)
        self.widgets_ui['y_value'] = y_value
        spacer3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        intensity_label = QtGui.QLabel("Counts:")
        intensity_value = QtGui.QLabel("N/A")
        self.widgets_ui['intensity_value'] = intensity_value
        intensity_value.setFixedWidth(50)

        hori_layout.addItem(spacer1)
        hori_layout.addWidget(x_label)
        hori_layout.addWidget(x_value)
        hori_layout.addItem(spacer2)
        hori_layout.addWidget(y_label)
        hori_layout.addWidget(y_value)
        hori_layout.addItem(spacer3)
        hori_layout.addWidget(intensity_label)
        hori_layout.addWidget(intensity_value)
        hori_widget = QtGui.QWidget()
        hori_widget.setLayout(hori_layout)
        
        # put everything back into the main GUI
        vertical_layout = QtGui.QVBoxLayout()
        vertical_layout.addWidget(image_view)
        vertical_layout.addWidget(hori_widget)
        
        self.ui.left_widget.setLayout(vertical_layout)
        self.ui.left_widget.setVisible(status)
#        image_view.scene.sigMouseMoved.connect(self.mouse_moved_in_image)

    def get_correct_widget_value(self, ui='', variable_name=''):
        s_variable = str(ui.text())
        if s_variable == '':
            s_variable = str(self.default_bins_settings[variable_name])
            ui.setText(s_variable)
        return np.int(s_variable)

    def roi_selection_widgets_modified(self):
                
        if self.data == []:
            return
        
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        if self.parent.binning_line_view['ui']:
            _image_view = self.parent.binning_line_view['image_view']
            _image_view.removeItem(self.parent.binning_line_view['ui'])
            self.parent.binning_line_view['ui'] = None
            
        x0 = self.get_correct_widget_value(ui = self.ui.selection_x0,
                                               variable_name = 'x0')
        y0 = self.get_correct_widget_value(ui = self.ui.selection_y0,
                                               variable_name = 'y0')
        width = self.get_correct_widget_value(ui = self.ui.selection_width,
                                                  variable_name = 'width')
        height = self.get_correct_widget_value(ui = self.ui.selection_height,
                                                   variable_name = 'height')
        bin_size = self.get_correct_widget_value(ui = self.ui.pixel_bin_size,
                                                         variable_name = 'bin_size')        
        
        self.parent.binning_bin_size = bin_size
        self.parent.binning_done = True        
    
        #self.widgets_ui['roi'].setPos([x0, y0], update=False, finish=False)
        #self.widgets_ui['roi'].setSize([width, height], update=False, finish=False)
    
        self.parent.binning_line_view['roi'].setPos([x0, y0], update=False, finish=False)
        self.parent.binning_line_view['roi'].setSize([width, height], update=False, finish=False)

        pos_adj_dict = self.calculate_matrix_of_pixel_bins(bin_size=bin_size,
                                                               x0=x0,
                                                               y0=y0,
                                                               width=width,
                                                               height=height)
    
        pos = pos_adj_dict['pos']
        adj = pos_adj_dict['adj']

        line_color = (255,0,0,255,1)    
        lines = np.array([line_color for n in np.arange(len(pos))],
                             dtype=[('red',np.ubyte),('green',np.ubyte),
                                   ('blue',np.ubyte),('alpha',np.ubyte),
                                   ('width',float)]) 
    

        self.parent.binning_line_view['pos'] = pos
        self.parent.binning_line_view['adj'] = adj
        self.parent.binning_line_view['pen'] = lines

        self.update_binning_bins()

        if self.parent.fitting_ui:
            
            o_table = TableDictionaryHandler(parent=self.parent)
            o_table.create_table_dictionary()
            
            o_fitting = FillingTableHandler(parent=self.parent)
            o_fitting.fill_table()
            
            self.parent.fitting_ui.selection_in_value_table_of_rows_cell_clicked(-1, -1)
            
            o_hanlder = FittingHandler(parent=self.parent)

            o_hanlder.display_roi()
            
        #if self.parent.fitting_ui:
            #if self.parent.fitting_ui.line_view:
                #if self.parent.fitting_ui.line_view in self.parent.fitting_ui.image_view.children():
                    #self.parent.fitting_ui.image_view.removeItem(self.parent.fitting_ui.line_view)
                #self.parent.fitting_ui.line_view = None
                    
            ## remove pre-defined lock and selected item
            #table_dictionary = self.parent.fitting_ui.table_dictionary
            #for _entry in table_dictionary.keys():
                #if table_dictionary[_entry]['selected_item'] in self.parent.fitting_ui.image_view.children():
                    #self.parent.fitting_ui.image_view.removeItem(table_dictionary[_entry]['selected_item'])
                #if table_dictionary[_entry]['locked_item'] in self.parent.fitting_ui.image_view.children():
                    #self.parent.fitting_ui.image_view.removeItem(table_dictionary[_entry]['locked_item'])
        
        #self.line_view_binning = line_view_binning
        #self.pos = pos
        #self.adj = adj
        #self.lines = lines
        
        #if self.parent.fitting_ui:
            
            #o_fitting_ui = FittingHandler(parent=self.parent)
            #o_fitting_ui.display_image()
            #o_fitting_ui.display_roi()
            #o_fitting_ui.fill_table()

        QApplication.restoreOverrideCursor()

    def update_binning_bins(self):
        '''
        this method takes from the parent file the information necessary to display the selection with
        bins in the binning window
        '''
        
        pos = self.parent.binning_line_view['pos']
        adj = self.parent.binning_line_view['adj']
        lines = self.parent.binning_line_view['pen']
        
        line_view_binning = pg.GraphItem()
        self.parent.binning_line_view['image_view'].addItem(line_view_binning)
        line_view = line_view_binning
        line_view.setData(pos=pos, 
                          adj=adj,
                          pen=lines,
                          symbol=None,
                          pxMode=False)

        self.parent.binning_line_view['ui'] = line_view
                
    def  calculate_matrix_of_pixel_bins(self, bin_size=2,
                                            x0=0,
                                            y0=0,
                                            width=20,
                                            height=20):
        
        pos_adj_dict = {}

        nbr_height_bins = np.float(height) / np.float(bin_size)
        real_height = y0 + np.int(nbr_height_bins) * np.int(bin_size)
        
        nbr_width_bins = np.float(width) / np.float(bin_size)
        read_width = x0 + np.int(nbr_width_bins) * np.int(bin_size)
        
        # pos (each matrix is one side of the lines)
        pos = []
        adj = []

        # vertical lines
        x = x0
        index = 0
        while (x <= x0 + width):
            one_edge = [x, y0]
            other_edge = [x, real_height]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index+1])
            x += bin_size
            index += 2
            
        # horizontal lines
        y = y0
        while (y <= y0 + height):
            one_edge = [x0, y]
            other_edge = [read_width, y]
            pos.append(one_edge)
            pos.append(other_edge)
            adj.append([index, index+1])
            y += bin_size
            index += 2

        pos_adj_dict['pos'] = np.array(pos)
        pos_adj_dict['adj'] = np.array(adj)
        
        return pos_adj_dict
       
    def closeEvent(self, event=None):
        self.parent.binning_ui = None
        
        if len(self.data) > 0:
            
            x0 = np.int(str(self.ui.selection_x0.text()))
            y0 = np.int(str(self.ui.selection_y0.text()))
            width = np.int(str(self.ui.selection_width.text()))
            height = np.int(str(self.ui.selection_height.text()))
            bin_size = np.int(str(self.ui.pixel_bin_size.text()))
            self.parent.binning_roi = [x0, y0, width, height, bin_size]

        else:
            
            # reset everyting if we quit with no data plotted
            binning_line_view = {'ui': None,
                                 'pos': None,
                                 'adj': None,
                                 'pen': None,
                                 'image_view': None,
                                 'roi': None}
            self.parent.binning_line_view = binning_line_view
            