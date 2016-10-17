from PIL import Image


class ImageHandler(object):
    
    metadata = {}
    data_type = 'tiff'
    
    def __init__(self, parent=None, list_files = None):
        self.parent = parent
        self.list_files = list_files
        self.get_data_type()
        
    def get_data_type(self):
        pass
        
    def get_data(self):
        if list_files is None:
            return
        
        for _file in self.list_files:
            _data = self.get_tiff_data(_file)


    def get_tiff_data(self, filename):
        _o_image = Image.open(filename)
        _metadata = _o_image.tag_v2.as_dict()
        self.metadata[filename] = _metadata
    
    