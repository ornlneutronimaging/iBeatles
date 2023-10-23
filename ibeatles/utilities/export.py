from ibeatles.fitting import FittingKeys
from ibeatles.utilities.array_utilities import from_nparray_to_list
from ibeatles.utilities.json_handler import make_value_json_friendly
from ibeatles.fitting.kropff import SessionSubKeys


@staticmethod
def format_kropff_dict(table: dict = None, d_dict: dict = None, strain_dict: dict = None, json_friendly : bool = False):
    """

    Parameters
    ----------
    table
    d_dict
    strain_dict
    json_friendly if True, the NaN will be replaced by 'NULL'

    Returns
    -------

    """

    cleaned_table = {}
    for _row in table.keys():
        cleaned_table[_row] = {}
        cleaned_table[_row][FittingKeys.y_axis] = from_nparray_to_list(table[_row][FittingKeys.y_axis],
                                                                       json_friendly=json_friendly)
        cleaned_table[_row][FittingKeys.x_axis] = from_nparray_to_list(table[_row][FittingKeys.x_axis],
                                                                       json_friendly=json_friendly)

        cleaned_table[_row][SessionSubKeys.fitted] = {}

        cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof] = {}
        cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof][FittingKeys.x_axis] = \
            from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof][FittingKeys.x_axis],
                                 json_friendly=json_friendly)
        cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof][FittingKeys.y_axis] = \
            from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.high_tof][FittingKeys.y_axis],
                                 json_friendly=json_friendly)

        cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof] = {}
        cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof][FittingKeys.x_axis] = \
            from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof][FittingKeys.x_axis],
                                 json_friendly=json_friendly)
        cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof][FittingKeys.y_axis] = \
            from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.low_tof][FittingKeys.y_axis],
                                 json_friendly=json_friendly)

        cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak] = {}
        cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak][FittingKeys.x_axis] = \
            from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak][FittingKeys.x_axis],
                                 json_friendly=json_friendly)
        cleaned_table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak][FittingKeys.y_axis] = \
            from_nparray_to_list(table[_row][SessionSubKeys.fitted][SessionSubKeys.bragg_peak][FittingKeys.y_axis],
                                 json_friendly=json_friendly)

        def format_output(input=None, json_friendly=False):
            """create a json friendly version of the input if required"""
            if json_friendly:
                return make_value_json_friendly(input)
            else:
                return input

        # if json_friendly:
        cleaned_table[_row]['strain'] = {'val': format_output(strain_dict[_row]['val']),
                                         'err': format_output(strain_dict[_row]['err'])}
        cleaned_table[_row]['d'] = {'val': format_output(d_dict[_row]['val']),
                                    'err': format_output(d_dict[_row]['err'])}

        cleaned_table[_row]['a0'] = format_output(table[_row]['a0'])
        cleaned_table[_row]['b0'] = format_output(table[_row]['b0'])
        cleaned_table[_row]['ahkl'] = format_output(table[_row]['ahkl'])
        cleaned_table[_row]['bhkl'] = format_output(table[_row]['bhkl'])
        cleaned_table[_row]['tau'] = format_output(table[_row]['tau'])
        cleaned_table[_row]['sigma'] = format_output(table[_row]['sigma'])
        cleaned_table[_row]['lambda_hkl'] = format_output(table[_row]['lambda_hkl'])

        cleaned_table[_row]['bragg peak threshold'] = format_output(table[_row]['bragg peak threshold'])

        # else:
        #
        #     cleaned_table[_row]['strain'] = {'val': format_output(strain_dict[_row]['val']),
        #                                      'err': format_output(strain_dict[_row]['err'])}
        #     cleaned_table[_row]['d'] = {'val': format_output(d_dict[_row]['val']),
        #                                 'err': format_output(d_dict[_row]['err'])}
        #
        #     cleaned_table[_row]['a0'] = format_output(table[_row]['a0'])
        #     cleaned_table[_row]['b0'] = format_output(table[_row]['b0'])
        #     cleaned_table[_row]['ahkl'] = format_output(table[_row]['ahkl'])
        #     cleaned_table[_row]['bhkl'] = format_output(table[_row]['bhkl'])
        #     cleaned_table[_row]['tau'] = format_output(table[_row]['tau'])
        #     cleaned_table[_row]['sigma'] = format_output(table[_row]['sigma'])
        #     cleaned_table[_row]['lambda_hkl'] = format_output(table[_row]['lambda_hkl'])
        #
        #     cleaned_table[_row]['bragg peak threshold'] = format_output(table[_row]['bragg peak threshold'])

        cleaned_table[_row]['bin_coordinates'] = {'x0': format_output(table[_row]['bin_coordinates']['x0']),
                                                  'y0': format_output(table[_row]['bin_coordinates']['y0']),
                                                  'x1': format_output(table[_row]['bin_coordinates']['x1']),
                                                  'y1': format_output(table[_row]['bin_coordinates']['y1'])}

    return cleaned_table


@staticmethod
def format_kropff_table(table: dict = None, d_dict: dict = None, strain_dict: dict = None):
    formatted_table = ["#index, " +
                       "bin x0, bin y0, bin x1, bin y1, " +
                       "lambda hkl val, lambda hkl err, " +
                       "d value, d err, strain, strain error"]
    for _row in table.keys():
        _entry = table[_row]

        _row_index = _row
        _bin_x0 = _entry['bin_coordinates']['x0']
        _bin_y0 = _entry['bin_coordinates']['y0']
        _bin_x1 = _entry['bin_coordinates']['x1']
        _bin_y1 = _entry['bin_coordinates']['y1']

        _lambda_hkl_val = _entry['lambda_hkl']['val']
        _lambda_hkl_err = _entry['lambda_hkl']['err']

        _d_value = d_dict[_row]['val']
        _d_err = d_dict[_row]['err']

        _strain_value = strain_dict[_row]['val']
        _strain_value_err = strain_dict[_row]['err']

        line = [_row_index,
                _bin_x0, _bin_y0, _bin_y0, _bin_y1,
                _lambda_hkl_val, _lambda_hkl_err,
                _d_value, _d_err,
                _strain_value, _strain_value_err]
        line = [str(_value) for _value in line]

        formatted_table.append(", ".join(line))

    return formatted_table
