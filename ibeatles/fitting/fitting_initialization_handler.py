import numpy as np

from ibeatles.table_dictionary.table_dictionary_handler import TableDictionaryHandler


class FittingInitializationHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run(self):
        self.retrieve_parameters_and_update_table()
        self.parent.fitting_ui.update_table()
        
        
    def retrieve_parameters_and_update_table(self):
        table_handler = TableDictionaryHandler(parent=self.parent)

        d_spacing = self.get_d_spacing()
        table_handler.fill_table_with_variable(variable_name = 'd_spacing',
                                               value = d_spacing,
                                               all_keys = True)

        sigma = self.get_sigma()
        table_handler.fill_table_with_variable(variable_name = 'sigma',
                                               value = sigma,
                                               all_keys = True)
        
        alpha = self.get_alpha()
        table_handler.fill_table_with_variable(variable_name = 'alpha',
                                               value = alpha,
                                               all_keys = True)
        
        a1 = self.get_a1()
        table_handler.fill_table_with_variable(variable_name = 'a1',
                                               value = a1,
                                               all_keys = True)
        
        a2 = self.get_a2()
        table_handler.fill_table_with_variable(variable_name = 'a2',
                                               value = a2,
                                               all_keys = True)

        
    def get_a1(self):
        return np.NaN
    
    def get_a2(self):
        return np.NaN
        
    def get_sigma(self):
        return np.NaN
    
    def get_alpha(self):
        return np.NaN

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