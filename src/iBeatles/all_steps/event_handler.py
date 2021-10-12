from .. import DataType


class EventHandler:

    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type

    def is_step_selected_allowed(self, step_index_requested=0):

        # load tab
        # validate all the time
        if step_index_requested == 0:
            return True

        # normalization
        # validate only if data loaded
        if step_index_requested == 1:
            if self.parent.data_metadata[DataType.sample] == []:
                return False
            return True

        # normalized
        # validate all the time
        if step_index_requested == 2:
            return True

        # bin
        # validate only if normalized data loaded
        if step_index_requested == 3:
            if self.parent.data_metadata[DataType.normalized] == []:
                return False
            return True

        # fitting
        # validate if there is a bin region selected
        if step_index_requested == 4:
            return True


        return True



