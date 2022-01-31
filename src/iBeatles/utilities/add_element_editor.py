from qtpy import QtCore
from qtpy.QtWidgets import QDialog

from ..utilities.gui_handler import GuiHandler
from ..utilities.math_tools import is_float
from .. import load_ui


class AddElement(object):

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):

        _interface = AddElementInterface(parent=self.parent)
        _interface.show()
        self.parent.add_element_editor_ui = _interface


class AddElementInterface(QDialog):
    new_element = {}

    def __init__(self, parent=None):
        self.parent = parent

        QDialog.__init__(self, parent=parent)
        self.ui = load_ui('ui_addElement.ui', baseinstance=self)
        self.setWindowTitle("Add Element Editor")
        self.ui.element_name_error.setVisible(False)

    def element_name_changed(self, current_value):
        self.check_add_widget_state()

    def lattice_changed(self, current_value):
        self.check_add_widget_state()

    def check_add_widget_state(self):
        lattice_value = self.ui.lattice.text()
        if lattice_value.strip() == "":
            self.ui.add.setEnabled(False)
            return

        if not is_float(lattice_value):
            self.ui.add.setEnabled(False)
            return

        current_element_name = str(self.ui.element_name.text())
        list_element_root = self.parent.ui.list_of_elements.findText(current_element_name,
                                                                     QtCore.Qt.MatchCaseSensitive)
        if not (list_element_root == -1):  # element already there
            self.ui.element_name_error.setVisible(True)
            self.ui.add.setEnabled(False)
            return

        else:
            self.ui.element_name_error.setVisible(False)
            self.ui.add.setEnabled(True)
            return

    def retrieve_metadata(self):
        o_gui = GuiHandler(parent=self)

        element_name = o_gui.get_text(ui=self.ui.element_name)
        lattice = o_gui.get_text(ui=self.ui.lattice)
        crystal_structure = o_gui.get_text_selected(ui=self.ui.crystal_structure)

        self.new_element = {'element_name': element_name,
                            'lattice': lattice,
                            'crystal_structure': crystal_structure}

    def add_element_to_list_of_elements_widgets(self):
        _element = self.new_element
        self.parent.ui.list_of_elements.addItem(_element['element_name'])
        nbr_element = self.parent.ui.list_of_elements.count()
        self.parent.ui.list_of_elements.setCurrentIndex(nbr_element - 1)
        self.parent.ui.list_of_elements_2.addItem(_element['element_name'])
        self.parent.ui.list_of_elements_2.setCurrentIndex(nbr_element - 1)

    def save_new_element_to_local_list(self):
        _new_element = self.new_element

        _new_entry = {'lattice': _new_element['lattice'],
                      'crystal_structure': _new_element['crystal_structure']}

        self.parent.local_bragg_edge_list[_new_element['element_name']] = _new_entry

    def add_clicked(self):
        self.retrieve_metadata()
        self.save_new_element_to_local_list()
        self.add_element_to_list_of_elements_widgets()
        self.close()
