try:
    import PyQt4
    import PyQt4.QtGui as QtGui
    import PyQt4.QtCore as QtCore
    from PyQt4.QtGui import QMainWindow
    from PyQt4.QtGui import QApplication         
except:
    import PyQt5
    import PyQt5.QtGui as QtGui
    import PyQt5.QtCore as QtCore
    from PyQt5.QtWidgets import QMainWindow
    from PyQt5.QtWidgets import QApplication

import numpy as np

from ibeatles.interfaces.ui_fittingStoryTable import Ui_MainWindow as UiMainWindow
from ibeatles.table_dictionary.table_fitting_story_dictionary_handler import TableFittingStoryDictionaryHandler
from ibeatles.utilities.status import Status


class CreateFittingStoryLauncher(object):
    
    def __init__(self, parent=None):
        self.parent = parent
        
        if self.parent.fitting_story_ui == None:
            fitting_story_window = FittingStoryWindow(parent=parent)
            fitting_story_window.show()
            self.parent.fitting_story_ui = fitting_story_window
        
        else:
            self.parent.fitting_story_ui.setFocus()
            self.parent.fitting_story_ui.activateWindow()
            
            
class FittingStoryWindow(QMainWindow):
    
    list_column_tag = ['d_spacing',
                       'sigma',
                       'alpha',
                       'a1',
                       'a2',
                       'a5',
                       'a6',
                       ]
    
    def __init__(self, parent=None):
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui= UiMainWindow()
        self.ui.setupUi(self)
        
        self.init_widgets()
        self.fill_table()
        
    def init_widgets(self):
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/MPL Toolbar/up_arrow.png/"))
        self.ui.up_button.setIcon(QtGui.QIcon(icon))

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/MPL Toolbar/down_arrow.png/"))
        self.ui.down_button.setIcon(QtGui.QIcon(icon))
        
    def clear_table(self):
        nbr_row = self.ui.story_table.rowCount()
        for _row in np.arange(nbr_row):
            self.ui.story_table.removeRow(0)
        
    def fill_table(self):
        if self.parent.table_fitting_story_dictionary == {}:
            o_table = TableFittingStoryDictionaryHandler(parent=self.parent)
            o_table.initialize_table()
            
        table_fitting_story_dictionary = self.parent.table_fitting_story_dictionary
        
        story_table = self.ui.story_table
        
        self.clear_table()
        for _index in table_fitting_story_dictionary.keys():
            story_table.insertRow(_index)
                        
            _entry = table_fitting_story_dictionary[_index]
            
            _status_of_row = _entry['progress']
            if _status_of_row == Status.in_progress:
                _color = QtGui.QColor(0,255,0, alpha=255)
            elif _status_of_row == Status.completed:
                _color = QtGui.QColor(0, 0, 255, alpha=255)
            else:
                _color = QtGui.QColor(0, 0, 0)
            
            #_item = self.set_item(text=str(_index+1))
            #_item.setTextColor(_color)
            #story_table.setItem(_index, 0, _item)
                        
            for _index_tag, _tag in enumerate(self.list_column_tag):
                _widget = self.set_widget(status=_entry[_tag])
                story_table.setCellWidget(_index, _index_tag, _widget)

    def set_item(self, text=''):
        _item = QtGui.QTableWidgetItem(text)
        return _item

    def set_widget(self, status=False):
        _layout = QtGui.QHBoxLayout()
        _widget = QtGui.QCheckBox()
        _widget.setChecked(status)
        _layout.addStretch()
        _layout.addWidget(_widget)
        _layout.addStretch()
        _new_widget = QtGui.QWidget()
        _new_widget.setLayout(_layout)
        return _new_widget
        
    def add_row_button_clicked(self):
        pass
    
    def remove_row_button_clicked(self):
        pass
    
    def start_fitting_button_clicked(self):
        pass

    def move_row_up_clicked(self):
        pass
    
    def move_row_down_clicked(self):
        pass