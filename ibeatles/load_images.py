import glob


class LoadImages(object):
    
    image_array = []
    list_of_files = []

    def __init__(self, image_ext = '.tiff', folder = None):
        self.image_ext = image_ext
        self.folder = folder
        
        
        self.retrieve_list_of_files()
        self.load()
        
        
    def retrieve_list_of_files(self):
        _folder = self.folder
        _image_ext = self.image_ext
        _list_of_files = glob.glob(_folder + '/*' + _image_ext)
        print("searching criteria: " + _folder + '/*' + _image_ext)
        self.list_of_files = _list_of_files

    def load(self):
        if (self.image_ext == '.tiff') or (self.image_ext == '.tif'):
            self.load_tiff()
        elif (self.image_ext == '.fits'):
            self.load_fits()
        else:
            raise TypeError("Image Type not supported")
    
    def load_tiff(self):
        print("loading tiff")
        print(self.list_of_files)
    
    def load_fits(self):
        print("loading fits")
        print(self.list_of_files)
        