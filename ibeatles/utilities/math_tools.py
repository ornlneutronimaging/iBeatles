import numpy as np


def is_int(value):
    is_number = True
    try:
        int(value)
    except ValueError:
        is_number = False

    return is_number


def is_nan(value):
    if np.isnan(value):
        return True

    return False


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


class MeanRangeCalculation:
    '''
    Mean value of all the counts between left_index and right_index
    '''

    def __init__(self, data=None):
        self.data = data
        self.nbr_point = len(self.data)

    def calculate_left_right_mean(self, index=-1):
        _data = self.data
        _nbr_point = self.nbr_point

        self.left_mean = np.mean(_data[0:index + 1])
        self.right_mean = np.mean(_data[index + 1:_nbr_point])

    def calculate_delta_mean_square(self):
        self.delta_square = np.square(self.left_mean - self.right_mean)


def calculate_inflection_point(data=[]):
    '''
    will calculate the inflection point by stepping one data at a time and adding
    all the counts to the left and right of that point. Inflection point will be the max
    of the resulting array
    '''
    _working_array = []
    for _index, _y in enumerate(data):
        o_range = MeanRangeCalculation(data=data)
        o_range.calculate_left_right_mean(index=_index)
        o_range.calculate_delta_mean_square()
        _working_array.append(o_range.delta_square)

    _peak_value = _working_array.index(max(_working_array))
    return _peak_value
