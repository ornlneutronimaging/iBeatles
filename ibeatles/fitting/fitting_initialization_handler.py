try:
    import PyQt4
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QApplication         
except:
    import PyQt5
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QApplication

import numpy as np

from ibeatles.table_dictionary.table_dictionary_handler import TableDictionaryHandler
from ibeatles.fitting.initialization_sigma_alpha import InitializationSigmaAlpha
from ibeatles.utilities.math_tools import calculate_inflection_point

class FittingInitializationHandler(object):

    all_variables_initialized = True
    advanced_mode = False
    selection_range = {'left_range': {'x_axis': [],
                                      'y_axis': [],
                                      },
                       'right_range': {'x_axis': [],
                                       'y_axis': [],
                                       },
                       'inflection': {'x': np.NaN,
                                      'y': np.NaN},
                       }
    
    a1 = np.NaN   #only used when using basic mode to calculate a2
    
    percentage_of_data_to_remove_on_side = 10.  #%
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def make_all_active(self):
        o_table = TableDictionaryHandler(parent=self.parent)
        o_table.full_table_selection_tool(status=True)
        self.parent.fitting_ui.update_table()
        self.parent.fitting_ui.update_bragg_edge_plot()
        
    def run(self):
        o_init_sigma_alpha = InitializationSigmaAlpha(parent=self.parent)
        
    def finished_up_initialization(self):
        self.advanced_mode = self.parent.fitting_ui.ui.advanced_table_checkBox.isChecked()
        if self.parent.fitting_ui.sigma_alpha_initialized:
            QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            self.retrieve_parameters_and_update_table()
            self.parent.fitting_ui.update_table()
            QApplication.restoreOverrideCursor()
        
    def retrieve_parameters_and_update_table(self):
        table_handler = TableDictionaryHandler(parent=self.parent)
        initialization_table = self.parent.fitting_ui.initialization_table

        d_spacing = self.get_d_spacing()
        if np.isnan(d_spacing):
            self.all_variables_initialized = False
        initialization_table['d_spacing'] = d_spacing
        table_handler.fill_table_with_variable(variable_name = 'd_spacing',
                                               value = d_spacing,
                                               all_keys = True)

        sigma = self.get_sigma()
        if np.isnan(sigma):
            self.all_variables_initialized = False
        table_handler.fill_table_with_variable(variable_name = 'sigma',
                                               value = sigma,
                                               all_keys = True)
        
        alpha = self.get_alpha()
        if np.isnan(alpha):
            self.all_variables_initialized = False
        table_handler.fill_table_with_variable(variable_name = 'alpha',
                                               value = alpha,
                                               all_keys = True)
        
        # this function will allow to retrieve parameters that will be used by a1, a2, a5 and a6 
        self.isolate_left_and_right_part_of_inflection_point()

        if self.advanced_mode:

            a2 = self.get_a2()
            if np.isnan(a2):
                self.all_variables_initialized = False
            initialization_table['a2'] = a2
            table_handler.fill_table_with_variable(variable_name = 'a2',
                                                   value = a2,
                                                   all_keys = True)
            
            a5 = self.get_a5()
            if np.isnan(a5):
                self.all_variables_initialized = False
            initialization_table['a5'] = a5
            table_handler.fill_table_with_variable(variable_name = 'a5',
                                                   value = a5,
                                                   all_keys = True)
            
            a6 = self.get_a6()
            if np.isnan(a6):
                self.all_variables_initialized = False
            initialization_table['a6'] = a6
            table_handler.fill_table_with_variable(variable_name = 'a6',
                                                   value = a6,
                                                   all_keys = True)            


            a1 = self.get_a1()
            if np.isnan(a1):
                self.all_variables_initialized = False
            initialization_table['a1'] = a1
            table_handler.fill_table_with_variable(variable_name = 'a1',
                                                   value = a1,
                                                   all_keys = True)

        else: # basic mode
            
            a1 = self.get_a1()
            if np.isnan(a1):
                self.all_variables_initialized = False
            initialization_table['a1'] = a1
            table_handler.fill_table_with_variable(variable_name = 'a1',
                                                   value = a1,
                                                   all_keys = True)
            
            a2 = self.get_a2()
            if np.isnan(a2):
                self.all_variables_initialized = False
            initialization_table['a2'] = a2
            table_handler.fill_table_with_variable(variable_name = 'a2',
                                                   value = a2,
                                                   all_keys = True)
        
        
        self.parent.fitting_ui.initialization_table = initialization_table
        
    def isolate_left_and_right_part_of_inflection_point(self):
    
        # get array of counts selected
        [left_index, right_index] =  self.parent.fitting_bragg_edge_linear_selection

        # get full x_axis
        full_x_axis = self.parent.fitting_ui.bragg_edge_data['x_axis']
        
        # get full y_axis
        full_y_axis = self.parent.fitting_ui.bragg_edge_data['y_axis']
        
        ## calculate inflexion point (index) using Ed's method
        #y_axis = full_y_axis[left_index: right_index+1]
        #inflection_point_index = calculate_inflection_point(data=y_axis)
        #print(inflection_point_index)
        #print(y_axis[inflection_point_index + left_index])
    
        # for now inflection is only calculated by using center of selection
        inflection_point_index = np.int(np.mean([left_index, right_index]))
        self.selection_range['left_range']['y_axis'] = full_y_axis[left_index: inflection_point_index]
        self.selection_range['left_range']['x_axis'] = full_x_axis[left_index: inflection_point_index]
        self.selection_range['right_range']['y_axis'] = full_y_axis[inflection_point_index: ]
        self.selection_range['right_range']['x_axis'] = full_x_axis[inflection_point_index: ]
        self.selection_range['inflection']['y'] = full_y_axis[inflection_point_index]
        self.selection_range['inflection']['x'] = full_x_axis[inflection_point_index]
        
    def get_a1(self):
        if self.advanced_mode:
            intercept = self.a2_intercept
            a2 = self.a2
            a6 = self.a6
            return intercept + a2 * a6
        else:
            left_range = self.selection_range['left_range']['y_axis']
            nbr_data = len(left_range)
            nbr_data_to_remove = np.int((self.percentage_of_data_to_remove_on_side/100.)*nbr_data)
            a1 = np.mean(left_range[0: -nbr_data_to_remove])
            self.a1 = a1
            return a1
    
    def get_a2(self):
        if self.advanced_mode:
            x_axis = self.selection_range['left_range']['x_axis']
            y_axis = self.selection_range['left_range']['y_axis']
            
            nbr_data = len(x_axis)
            nbr_data_to_remove = np.int((self.percentage_of_data_to_remove_on_side/100.)*nbr_data)
            
            x_axis_to_use = x_axis[0: nbr_data_to_remove]
            y_axis_to_use = y_axis[0: nbr_data_to_remove]
            
            [slope, interception] = np.polyfit(x_axis_to_use, y_axis_to_use, 1)
            self.a2 = slope # saving it to calculate a6
            self.a2_intercept = interception # saving it to calculate a1
            return slope

        else:
            _mean_left_side = self.a1
            right_range = self.selection_range['right_range']['y_axis']
            nbr_data = len(right_range)
            nbr_data_to_remove = np.int((self.percentage_of_data_to_remove_on_side/100.)*nbr_data)
            _mean_right_side = np.mean(right_range[nbr_data_to_remove:])
            a2 = np.abs(_mean_right_side - _mean_left_side)
            return a2
        
    def get_a5(self):
        x_axis = self.selection_range['right_range']['x_axis']
        y_axis = self.selection_range['right_range']['y_axis']
    
        nbr_data = len(x_axis)
        nbr_data_to_remove = np.int((self.percentage_of_data_to_remove_on_side/100.)*nbr_data)
    
        print("nbr_data_to_remove: {}".format(nbr_data_to_remove))
        print("len(x_axis): {}".format(len(x_axis)))
    
        x_axis_to_use = x_axis[nbr_data_to_remove:]
        y_axis_to_use = y_axis[nbr_data_to_remove:]
    
        [slope, interception] = np.polyfit(x_axis_to_use, y_axis_to_use, 1)
        self.a5 = slope # saving it to calculate a6
        return slope
    
    def get_a6(self):
        '''see docs folder for full description of formula used to get a6'''

        intensity = self.selection_range['inflection']['y']
        x_edge = self.selection_range['inflection']['x']
        
        a6 = x_edge - (2. * intensity) / (self.a5 - self.a2)
        self.a6 = a6 # saving it to caculate a1
        return a6

    def get_sigma(self):
        sigma = self.parent.fitting_ui.initialization_table['sigma']
        return sigma
    
    def get_alpha(self):
        alpha = self.parent.fitting_ui.initialization_table['alpha']
        return alpha

    def get_d_spacing(self):
        '''
        calculates the d-spacing using the lambda range selection and using the central lambda
        
        2* d_spacing = lambda
        '''
        lambda_min = np.float(str(self.parent.fitting_ui.ui.lambda_min_lineEdit.text()))
        lambda_max = np.float(str(self.parent.fitting_ui.ui.lambda_max_lineEdit.text()))
        
        average_lambda = np.mean([lambda_min, lambda_max])
        
        d_spacing = average_lambda / 2.
        
        return d_spacing