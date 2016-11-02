import os
import time

from ibeatles.utilities.image_handler import ImageHandler
import matplotlib.pyplot as plt


class RetrieveDataInfos(object):

    def __init__(self, parent=None, data_type='sample'):
        self.parent = parent
        self.data_type = data_type
        
        self.general_infos_ui = {'sample': self.parent.ui.data_general_infos,
                                 'ob':  self.parent.ui.data_general_infos,
                                 'normalized': self.parent.ui.normalized_general_infos}
        
        self.selected_infos_ui = {'sample': self.parent.ui.data_selected_infos,
                                 'ob': self.parent.ui.data_selected_infos,
                                 'normalized': self.parent.ui.normalized_selected_infos}
        
        self.path = self.parent.data_metadata[data_type]['folder']
        
        self.table_ui = {'sample': self.parent.ui.list_sample,
                         'ob': self.parent.ui.list_open_beam,
                         'normalized': self.parent.ui.list_normalized}

        #self.preview_widget = {'sample': self.parent.ui.preview_widget,
                               #'ob': self.parent.ui.preview_widget,
                               #'normalized': self.parent.ui.normalized_preview_widget}

        self.preview_widget = {'sample': self.parent.qmc,
                               'ob': self.parent.qmc,
                               'normalized': self.parent.ui.normalized_preview_widget}

class RetrieveSelectedFileDataInfos(RetrieveDataInfos):
    
    selected_infos = {'acquisition_duration': {'name': "Acquisition Duration",
                                               'value': 0},
                      'acquisition_time': {'name': 'Acquisition Time',
                                           'value': ''},
                      'image_size': {'name': 'Image(s) Size',
                                      'value': '512x512'},
                      'image_type': {'name': 'Image Type',
                                     'value': '16 bits'},
                      'min_counts': {'name': 'min counts',
                                    'value': 0},
                      'max_counts': {'name': 'max counts',
                                     'value': 0}}
    
    data = []
    
    def update(self):
        list_row_selected = self.get_list_row_selected()

        if list_row_selected == []:
            self.selected_infos = {}
            self.data = []
        else:
            list_files_selected = self.get_list_files_selected()
            full_filename = os.path.join(self.path, list_files_selected[0])
            image_handler = ImageHandler(parent=self.parent, 
                                         filename = full_filename)
            self.selected_infos = image_handler.get_metadata(self.selected_infos)
            self.data = image_handler.get_data()
        
        self.display()
        
    def display(self):

        #metadata
        text = ''
        for key in self.selected_infos:
            text += '<b>{}</b>: {}<br/>'.format(self.selected_infos[key]['name'], 
                                      self.selected_infos[key]['value'])
        self.selected_infos_ui[self.data_type].setHtml(text)
        
        #data
        _data = self.data
        
        if _data == []:
            self.preview_widget[self.data_type].clear()
        else:
            img = self.preview_widget[self.data_type].ax1.imshow(_data)
            #img = self.parent.qmc.ax1.imshow(_data)
            cbar = self.preview_widget[self.data_type].fig.colorbar(img)
            #cbar = self.parent.qmc.fig.colorbar(img)
            self.preview_widget[self.data_type].fig.tight_layout()
            #self.parent.qmc.fig.tight_layout()

        self.preview_widget[self.data_type].draw()
        #self.parent.qmc.draw()
        #self.preview_widget[self.data_type].draw()        
        
            
    def get_list_files_selected(self):
        list_files = [str(x.text()) for x in self.table_ui[self.data_type].selectedItems()]
        return list_files
        
    def get_list_row_selected(self):
        selection = self.table_ui[self.data_type].selectedIndexes()
        _list_row_selected = []
        for _index in selection:
            _list_row_selected.append(_index.row())
        return _list_row_selected
        
        
class RetrieveGeneralFileInfos(RetrieveDataInfos):
    
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
        if data_files == []:
            self.general_infos = {} #no files so no infos to display

        else:
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
            
        self.general_infos_ui[self.data_type].setHtml(text)
        
        
        