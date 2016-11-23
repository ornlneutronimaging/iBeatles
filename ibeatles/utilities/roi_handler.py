class RoiHandler(object):
    
    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type
        
    def get_roi_index_that_changed(self):
        previous_roi = self.parent.old_list_roi[self.data_type]
        new_roi = self.parent.list_roi[self.data_type]

        roi_index = -1
        
        for _index, _roi in enumerate(new_roi):
            _previous_roi = previous_roi[_index]
            if roi_index == -1:
                if not(_roi == _previous_roi):
                    roi_index = _index
                    break
                
        old_list_roi[self.data_type] = new_roi
        self.parent.old_list_roi = old_list_roi
            
