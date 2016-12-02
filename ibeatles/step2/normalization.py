from copy import deepcopy

from ibeatles.step2.roi_handler import Step2RoiHandler
from ibeatles.step2.plot import Step2Plot


class Normalization(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run(self):
        _data = self.parent.data_metadata['sample']['data']
        _ob = self.parent.data_metadata['ob']['data']
        
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
        o_plot = Step2Plot(parent = self.parent)
        o_plot.clear_counts_vs_file()
        
    def normalization_only_sample_data_with_roi(self, data, list_roi):
        o_plot = Step2Plot(parent = self.parent, normalized=data)
        o_plot.display_counts_vs_file(list_roi = list_roi)






    
    def normalization_sample_and_ob_data_without_roi(self, data, ob):
        o_plot = Step2Plot(parent = self.parent)
        o_plot.clear_counts_vs_file()
    
    def normalization_sample_and_ob_data_with_roi(self, data, ob, list_roi):
        pass
    