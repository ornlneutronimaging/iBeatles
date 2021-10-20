from .. import DataType


class Pyqtgrah:

    def __init__(self, parent=None, image_view=None, data_type=DataType.sample):
        self.parent = parent
        self.image_view = image_view
        self.data_type = data_type
        self.first_update = False
        self.histo_widget = self.image_view.getHistogramWidget()

    def set_state(self, state=None):
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
        return _state, _view_box

    def save_histogram_level(self):
        histogram_level = self.parent.image_view_settings[self.data_type]['histogram']
        if histogram_level is None:
            self.first_update = True
        _histo_widget = self.image_view.getHistogramWidget()
        self.parent.image_view_settings[self.data_type]['histogram'] = _histo_widget.getLevels()

    def reload_histogram_level(self):
        if not self.first_update:
            self.histo_widget.setLevels(self.parent.image_view_settings[self.data_type]['histogram'][0],
                                        self.parent.image_view_settings[self.data_type]['histogram'][1])
