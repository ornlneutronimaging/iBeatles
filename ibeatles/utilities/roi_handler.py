from PyQt5 import QtGui
from copy import deepcopy


class RoiHandler(object):
    
    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type
        
    def get_roi_index_that_changed(self):
        old_list_roi = self.parent.old_list_roi[self.data_type]
        new_list_roi = self.parent.list_roi[self.data_type]

        if not (len(old_list_roi) == len(new_list_roi)):
            self.parent.old_list_roi[self.data_type] = deepcopy(new_list_roi)
            
            return -1

        roi_index = -1
        
        for _index, _roi in enumerate(new_list_roi):
            _previous_roi = old_list_roi[_index]

            if roi_index == -1:
                if self.are_array_not_equal(_roi, _previous_roi):
                    roi_index = _index
                    old_list_roi[_index] = [_roi[:]]
                    break
                
        self.parent.old_list_roi[self.data_type] = old_list_roi
#        QtGui.QApplication.processEvents()
    
        return roi_index
        
    def are_array_not_equal(self, array1, array2):
        
        for _index, _value in enumerate(array1):
            if not (_value == array2[_index]):
                return False
        
        return True