try:
    from PyQt4 import QtGui
except:
    from PyQt5 import QtGui
import numpy as np
from lmfit import Model

from ibeatles.fitting.fitting_functions import basic_fit, advanced_fit


class ResultValueError(object):
    
    def __init__(self, result=None):
        self.result = result
        
    def get_value_err(self, tag=''):
        value = self.result.params[tag].value
        error = self.result.params[tag].stderr
        
        return [value, error]


class FittingJobHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run_story(self):
        table_fitting_story_dictionary = self.parent.table_fitting_story_dictionary
        table_dictionary = self.parent.table_dictionary
        nbr_entry = len(table_fitting_story_dictionary)

        _advanced_fitting_mode = self.parent.fitting_ui.ui.advanced_table_checkBox.isChecked()
        
        # define fitting equation
        if _advanced_fitting_mode:
            gmodel = Model(advanced_fit, missing='drop')  #do not considerate the np.NaN
        else:
            gmodel = Model(basic_fit, missing='drop')

        # index of selection in bragg edge plot
        [left_index, right_index] = self.parent.fitting_bragg_edge_linear_selection

        # retrieve image
        data_2d = np.array(self.parent.data_metadata['normalized']['data'])
        full_x_axis = self.parent.fitting_ui.bragg_edge_data['x_axis']
        x_axis = np.array(full_x_axis[left_index: right_index], dtype=float)
        
        self.parent.fitting_story_ui.eventProgress.setValue(0)
        self.parent.fitting_story_ui.eventProgress.setMaximum(nbr_entry)
        self.parent.fitting_story_ui.eventProgress.setVisible(True)
        self.parent.fitting_story_ui.eventProgress2.setVisible(True)
        
        for _entry_index in table_fitting_story_dictionary.keys():
            
            self.status_of_row(row=_entry_index, status='IN PROGRESS')

            _entry = table_fitting_story_dictionary[_entry_index]
            d_spacing_flag = _entry['d_spacing']
            alpha_flag = _entry['alpha']
            sigma_flag = _entry['sigma']
            a1_flag = _entry['a1']
            a2_flag = _entry['a2']
            
            if _advanced_fitting_mode:
                a5_flag = _entry['a5']
                a6_flag = _entry['a6']
                
            self.parent.fitting_story_ui.eventProgress2.setValue(0)
            self.parent.fitting_story_ui.eventProgress2.setMaximum(len(table_dictionary))

            # loop over all the bins
            progress_bar_index = 0
            for _bin_index in table_dictionary:
                _bin_entry = table_dictionary[_bin_index]

                
                if _bin_entry['active']:

                    # define status of variables
                    params = gmodel.make_params()

                    _d_spacing = _bin_entry['d_spacing']['val']
                    params.add('d_spacing', value=_d_spacing, vary=d_spacing_flag)
                    
                    _sigma = _bin_entry['sigma']['val']
                    params.add('sigma', value=_sigma, vary=sigma_flag)

                    _alpha = _bin_entry['alpha']['val']
                    params.add('alpha', value=_alpha, vary=alpha_flag)
                    
                    _a1 = _bin_entry['a1']['val']
                    params.add('a1', value=_a1, vary=a1_flag)
                    
                    _a2 = _bin_entry['a2']['val']
                    params.add('a2', value=_a2, vary=a2_flag)
                    
                    if _advanced_fitting_mode:
                        _a5 = _bin_entry['a5']['val']
                        params.add('a5', value=_a5, vary=a5_flag)
                        
                        _a6 = _bin_entry['a6']['val']
                        params.add('a6', value=_a6, vary=a6_flag)
                        
                    _bin_x0 = _bin_entry['bin_coordinates']['x0']
                    _bin_x1 = _bin_entry['bin_coordinates']['x1']
                    _bin_y0 = _bin_entry['bin_coordinates']['y0']
                    _bin_y1 = _bin_entry['bin_coordinates']['y1']
                    
                    y_axis = data_2d[left_index: right_index,
                                     _bin_x0: _bin_x1,
                                     _bin_y0: _bin_y1]
                    
                    y_axis = y_axis.sum(axis=1)
                    y_axis = np.array(y_axis.sum(axis=1), dtype=float)
                    
                    try:
                        result = gmodel.fit(y_axis, params, t=x_axis)
                    except ValueError:
                        self.status_of_row(row=_entry_index, status='FAILED')
                        #FIXME
                        #show dialog message that informs that fitting did not converge
                        #tell which step failed
                    
                    _o_result = ResultValueError(result=result)
                    if d_spacing_flag:
                        [value, error] = _o_result.get_value_err(tag='d_spacing')
                        _bin_entry['d_spacing']['val'] = value
                        _bin_entry['d_spacing']['err'] = error
                        
                    if sigma_flag:
                        [value, error] = _o_result.get_value_err(tag='sigma')
                        _bin_entry['sigma']['val'] = value
                        _bin_entry['sigma']['err'] = error
                        
                    if alpha_flag:
                        tag = 'alpha'
                        [value, error] = _o_result.get_value_err(tag=tag)
                        _bin_entry[tag]['val'] = value
                        _bin_entry[tag]['err'] = error
                        
                    if a1_flag:
                        tag = 'a1'
                        [value, error] = _o_result.get_value_err(tag=tag)
                        _bin_entry[tag]['val'] = value
                        _bin_entry[tag]['err'] = error
                        
                    if a2_flag:
                        tag = 'a2'
                        [value, error] = _o_result.get_value_err(tag=tag)
                        _bin_entry[tag]['val'] = value
                        _bin_entry[tag]['err'] = error
                        
                    if _advanced_fitting_mode:
    
                        if a5_flag:
                            tag = 'a5'
                            [value, error] = _o_result.get_value_err(tag=tag)
                            _bin_entry[tag]['val'] = value
                            _bin_entry[tag]['err'] = error
    
                        if a6_flag:
                            tag = 'a6'
                            [value, error] = _o_result.get_value_err(tag=tag)
                            _bin_entry[tag]['val'] = value
                            _bin_entry[tag]['err'] = error
                        
                    table_dictionary[_bin_index] = _bin_entry
                    
                progress_bar_index += 1
                self.parent.fitting_story_ui.eventProgress2.setValue(progress_bar_index)
                QtGui.QApplication.processEvents()
                
            self.status_of_row(row=_entry_index, status='DONE')
            
            self.parent.fitting_story_ui.eventProgress.setValue(_entry_index+1)
            QtGui.QApplication.processEvents()
       
            self.parent.table_dictionary = table_dictionary
            self.parent.fitting_ui.re_fill_table()
            self.parent.fitting_ui.update_bragg_edge_plot(update_selection=False)
        
        self.parent.fitting_story_ui.eventProgress.setVisible(False)
        self.parent.fitting_story_ui.eventProgress2.setVisible(False)
       
    def status_of_row(self, row=0, status='IN PROGRESS'):
        if status == 'IN PROGRESS':
            _color = QtGui.QColor(0,0,255) #blue
        elif status == 'DONE': 
            _color = QtGui.QColor(21,190,21) #green
        elif status == 'FAILED':
            status = 'SOME ERRORS!'
            _color = QtGui.QColor(255,0,0) #red
        else:
            _color =QtGui.QColor(0,0,0) #black
        _item = QtGui.QTableWidgetItem(status)
        _item.setTextColor(_color)
            
        self.parent.fitting_story_ui.ui.story_table.setItem(row, 7, _item)
        QtGui.QApplication.processEvents()
