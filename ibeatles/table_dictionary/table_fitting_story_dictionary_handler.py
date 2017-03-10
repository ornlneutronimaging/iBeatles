from ibeatles.utilities.status import Status


class TableFittingStoryDictionaryHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def initialize_table(self):
        table_fitting_story_dictionary = {}
        
        table_fitting_story_dictionary[0] = {'d_spacing': False,
                                             'sigma': False,
                                             'alpha': False,
                                             'a1': False,
                                             'a2': False,
                                             'a5': False,
                                             'a6': False,
                                             'progress': Status.not_run_yet}
        
        self.parent.table_fitting_story_dictionary = table_fitting_story_dictionary
        