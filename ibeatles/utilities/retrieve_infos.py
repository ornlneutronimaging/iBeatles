import os
import time


class RetrieveInfos(object):

    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type


class RetrieveDisplayFileInfos(RetrieveInfos):
    
    def update(self):
        pass
        
        
class RetrieveGeneralFileInfos(RetrieveInfos):
    
    general_infos = {'number_of_files': {'name': 'Number of Files',
                                         'value': -1 },
                     'time_stamp_files': {'name': 'Acquisition Time of Files',
                                               'value': -1},
                     'size_mb': {'name': 'Individual File Size (MB)',
                                   'value': ''},
                     'total_size_folder': {'name': 'Total Size of Folder (MB)',
                                           'value': ''},
                     }
                     

    def update(self):   
        data_files = self.parent.data_files[self.data_type]
        folder = self.parent.data_metadata[self.data_type]['folder']
        
        _nbr_files = len(data_files)
        self.general_infos['number_of_files']['value'] = _nbr_files
        
        _first_file = data_files[0]
        _timestamp_first_file = self.get_formated_time(folder + _first_file)
        self.general_infos['time_stamp_files']['value'] = _timestamp_first_file
        
        _size_of_one_file_kb = float(os.path.getsize(folder + _first_file))
        _file_size_mb = "{:.2f}".format(_size_of_one_file_kb / 1000000.0)
        self.general_infos['size_mb']['value'] = _file_size_mb
        
        _total_size_mb = _size_of_one_file_kb * _nbr_files / 1000000.0
        _total_size_mb = "{:.2f}".format(_total_size_mb)
        self.general_infos['total_size_folder']['value'] = _total_size_mb
        
        self.display()
        
    
    def get_formated_time(self, full_file_name):    
        return time.strftime('%m/%d/%Y %H:%M:%S', 
                             time.gmtime(os.path.getmtime(full_file_name)))
    
    def display(self):
        text = ''
        for key in self.general_infos:
            text += '<b>{}</b>: {}<br/>'.format(self.general_infos[key]['name'], 
                                      self.general_infos[key]['value'])
            
        self.parent.ui.data_general_infos.setHtml(text)
        
        
        