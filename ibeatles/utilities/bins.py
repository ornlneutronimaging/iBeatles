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
