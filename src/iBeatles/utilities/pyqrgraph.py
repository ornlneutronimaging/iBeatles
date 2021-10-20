class Pyqtgrah:

    @staticmethod
    def get_state(image_view):
        _view = image_view.getView()
        _view_box = _view.getViewBox()
        _state = _view_box.getState()
        return _state, _view_box
