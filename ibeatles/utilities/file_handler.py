import os


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
    