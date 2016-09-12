import PyQt4.QtGui as QtGui
import sys


class LoadDataHandler(object):
    

    def __init__(self, parent=None):
        self.parent = parent
        
    
    def load(self, type='sample'):
        """
        type = ['sample', 'ob', 'normalized', 'time_spectra']
        """
        
        mydialog = FileDialog()
        mydialog.setFileMode(QtGui.QFileDialog.Directory)
        mydialog.setFileMode(QtGui.QFileDialog.AnyFile)
        filelist = mydialog.getExistingDirectory(self.parent, "select stuff", ".")
        
        
        
class FileDialog(QtGui.QFileDialog):
    def __init__(self, *args):
        QtGui.QFileDialog.__init__(self, *args)
        self.setOption(self.DontUseNativeDialog, True)
        self.setFileMode(self.ExistingFiles)


