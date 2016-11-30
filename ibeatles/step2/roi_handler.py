from PyQt4 import QtGui


class Step2RoiHandler(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
    def save_roi(self):
        list_roi_id = self.parent.list_roi_id['normalization']
        list_roi = self.parent.list_roi['normalization']

        sample = self.parent.data_metadata['normalization']['data']
        image_item = self.parent.step2_ui['image_view'].imageItem

        for _index, _roi_id in enumerate(list_roi_id):
            region = _roi_id.getArraySlice(sample, image_item)
            x0 = region[0][0].start
            x1 = region[0][0].stop-1
            y0 = region[0][1].start
            y1 = region[0][1].stop-1
            
            width = x1-x0
            height = y1-y0
            
            _roi = list_roi[_index]
            _roi[2] = x0
            _roi[3] = x1
            _roi[4] = width
            _roi[5] = height
            
            list_roi[_index] = _roi
            
        self.parent.list_roi['normalization'] = list_roi
