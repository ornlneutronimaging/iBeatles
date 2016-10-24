from PIL import Image
import os


class ImageHandler(object):
    
    metadata = {}
    data_type = 'tiff'
    data = []
    filename = ''
    
    def __init__(self, parent=None, list_files = None):
        self.data = []
        self.parent = parent
        self.list_files = list_files

        # only first file loaded for now
        self.filename = list_files[0]
        self.retrieve_image_type()
        
    def retrieve_image_type(self):
        _file_0 = self.filename
        [filename, file_extension] = os.path.splitext(_file_0)
        if (file_extension == '.tiff') or (file_extension == '.tif'):
            self.data_type = 'tiff'
        elif (file_extension == '.fits'):
            self.data_type = 'fits'
        else:
            raise ValueError("File Format not Supported!")
        
    def get_data(self):
        if self.filename == '':
            return []
        
        # if data not loaded yet
        if self.data == []:
            
            # only load first selected data
            _file = self.filename
            if self.data_type == 'tiff':
                self.get_tiff_data()
            elif self.data_type == 'fits':
                self.get_fits_data()

    def get_metadata(self, selected_infos_dict={}):
        if self.data_type == 'tiff':
            self.get_tiff_metadata(selected_infos_dict)
        elif self.data_type == 'fits':
            self.get_fits_metadata(selected_infos_dict)
            
            
    def get_tiff_data(self):
        filename = self.filename
        pass
    
    def get_fits_data(self):
        filename = self.filename
        pass

    def get_tiff_metadata(self, selected_infos):

        _o_image = Image.open(self.filename)
        _metadata = _o_image.tag_v2.as_dict()

        



        return None
    
    def get_fits_metadata(self, filename):
        pass