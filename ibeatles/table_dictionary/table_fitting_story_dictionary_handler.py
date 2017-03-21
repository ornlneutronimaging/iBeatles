try:
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QApplication 
except:
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QApplication
import numpy as np

from ibeatles.utilities.status import Status


class TableFittingStoryDictionaryHandler(object):
    
    story_1 = [['a1','a6'],
               ['a2','a5'],
               ['d_spacing','sigma','alpha'],
               ['a1','a2','a5','a6'],
               ['d_spacing','sigma','alpha'],
               ['d_spacing','sigma','alpha','a1','a2','a5','a6']]

    list_widget_tag = ['d_spacing','sigma','alpha','a1','a2','a5','a6']

    def __init__(self, parent=None):
        self.parent = parent
        
    def initialize_table(self):
      
        table_fitting_story_dictionary = {}
        
        for row in np.arange(6):
            table_fitting_story_dictionary[row] = {'d_spacing': False,
                                                   'sigma': False,
                                                   'alpha': False,
                                                   'a1': False,
                                                   'a2': False,
                                                   'a5': False,
                                                   'a6': False,
                                                   'progress': Status.not_run_yet}
        
        for _index, _story in enumerate(self.story_1):
            for _variable in _story:
                table_fitting_story_dictionary[_index][_variable] = True
        
        self.parent.table_fitting_story_dictionary = table_fitting_story_dictionary

    def move_entry(self, direction='up'):

        table_fitting_story_dictionary = self.parent.table_fitting_story_dictionary
   