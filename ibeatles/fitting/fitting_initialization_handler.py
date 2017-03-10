class FittingInitializationHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def run(self):
        self.retrieve_parameters()
        
    def retriieve_parameters(self):
        pass