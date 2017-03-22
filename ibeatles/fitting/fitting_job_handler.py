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

        _advanced_fitting_mode = self.parent.fitting_ui.ui.advanced_table_checkBox.isChecked()

        self.parent.fitting_story_ui.eventProgress.setValue(0)
        self.parent.fitting_story_ui.eventProgress.setMaximum(nbr_entry)
        self.parent.fitting_story_ui.eventProgress.setVisible(True)
        for _entry in table_fitting_story_dictionary:

            d_spacing_flag = _entry['d_spacing']
            alpha_flag = _entry['alpha']
            sigma_flag = _entry['sigma']
            a1_flag = _entry['a1']
            a2_flag = _entry['a2']
            
            if _advanced_fitting_mode:
                a5_flag = _entry['a5']
                a6_flag = _entry['a6']
                
            # loop over all the bins
            for _bin_index in table_dictionary:
                _bin_entry = table_dictionary[_bin_index]
                if _bin_entry['active']:
                    _d_spacing = _bin_entry['d_spacing']
                    _sigma = _bin_entry['sigma']
                    _alpha = _bin_entry['alpha']
                    _a1 = _bin_entry['a1']
                    _a2 = _bin_entry['a2']
                    
                    if _advanced_fitting_mode:
                        _a5 = _bin_entry['a5']
                        _a6 = _bin_entry['a6']
                        
                    _bin_x0 = _bin_entry['bin_coordinates']['x0']
                    _bin_x1 = _bin_entry['bin_coordinates']['x1']
                    _bin_y0 = _bin_entry['bin_coordinates']['y0']
                    _bin_y1 = _bin_entry['bin_coordinates']['y1']
                    
                    
                    
                
            
            







            
            self.parent.fitting_story_ui.eventProgress.setValue(_entry+1)
            QtGui.QApplication.processEvents()
        
        self.parent.fitting_story_ui.eventProgress.setVisible(False)