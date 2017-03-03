import numpy as np


def is_int(value):
    
    is_number = True
    try:
        int(value)
    except ValueError:
        is_number = False
        
    return is_number

def is_float(value):
    
    is_number = True
    try:
        float(value)
    except ValueError:
        is_number = False
        
    return is_number

def get_random_value(max_value=1):
    _value = np.random.rand()
    return _value * max_value
    