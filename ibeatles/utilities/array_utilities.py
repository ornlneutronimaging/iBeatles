import numpy as np


def find_nearest_index(array, value):
    idx = (np.abs(np.array(array)-value)).argmin()
    return idx