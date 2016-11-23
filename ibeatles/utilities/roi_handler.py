class RoiHandler(object):
    
    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type
        
    def get_roi_index_that_changed(self):
        old_list_roi = self.parent.old_list_roi[self.data_type]
        new_list_roi = self.parent.list_roi[self.data_type]

        roi_index = -1
        
        for _index, _roi in enumerate(new_list_roi):
            _previous_roi = old_list_roi[_index]

            if roi_index == -1:
                if not(_roi == _previous_roi):
                    roi_index = _index
                    old_list_roi[_index] = [_roi[:]]
                    break
                
        self.parent.old_list_roi[self.data_type] = old_list_roi

        print("roi_index {}".format(roi_index))
        return roi_index
            
