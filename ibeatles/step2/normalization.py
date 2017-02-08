from PyQt4 import QtGui
import os
from copy import deepcopy
import numpy as np

from ibeatles.step2.roi_handler import Step2RoiHandler
from ibeatles.step2.plot import Step2Plot


class Normalization(object):
    
    coeff_array = 1
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run_and_export(self):
        
        # ask for output folder location
        sample_folder = self.parent.data_metadata['sample']['folder']
        default_dir = os.path.dirname(os.path.dirname(sample_folder))
        output_folder = QtGui.QFileDialog.getExistingDirectory(caption="Select Where the Normalized folder will be created...", 
                                                              directory=default_dir, 
                                                              options=QtGui.QFileDialog.ShowDirsOnly)

        if not output_folder:
            return
        
        # calculate the array of coefficients
        self.run(live_plot=False)
        
        # perform normalization on all images selected
        self.normalize_full_set(output_folder = output_folder)


    def normalize_full_set(self, output_folder=''):
        
        # get short list of data file names
        list_samples_names = self.parent.data_files['sample']
    
        # get range we want to normalize 
        range_to_normalize = self.parent.range_files_to_normalized_step2['file_index']

        _data = self.parent.data_metadata['sample']['data']
        _data = _data[range_to_normalize[0]: range_to_normalize[1]+1]
                      
        _ob = self.parent.data_metadata['ob']['data']
        _ob = _ob[range_to_normalize[0]: range_to_normalize[1]+1]

        _array_coeff = self.coeff_array
        _array_coeff = _array_coeff[range_to_normalize[0]: range_to_normalize[1]+1]

        print(np.shape(_data))
        print(np.shape(_ob))
        print(np.shape(_array_coeff))



        
    def run(self, live_plot=True):
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
            self.normalization_only_sample_data(_data, list_roi_to_use, live_plot)
        else:
            self.normalization_sample_and_ob_data(_data, _ob, list_roi_to_use, live_plot)
        
    def normalization_only_sample_data(self, data, list_roi, live_plot):
        if list_roi == []:
            self.normalization_only_sample_data_without_roi(data, live_plot)
        else:
            self.normalization_only_sample_data_with_roi(data, list_roi, live_plot)

    def normalization_sample_and_ob_data(self, data, ob, list_roi, live_plot):
        if list_roi == []:
            self.normalization_sample_and_ob_data_without_roi(data, ob, live_plot)
        else:
            self.normalization_sample_and_ob_data_with_roi(data, ob, list_roi, live_plot)
            
    def normalization_only_sample_data_without_roi(self, data, live_plot):
        o_plot = Step2Plot(parent = self.parent)
        o_plot.clear_counts_vs_file()
        
    def normalization_only_sample_data_with_roi(self, data, list_roi, live_plot):
        o_plot = Step2Plot(parent = self.parent, normalized=data)
        self.calculate_coeff(sample=data, list_roi=list_roi)
        #sample_integrated = o_plot.calculate_mean_counts(data)
        #array_by_coeff = o_plot.multiply_array_by_coeff(data=sample_integrated, coeff=self.coeff_array)
        if live_plot:
            o_plot.display_counts_vs_file(data = self.coeff_array)
    
    def normalization_sample_and_ob_data_without_roi(self, data, ob, live_plot):
        o_plot = Step2Plot(parent = self.parent)
        o_plot.clear_counts_vs_file()
    
    def normalization_sample_and_ob_data_with_roi(self, data, ob, list_roi, live_plot):
        o_plot = Step2Plot(parent = self.parent, normalized=data)
        self.calculate_coeff(sample=data, ob=ob, list_roi=list_roi)
        #sample_integrated = o_plot.calculate_mean_counts(data)
        #ob_integrated = o_plot.calculate_mean_counts(ob)
        #ratio_array = sample_integrated / ob_integrated
        #array_by_coeff = o_plot.multiply_array_by_coeff(data=ratio_array, coeff=self.coeff_array)
        if live_plot:
            #o_plot.display_counts_vs_file(data = array_by_coeff)
            o_plot.display_counts_vs_file(data = self.coeff_array)
            
    def calculate_coeff(self, sample=[], ob=[], list_roi=[]):
        if ob == []:
            # we consider that no OB is like having a perfect OB -> intensity of 1
            o_plot = Step2Plot(parent=self.parent)
            one_over_coeff = o_plot.calculate_mean_counts(sample, list_roi=list_roi)
            self.coeff_array = 1 / one_over_coeff
        else:
            o_plot = Step2Plot(parent=self.parent)
            ob_mean = o_plot.calculate_mean_counts(ob, list_roi=list_roi)
            sample_mean = o_plot.calculate_mean_counts(sample, list_roi=list_roi)
            coeff = ob_mean / sample_mean
            self.coeff_array = coeff
            
