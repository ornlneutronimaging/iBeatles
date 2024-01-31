import numpy as np


def create_list_of_bins_from_selection(top_row=0, bottom_row=0, left_column=0, right_column=0):
    """
    this will return a list of bins(row,column) from the selection

    example1:
            top_row=0, bottom_row=1, left_column=4, right_column=4
            return ((0,4), (1,4))

    example2:
            top_row=3, bottom_row=5, left_column=4, right_column=5
            return ((3,4), (4,4), (5,4), (3,5), (4,5), (5,5))
    """

    list_bins = []
    for _row in np.arange(top_row, bottom_row+1):
        for _column in np.arange(left_column, right_column+1):
            list_bins.append((_row, _column))

    list_bins.sort()

    return list(list_bins)


def create_list_of_surrounding_bins(central_bin=None, full_bin_width=None, full_bin_height=None):
    """
    this will return the list of bins surrounding the central_bin coordinates (row, column)

    bin_width = 6
    bin_height = 5

    example1:
        central_bin = (0,0)
        surrounding_bins = [(1,0), (1,1), (0,1)]

    example2:
        central_bin = (5,0)
        surrounding_bins = [(4,0), (4,1), (5,1), (6,1), (6,0)]

    example3:
        central_bin = (4,5)
        surrounding_bins = [(3,4), (3,5), (3,6), (4,4), (4,6), (5,4), (5,5), (5,6)]
    """
    row = central_bin[0]
    column = central_bin[1]

    left_row_value = np.max([row-1, 0])
    right_row_value = row if (row+1) >= full_bin_height else (row+1)

    top_column_value = np.max([column-1, 0])
    bottom_column_value = column if (column+1) >= full_bin_width else (column+1)

    list_surrounding_bins = []
    for _row in np.arange(left_row_value, right_row_value+1):
        for _column in np.arange(top_column_value, bottom_column_value+1):
            new_bin = (_row, _column)
            if new_bin == central_bin:
                continue
            list_surrounding_bins.append(new_bin)

    list_surrounding_bins.sort()
    return list_surrounding_bins


def convert_bins_to_keys(list_of_bins=None, full_bin_height=None):
    """
    this convert into a key (used by the self.grand_parent.kropff_table_dictionary) the list of
    bins values (row, column) using the simple math  key = str(_row + _col * nbr_row)
    """
    list_keys = []
    for _bin in list_of_bins:
        _row, _col = _bin
        str_key = str(_row + _col * full_bin_height)
        list_keys.append(str_key)

    return list_keys
