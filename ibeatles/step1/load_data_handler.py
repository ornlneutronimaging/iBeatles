import sys
import os
import glob
import pprint

import PyQt4.QtGui as QtGui


from ibeatles.load_images import LoadImages



class LoadDataHandler(object):
    

    def __init__(self, parent=None):
        self.parent = parent
        
    
    def load(self, data_type='sample'):
        """
        type = ['sample', 'ob', 'normalized', 'time_spectra']
        """
        
        self.data_type = data_type
        
        mydialog = FileDialog()
        mydialog.setDirectory(self.parent.sample_folder)
        mydialog.exec_()

        selectedFiles = mydialog.filesSelected()
        if selectedFiles:
            if len(selectedFiles) == 1:
                if os.path.isdir(selectedFiles[0]):
                    self.load_directory(selectedFiles[0])
                else:
                    self.load_files(selectedFiles[0])
            else:
                self.load_files(selectedFiles)


    def load_directory(self, folder):
        list_files = glob.glob(folder + '/*.*')
        image_type = self.get_image_type(list_files)
        o_load_image = LoadImages(image_ext = image_type, folder = folder)
        image_array = o_load_image.image_array
    
    
    def load_files(self, files):
        print("I am a list of files")


    def get_image_type(self, list_of_files):
        raw_file, ext = os.path.splitext(list_of_files[0])
        return ext
        

        
class FileDialog(QtGui.QFileDialog):

    selectedFiles = []
    
    def __init__(self, *args):
        QtGui.QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, False)
        self.setFileMode(self.ExistingFiles)
        btns = self.findChildren(QtGui.QPushButton)
        self.openBtn = [x for x in btns if 'open' in str(x.text()).lower()][0]
        self.openBtn.clicked.disconnect()
        self.openBtn.clicked.connect(self.openClicked)
        self.tree = self.findChild(QtGui.QTreeView)

    def openClicked(self):
        inds = self.tree.selectionModel().selectedIndexes()
        files = []
        for i in inds:
            if i.column() == 0:
                files.append(os.path.join(str(self.directory().absolutePath()),str(i.data().toString())))
        self.selectedFiles = files
        self.hide()

    def filesSelected(self):
        return self.selectedFiles