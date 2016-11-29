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

from ibeatles.utilities.colors import pen_color


class CustomAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return ['{:.4f}'.format(1./i) for i in values]
                
                
class Step2GuiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def init_pyqtgraph(self):
        pass
