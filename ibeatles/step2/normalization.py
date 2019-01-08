try:
    from PyQt4 import QtGui, QtCore
except:
    from PyQt5 import QtGui, QtCore
    import os
import shutil
from copy import deepcopy
import numpy as np

from ibeatles.step2.roi_handler import Step2RoiHandler
from ibeatles.step2.plot import Step2Plot
from ibeatles.utilities.file_handler import FileHandler
from ibeatles.step1.time_spectra_handler import TimeSpectraHandler


class Normalization(object):
    
    coeff_array = 1  # ob / sample of ROI selected
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run_and_export(self):
        
        # ask for output folder location
        sample_folder = self.parent.data_metadata['sample']['folder']
        sample_name = os.path.basename(os.path.dirname(sample_folder))
        default_dir = os.path.dirname(os.path.dirname(sample_folder))
        output_folder = str(QtGui.QFileDialog.getExistingDirectory(caption="Select Where the Normalized folder will be created...", 
                                                                   directory=default_dir,
                                                                   options=QtGui.QFileDialog.ShowDirsOnly))

        if not output_folder:
            return
        
        # calculate the array of coefficients
        self.run(live_plot=False)
        
        # perform normalization on all images selected
        self.normalize_full_set(output_folder = output_folder, base_folder_name = sample_name)


    def normalize_full_set(self, output_folder='', base_folder_name=''):
        
        output_folder = os.path.join(output_folder, base_folder_name + '_normalized')
        self.parent.time_spectra_normalized_folder  = output_folder
        if os.path.exists(output_folder):
            # if folder does exist already, we first remove it
            shutil.rmtree(output_folder)
        os.mkdir(output_folder)
        self.parent.ui.normalized_folder.setText(base_folder_name + '_normalized')
        self.parent.data_metadata['normalized']['folder'] = output_folder
        
        # get range we want to normalize 
        range_to_normalize = self.parent.range_files_to_normalized_step2['file_index']

        # get short list of data file names
        list_samples_names = self.parent.data_files['sample']
        list_samples_names = list_samples_names[range_to_normalize[0]: range_to_normalize[1]+1]

        data = self.parent.data_metadata['sample']['data']
        data = data[range_to_normalize[0]: range_to_normalize[1]+1]
                      
        ob = self.parent.data_metadata['ob']['data']
        ob = ob[range_to_normalize[0]: range_to_normalize[1]+1]

        array_coeff = self.coeff_array
        array_coeff = array_coeff[range_to_normalize[0]: range_to_normalize[1]+1]

        # progress bar
        self.parent.eventProgress.setMinimum(0)
        self.parent.eventProgress.setMaximum(len(list_samples_names)-1)
        self.parent.eventProgress.setValue(0)
        self.parent.eventProgress.setVisible(True)
        QtGui.QApplication.processEvents()

        # list of file name (short)
        normalized_array = []
        normalized_file_name = []
        normalized_sum_counts = []
        for _index_file, _short_file in enumerate(list_samples_names):
            
            _long_file_name = os.path.join(output_folder, _short_file)
            _data = data[_index_file]
            _ob = ob[_index_file]
            _coeff = array_coeff[_index_file]
            
            normalized_data = self.perform_single_normalization_and_export(data = _data,
                                                         ob = _ob,
                                                         coeff = _coeff,
                                                         output_file_name = _long_file_name)
            normalized_data[np.isnan(normalized_data)] = 0
            normalized_array.append(normalized_data)
            _sum = np.nansum(normalized_data)
            normalized_sum_counts.append(_sum)
            normalized_file_name.append(_short_file)
            
            self.parent.eventProgress.setValue(_index_file+1)
            QtGui.QApplication.processEvents()
                        
        self.parent.data_metadata['normalized']['data'] = normalized_array
        self.parent.data_files['normalized'] = normalized_file_name
        
        # tof array
        tof_array = self.parent.data_metadata['time_spectra']['data']
        tof_array = tof_array[range_to_normalize[0]: range_to_normalize[1]+1]
        short_tof_file_name = '{}_Spectra.txt'.format(base_folder_name)
        tof_file_name = os.path.join(output_folder, short_tof_file_name)
        tof_array = list(zip(tof_array, normalized_sum_counts))
        FileHandler.make_ascii_file(data=tof_array, output_file_name=tof_file_name, sep='\t')
        self.parent.ui.time_spectra_folder_2.setText(os.path.basename(output_folder))
        self.parent.ui.time_spectra_2.setText(short_tof_file_name)
    
        o_time_handler = TimeSpectraHandler(parent = self.parent, normalized_tab=True)
        o_time_handler.load()
        o_time_handler.calculate_lambda_scale()
        tof_array = o_time_handler.tof_array
        lambda_array = o_time_handler.lambda_array
        self.parent.data_metadata['time_spectra']['normalized_data'] = tof_array
        self.parent.data_metadata['time_spectra']['normalized_lambda'] = lambda_array        
        
        # populate normalized tab
        list_ui = self.parent.ui.list_normalized
        list_ui.clear()
        for _row, _file in enumerate(normalized_file_name):
            _item = QtGui.QListWidgetItem(_file)
            list_ui.insertItem(_row, _item)
        
        self.parent.eventProgress.setVisible(False)

    def perform_single_normalization_and_export(self, data=[], ob=[], coeff=[], output_file_name=''):
        
        ob = ob.astype(float)
        data = data.astype(float)
        coeff = coeff.astype(float)
        
        # sample / ob
        ob[ob == 0] = np.NAN
        _step1 = np.divide(data, ob)
        _step1[_step1 == np.NaN] = 0
        _step1[_step1 == np.inf] = 0
        
        # _term1 * coeff
        _data = _step1 * coeff
        
        FileHandler.make_fits(data=_data, filename=output_file_name)
        
        return _data
        
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
            # replace 0 by NaN
            one_over_coeff[one_over_coeff == 0] = np.NaN
            self.coeff_array = 1 / one_over_coeff
        else:
            o_plot = Step2Plot(parent=self.parent)
            ob_mean = o_plot.calculate_mean_counts(ob, list_roi=list_roi)
            sample_mean = o_plot.calculate_mean_counts(sample, list_roi=list_roi)
            # replace 0 by NaN
            sample_mean[sample_mean == 0] = np.NaN
            coeff = ob_mean / sample_mean
            self.coeff_array = coeff
            
