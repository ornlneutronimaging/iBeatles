from ibeatles.tools.utilities import TimeSpectraKeys


def format_str(input_list, format_str="{}", factor=1, data_type=TimeSpectraKeys.file_index_array):
    """
    format the list of file_index, tof or lambda to fill the manual bin table
    :param input_list:
    :param format_str:
    :param factor:
    :param data_type:
    :return:
    """

    if data_type == TimeSpectraKeys.file_index_array:
        if len(input_list) == 1:
            return format_str.format(input_list[0] * factor)
        elif len(input_list) == 2:
            return format_str.format(input_list[0] * factor) + ", " + \
                   format_str.format(input_list[1] * factor)
        else:
            return format_str.format(input_list[0] * factor) + " ... " + \
                   format_str.format(input_list[-1] * factor)
    else:
        if len(input_list) == 1:
            return format_str.format(input_list[0] * factor)
        else:
            return format_str.format(input_list[0] * factor) + " ... " + \
                   format_str.format(input_list[-1] * factor)
