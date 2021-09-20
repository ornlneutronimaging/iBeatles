import numpy as np
import collections

from ..utilities.status import Status


class TableFittingStoryDictionaryHandler(object):
    story_1 = [['a1', 'a6'],
               ['a2', 'a5'],
               ['d_spacing', 'sigma', 'alpha'],
               ['a1', 'a2', 'a5', 'a6'],
               ['d_spacing', 'sigma', 'alpha'],
               ['d_spacing', 'sigma', 'alpha', 'a1', 'a2', 'a5', 'a6']]

    list_widget_tag = ['d_spacing', 'sigma', 'alpha', 'a1', 'a2', 'a5', 'a6']

    init_entry = {'d_spacing': False,
                  'sigma': False,
                  'alpha': False,
                  'a1': False,
                  'a2': False,
                  'a5': False,
                  'a6': False,
                  'progress': Status.not_run_yet}

    def __init__(self, parent=None):
        self.parent = parent

    def initialize_table(self):

        table_fitting_story_dictionary = collections.OrderedDict()

        for row in np.arange(6):
            table_fitting_story_dictionary[row] = {'d_spacing': False,
                                                   'sigma': False,
                                                   'alpha': False,
                                                   'a1': False,
                                                   'a2': False,
                                                   'a5': False,
                                                   'a6': False,
                                                   'progress': Status.not_run_yet}

        for _index, _story in enumerate(self.story_1):
            for _variable in _story:
                table_fitting_story_dictionary[_index][_variable] = True

        self.parent.table_fitting_story_dictionary = table_fitting_story_dictionary

    def move_entry(self, current_index_row=0, direction='up'):

        table_fitting_story_dictionary = self.parent.table_fitting_story_dictionary

        if direction == 'up':
            new_index_row = current_index_row - 1
        else:
            new_index_row = current_index_row + 1

        tmp_entry = table_fitting_story_dictionary[new_index_row]
        table_fitting_story_dictionary[new_index_row] = table_fitting_story_dictionary[current_index_row]
        table_fitting_story_dictionary[current_index_row] = tmp_entry

        self.parent.table_fitting_story_dictionary = table_fitting_story_dictionary

    def remove_entry(self, index_to_remove=0):

        table_fitting_story_dictionary = self.parent.table_fitting_story_dictionary
        # nbr_entry = len(table_fitting_story_dictionary)

        new_table_fitting_story_dictionary = collections.OrderedDict()
        new_index = 0
        for _index in table_fitting_story_dictionary.keys():

            if _index == index_to_remove:
                continue

            new_table_fitting_story_dictionary[new_index] = table_fitting_story_dictionary[_index]
            new_index += 1

        self.parent.table_fitting_story_dictionary = new_table_fitting_story_dictionary

    def add_entry(self, index_to_add=1):

        table_fitting_story_dictionary = self.parent.table_fitting_story_dictionary
        nbr_entry = len(table_fitting_story_dictionary)

        new_table_fitting_story_dictionary = collections.OrderedDict()
        if table_fitting_story_dictionary == {}:
            new_table_fitting_story_dictionary[0] = self.init_entry

        else:

            new_index = 0
            if index_to_add == nbr_entry:  # if new row is at the last row
                new_table_fitting_story_dictionary = table_fitting_story_dictionary
                new_table_fitting_story_dictionary[index_to_add] = self.init_entry

            else:  # for all other rows
                for _index in table_fitting_story_dictionary.keys():

                    if _index == index_to_add:
                        new_table_fitting_story_dictionary[new_index] = self.init_entry
                        new_index += 1

                    new_table_fitting_story_dictionary[new_index] = table_fitting_story_dictionary[_index]
                    new_index += 1

        print(new_table_fitting_story_dictionary)
        self.parent.table_fitting_story_dictionary = new_table_fitting_story_dictionary
