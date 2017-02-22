import numpy as np


class FillingTableHandler(object):
    
    val_err_dict = {'val': -1,
                    'err': -1}
    
    init_dict = {'bin_coordinates': {'x0': -1,
                                     'x1': -1,
                                     'y0': -1,
                                     'y1': -1},
                 'selected': False,
                 'lock': False,
                 'fitting_confidence': -1,
                 'd_spacing': val_err_dict,
                 'sigma': val_err_dict,
                 'intensity': val_err_dict,
                 'alpah': val_err_dict,
                 'a1': val_err_dict,
                 'a2': val_err_dict,
                 'a5': val_err_dict,
                 'a6': val_err_dict}
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def create_table_dictionary(self):
        '''
        this will define the corner position and index of each cell
        '''
        bin_size = self.parent.binning_bin_size
        pos = self.parent.binning_ui.pos
        
        # calculate outside real edges of bins
        min_max_xy = self.get_min_max_xy(pos)
        
        from_x = min_max_xy['x']['min']
        to_x = min_max_xy['x']['max']
        
        from_y = min_max_xy['y']['min']
        to_y = min_max_xy['y']['max']
        
        table_dictionary = {}
        _index = 0
        for _x in np.arange(from_x, to_x):
            for _y in np.arange(from_y, to_y):
                _str_index = str(_index)
                table_dictionary[_str_index] = self.init_dict
                table_dictionary[_str_index]['bin_coordinates']['x0'] = _x
                table_dictionary[_str_index]['bin_coordinates']['x1'] = _x+1
                table_dictionary[_str_index]['bin_coordinates']['y0'] = _y
                table_dictionary[_str_index]['bin_coordinates']['y1'] = _y+1

        
        self.table_dictionary = table_dictionary

    def fill_table(self):
        table_dictionary = self.table_dictionary
        nbr_row = len(table_dictionary)
        
        for _index in np.arange(nbr_row):
            _str_index = str(_index)
            _entry = table_dictionary[_str_index]
            
            
        





    def get_min_max_xy(self, pos_array):
        min_x = 10000
        max_x = -1
        min_y = 10000
        max_y = -1
        
        for xy in pos_array:
            [_x, _y] = xy
            if _x < min_x:
                min_x = _x
            if _x > max_x:
                max_x = _x
            if _y < min_y:
                min_y = _y
            if _y > max_y:
                max_y = _y

        return {'x': {'min': min_x, 
                      'max': max_x},
                'y': {'min': min_y,
                      'max': max_y}
                }

