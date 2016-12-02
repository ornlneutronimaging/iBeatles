from copy import deepcopy

from ibeatles.step2.roi_handler import Step2RoiHandler


class Normalization(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run(self):
        _data = self.parent.data_files['sample']
        _ob = self.parent.data_files['ob']
        
        # no data, nothing to do
        if _data == []:
            return
        
        # check if roi selected or not
        o_roi_handler = Step2RoiHandler(parent = self.parent)
        try: # to avoid valueError when row not fully filled
            list_roi_to_use = o_roi_handler.get_list_of_roi_to_use()
        except ValueError:
            return

        # if just sample data
        if _ob == []:
            self.normalization_only_sample_data(_data, list_roi_to_use)
        else:
            self.normalization_sample_and_ob_data(_data, _ob, list_roi_to_use)
        
    def normalization_only_sample_data(self, data, list_roi):
        if list_roi == []:
            self.normalization_only_sample_data_without_roi(data)
        else:
            self.normalization_only_sample_data_with_roi(data, list_roi)

    def normalization_sample_and_ob_data(self, data, ob, list_roi):
        if list_roi == []:
            self.normalization_sample_and_ob_data_without_roi(data, ob)
        else:
            self.normalization_sample_and_ob_data_with_roi(data, ob, list_roi)
            
    def normalization_only_sample_data_without_roi(self, data):
        _normalized = [deepcopy(_data) for _data in data]
        self.parent.data_files['normalized'] = _normalized
        
    def normalization_only_sample_data_with_roi(self, data, list_roi):
        pass
    
    def normalization_sample_and_ob_data_without_roi(self, data, ob):
        pass
    
    def normalization_sample_and_ob_data_with_roi(self, data, ob, list_roi):
        pass
    