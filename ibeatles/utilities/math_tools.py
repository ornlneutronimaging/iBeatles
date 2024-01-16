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


def get_value_of_closest_match(array_to_look_for=None, value=None, left_margin=True):
    """
    for example if the array_to_look = [1,2,3,4] and the value is 2.3,
    the method will return 2.
    for 2.5, it will return the closest or less than value, in this case 2 again.

    :param array_to_look_for: array where to find the closest match
    :param value: input value to use
    :return: return the closest value to the input value found in the array_to_look
    """
    array_to_look_for_in_float = [float(_value) for _value in array_to_look_for]
    value_float = float(value)

    diff_array = [np.abs(_v - value_float) for _v in array_to_look_for_in_float]
    array_of_matches = np.where(np.min(diff_array) == diff_array)

    if left_margin and len(array_of_matches[0]) == 2:
        index = -1
    else:
        index = 0
    best_match = array_of_matches[0][index]
    return best_match
