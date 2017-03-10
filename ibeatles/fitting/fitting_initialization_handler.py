class FittingInitializationHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run(self):
        self.retrieve_parameters()
        
    def retrieve_parameters(self):
        d_spacing = self.get_d_spacing()
        


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