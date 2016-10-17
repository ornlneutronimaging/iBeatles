class FileHandler(object):
    
    @classmethod
    def get_parent_folder(cls, full_folder):
        folders_split = full_folder.split('/')
        return folders_split[-2]