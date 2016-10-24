from PIL import Image
import os
import numpy as np
import time


class ImageHandler(object):
    
    metadata = {}
    data_type = 'tiff'
    data = [] # numpy array of image
    metadata = {} # metadata dictionary
    filename = ''
    
    def __init__(self, parent=None, filename = None):
        self.data = []
        self.parent = parent

        # only first file loaded for now
        self.filename = filename
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
        if self.data == []:
            self.get_data()
            
        if self.data_type == 'tiff':
            self.get_tiff_metadata(selected_infos_dict)
        elif self.data_type == 'fits':
            self.get_fits_metadata(selected_infos_dict)
            
        return self.metadata
            
            
    def get_tiff_data(self):
        filename = self.filename
        _o_image = Image.open(filename)
        
        #metadata dict
        metadata = _o_image.tag_v2.as_dict()
        self.metadata = metadata
        
        #image
        data = np.array(_o_image)
        self.data = data
    
    def get_fits_data(self):
        filename = self.filename
        pass

    def get_tiff_metadata(self, selected_infos):

        _metadata = self.metadata

        # acquisition time
        try: # new format
            acquisition_time_raw = _metadata[65000][0]
        except: 
            acquisition_time_raw = _metadata[279][0]
        acquisition_time = time.ctime(acquisition_time_raw)
        selected_infos['acquisition_time']['value'] = acquisition_time
        
        # acquisition duration
        try: 
            valueacquisition_duration_raw = _metadata[65021][0]
            [name, value] = acquisition_duration_raw.split(':')
        except:
            value = 'N/A'
        selected_infos['acquisition_duration']['value'] = value
        
        # image size
        try:
            sizeX_raw = _metadata[65028][0]
            [nameX, valueX] = sizeX_raw.split(':')
        except:
            valueX = _metadata[256]
        try:
            sizeY_raw = _metadata[65029][0]
            [nameY, valueY] = sizeY_raw.split(':')
        except:
            valueY = _metadata[257]
        image_size = "{}x{}".format(valueX, valueY)
        selected_infos['image_size']['value'] = image_size
        
        # image type
        bits = _metadata[258][0]
        selected_infos['image_type']['value'] = "{} bits".format(bits)

        self.metadata = selected_infos
    
    def get_fits_metadata(self, filename):
        pass