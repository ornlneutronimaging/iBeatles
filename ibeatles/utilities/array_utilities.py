import numpy as np


def find_nearest_index(array, value):
    idx = (np.abs(np.array(array)-value)).argmin()
    return idx

def get_min_max_xy(pos_array):
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

