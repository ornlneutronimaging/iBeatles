try:
    from PyQt4 import QtGui
except:
    from PyQt5 import QtGui


class FittingJobHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run_story(self):
        table_fitting_story_dictionary = self.parent.table_fitting_story_dictionary
        table_dictionary = self.parent.table_dictionary
        nbr_entry = len(table_fitting_story_dictionary)

        self.parent.fitting_story_ui.eventProgress.setValue(0)
        self.parent.fitting_story_ui.eventProgress.setMaximum(nbr_entry)
        self.parent.fitting_story_ui.eventProgress.setVisible(True)
        for _entry in table_fitting_story_dictionary:

            d_spacing_flag = _entry['d_spacing']
            alpha_flag = _entry['alpha']
            sigma_flag = _entry['sigma']
            a1 = _entry['a1']








            
            self.parent.fitting_story_ui.eventProgress.setValue(_entry+1)
            QtGui.QApplication.processEvents()
        
        self.parent.fitting_story_ui.eventProgress.setVisible(False)