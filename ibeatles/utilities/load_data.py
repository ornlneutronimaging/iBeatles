from astropy.io import fits
from PIL import Image


class LoadData(object):

    __slots__ = ['image_array', 'parent', 'list_of_files', 'image_ext']

    def __init__(self, parent=None, list_of_files=[], image_ext='.fits'):
        self.parent = parent
        self.list_of_files = list_of_files
        self.image_ext = image_ext

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
        _list_of_files = self.list_of_files
        _data = []
        for _file in _list_of_files:
            _image = self.load_fits_file(_file)
            _data.append(_image)

        self.image_array = _data

    @staticmethod
    def load_fits_file(fits_file_name):
        tmp = fits.open(fits_file_name, ignore_missing_end=True)[0].data
        try:
            if len(tmp.shape) == 3:
                tmp = tmp.reshape(tmp.shape[1:])
            return tmp
        except OSError:
            raise OSError("Unable to read the FITS file provided!")


