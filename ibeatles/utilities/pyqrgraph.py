from ibeatles import DataType


class Pyqtgrah:

    def __init__(self, parent=None, image_view=None, data_type=DataType.sample):
        self.parent = parent
        self.image_view = image_view
        self.data_type = data_type
        self.first_update = False
        self.histo_widget = self.image_view.getHistogramWidget()

        if self.data_type == DataType.normalized:
            self.combine_algo = 'sum' if self.parent.ui.roi_add_button.isChecked() else 'mean'
        elif self.data_type == DataType.sample:
            self.combine_algo = 'sum' if self.parent.ui.roi_mean_button.isChecked() else 'mean'
        else:
            self.combine_algo = 'sum'

    def set_state(self, state=None):
        if self.parent.image_view_settings[self.data_type]['first_time_using_state']:
            self.parent.image_view_settings[self.data_type]['first_time_using_state'] = False
            return

        _view = self.image_view.getView()
        _view_box = _view.getViewBox()
        if not state:
            state = self.parent.image_view_settings[self.data_type]['state']
            if not state:
                return
        _view_box.setState(state)

    def get_state(self):
        _view = self.image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()
        return _state

    def save_histogram_level(self, data_type_of_data=None):
        print("saving histogram")
        print(f"-> {data_type_of_data =}")
        print(f"-> {self.data_type =}")
        if self.parent.image_view_settings[self.data_type]['first_time_using_histogram']:
            # this is to make bin and fit tabs working
            self.parent.image_view_settings[self.data_type]['first_time_using_histogram'] = False
            return

        if data_type_of_data is None:
            data_type_of_data = self.data_type

        if self.parent.data_metadata[data_type_of_data]['data'] == []:
            return

        print(f"-> {self.combine_algo =}")
        histogram_level = self.parent.image_view_settings[data_type_of_data]['histogram'][self.combine_algo]

        if histogram_level is None:
            self.first_update = True
        _histo_widget = self.image_view.getHistogramWidget()

        print(f"-> {_histo_widget.getLevels() =}")

        self.parent.image_view_settings[data_type_of_data]['histogram'][self.combine_algo] = _histo_widget.getLevels()

    def reload_histogram_level(self):
        print("in reload_histogram_level")
        if not self.first_update:
            print("-> not first update")
            if self.parent.image_view_settings[self.data_type]['histogram'][self.combine_algo]:
                self.histo_widget.setLevels(self.parent.image_view_settings[self.data_type]['histogram'][self.combine_algo][0],
                                            self.parent.image_view_settings[self.data_type]['histogram'][self.combine_algo][1])

    def set_histogram_level(self, histogram_level):
        if histogram_level:
            self.histo_widget.setLevels(histogram_level[0], histogram_level[1])
            self.parent.image_view_settings[self.data_type]['histogram'][self.combine_algo] = histogram_level
