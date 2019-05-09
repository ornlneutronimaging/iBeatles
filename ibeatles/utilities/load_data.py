class LoadData(object):

    def __init__(self, parent=None, list_of_files=[]):
        self.parent = parent
        self.list_of_files = list_of_files

    def load(self):
        if (self.image_ext == '.tiff') or (self.image_ext == '.tif'):
            self.load_tiff()
        elif (self.image_ext == '.fits'):
            self.load_fits()
        else:
            raise TypeError("Image Type not supported")

    def load_tiff(self):
        _list_of_files = self.list_of_files
        _data = []
        for _file in _list_of_files:
            _image = mpimg.imread(_file)
            _data.append(_image)

        self.image_array = _data

    def load_fits(self):
        print("loading fits")
        print(self.list_of_files)
