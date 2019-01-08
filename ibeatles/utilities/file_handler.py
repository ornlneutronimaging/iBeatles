import os
#import pyfits
import numpy as np


class FileHandler(object):
    
    @classmethod
    def get_parent_folder(cls, full_folder):
        folders_split = full_folder.split('/')
        return folders_split[-2]
    
    @classmethod
    def get_base_filename(cls, full_file_name):
        return os.path.basename(full_file_name)
    
    @classmethod
    def retrieve_ascii_contain(cls, full_file_name):
        file_contain = []
        with open(full_file_name) as f:
            file_contain = f.read()
        return file_contain

    @classmethod
    def cleanup_list_of_files(cls, list_of_files=[], base_number=5):
        '''Will only keep the files that have the same number of character as
        the first n files'''
        if list_of_files == []:
            return []
        
        len_base_files = []
        for _file in list_of_files[0: base_number]:
            len_base_files.append(len(_file))
            
        # make sure all the length of the base number files match
        set_len_base_files = set(len_base_files)
        if len(set_len_base_files) > 1:
            raise ValueError("Format Input File Do Not Match!")
        
        len_file = len_base_files[0]
        final_list = []
        for _file in list_of_files:
            if len(_file) == len_file:
                final_list.append(_file)
                
        return final_list
    
    @classmethod
    def make_fits(cls, data=[], filename=''):
        hdu = pyfits.PrimaryHDU(data)
        hdulist = pyfits.HDUList([hdu])
        hdulist.writeto(filename)
        hdulist.close()    
        
    @classmethod
    def make_ascii_file(cls, metadata=[], data=[], output_file_name='', sep=','):
        f = open(output_file_name, 'w')
        for _meta in metadata:
            _line = _meta + "\n"
            f.write(_line)
            
        if len(np.shape(data)) > 1:
            for _data in data:
                _str_data = [str(_value) for _value in _data]
                _line = sep.join(_str_data) + "\n"
                f.write(_line)
        else:
            _str_data = [str(_value) + "\n" for _value in data]
            for _data in _str_data:
                f.write(_data)
           
        f.close()    