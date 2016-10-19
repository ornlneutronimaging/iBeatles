import os


class FileHandler(object):
    
    @classmethod
    def get_parent_folder(cls, full_folder):
        folders_split = full_folder.split('/')
        return folders_split[-2]
    
    @classmethod
    def get_base_filename(cls, full_file_name):
        return os.path.basename(full_file_name)