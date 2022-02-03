import numpy as np

from src.iBeatles.step6.get import Get


class Display:

    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        self.view_box = self._get_view_box()
        self.state = self._get_state()

    def run(self):

        self.parent.image_view.clear()
        if self.parent.ui.display_d_radioButton.isChecked():
            self.d_array()
        elif self.parent.ui.display_strain_mapping_radioButton.isChecked():
            self.strain_mapping()
        elif self.parent.ui.display_integrated_image_radioButton.isChecked():
            self.integrated_image()
        else:
            raise NotImplementedError("Display not implemented!")

    def integrated_image(self):
        integrated_image = self.parent.integrated_image
        self.parent.image_view.setImage(np.transpose(integrated_image))
        self.view_box.setState(self.state)

    def d_array(self):
        d_array = self.parent.d_array
        self.parent.image_view.setImage(np.transpose(d_array))
        self.view_box.setState(self.state)

    def strain_mapping(self):
        d_array = self.parent.d_array
        o_get = Get(parent=self.parent)
        d0 = o_get.active_d0()
        strain_mapping = (d_array - d0) / d0
        self.parent.image_view.setImage(np.transpose(strain_mapping))
        self.view_box.setState(self.state)

    def _get_view_box(self):
        _view = self.parent.image_view.getView()
        _view_box = _view.getViewBox()
        return _view_box

    def _get_state(self):
        return self.view_box.getState()
