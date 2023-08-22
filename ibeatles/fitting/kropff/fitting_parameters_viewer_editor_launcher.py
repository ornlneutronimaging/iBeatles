from qtpy.QtWidgets import QMainWindow, QMenu, QApplication
from qtpy import QtGui, QtCore
import numpy as np

from ibeatles.fitting.set_fitting_variables_handler import SetFittingVariablesHandler
from ibeatles.fitting.filling_table_handler import FillingTableHandler
from ibeatles import load_ui
from ibeatles.fitting.march_dollase.event_handler import EventHandler


class FittingParametersViewerEditorLauncher:

    def __init__(self, grand_parent=None, parent=None):
        self.grand_parent = grand_parent

        if self.grand_parent.kropff_fitting_parameters_viewer_editor_ui is None:
            set_variables_window = FittingParametersViewerEditor(grand_parent=grand_parent,
                                                                 parent=parent)
            self.grand_parent.kropff_fitting_parameters_viewer_editor_ui = set_variables_window
            set_variables_window.show()
        else:
            self.grand_parent.kropff_fitting_parameters_viewer_editor_ui.setFocus()
            self.grand_parent.kropff_fitting_parameters_viewer_editor_ui.activateWindow()


class FittingParametersViewerEditor(QMainWindow):
    advanced_mode = True
    nbr_column = -1
    nbr_row = -1

    def __init__(self, grand_parent=None, parent=None):

        self.grand_parent = grand_parent
        self.parent = parent
        QMainWindow.__init__(self, parent=grand_parent)
        self.ui = load_ui('ui_fittingVariablesKropff.ui', baseinstance=self)
        # self.ui = UiMainWindow()
        # self.ui.setupUi(self)
        self.setWindowTitle("Check/Set Variables")
        # self.installEventFilter(self)

        kropff_fitting_table = self.grand_parent.kropff_table_dictionary
        # print(kropff_fitting_table)

        list_key = list(kropff_fitting_table.keys())
        print(kropff_fitting_table[list_key[0]])

        self.init_widgets()
        self.init_table()

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.update_table()
        return False

    def init_table(self):
        fitting_selection = self.grand_parent.fitting_selection

        print(fitting_selection)
        nbr_row = fitting_selection['nbr_row']
        nbr_column = fitting_selection['nbr_column']

        self.nbr_column = nbr_column
        self.nbr_row = nbr_row

        # selection table
        self.ui.variable_table.setColumnCount(nbr_column)
        self.ui.variable_table.setRowCount(nbr_row)

        # set size of cells
        value = int(self.ui.advanced_selection_cell_size_slider.value())
        # self.selection_cell_size_changed(value)

    def init_widgets(self):
        pass
        # self.ui.fixed_label.setStyleSheet("background-color: green")
        # self.ui.locked_label.setStyleSheet("background-color: green")
        # self.ui.active_label.setStyleSheet("background-color: green")

    def selection_cell_size_changed(self, value):
        nbr_row = self.ui.variable_table.rowCount()
        nbr_column = self.ui.variable_table.columnCount()

        for _row in np.arange(nbr_row):
            self.ui.variable_table.setRowHeight(_row, value)
            # self.ui.colorscale_table.setRowHeight(_row, value)

        for _col in np.arange(nbr_column):
            self.ui.variable_table.setColumnWidth(_col, value)
            # self.ui.colorscale_table.setColumnWidth(_col, value)

    def update_table(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        variable_selected = self.get_variable_selected()
        o_handler = SetFittingVariablesHandler(grand_parent=self.grand_parent)
        o_handler.populate_table_with_variable(variable=variable_selected)
        o_filling_table = FillingTableHandler(grand_parent=self.grand_parent,
                                              parent=self.parent)
        self.grand_parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.grand_parent.fitting_ui.ui.value_table.blockSignals(False)
        QApplication.restoreOverrideCursor()

    def get_variable_selected(self):
        if self.ui.d_spacing_button.isChecked():
            return 'd_spacing'
        elif self.ui.sigma_button.isChecked():
            return 'sigma'
        elif self.ui.alpha_button.isChecked():
            return 'alpha'
        elif self.ui.a1_button.isChecked():
            return 'a1'
        elif self.ui.a2_button.isChecked():
            return 'a2'
        elif self.ui.a5_button.isChecked():
            return 'a5'
        elif self.ui.a6_button.isChecked():
            return 'a6'

    def apply_new_value_to_selection(self):
        variable_selected = self.get_variable_selected()
        selection = self.grand_parent.fitting_set_variables_ui.ui.variable_table.selectedRanges()
        o_handler = SetFittingVariablesHandler(grand_parent=self.grand_parent)
        new_variable = float(str(self.grand_parent.fitting_set_variables_ui.ui.new_value_text_edit.text()))
        o_handler.set_new_value_to_selected_bins(selection=selection,
                                                 variable_name=variable_selected,
                                                 variable_value=new_variable,
                                                 table_nbr_row=self.nbr_row)
        self.grand_parent.fitting_set_variables_ui.ui.new_value_text_edit.setText('')
        o_filling_table = FillingTableHandler(grand_parent=self.grand_parent,
                                              parent=self.parent)
        self.grand_parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.grand_parent.fitting_ui.ui.value_table.blockSignals(False)

    def variable_table_right_click(self, position):
        o_variable = VariableTableHandler(grand_parent=self.grand_parent)
        o_variable.right_click(position=position)

    def closeEvent(self, event=None):
        self.grand_parent.kropff_fitting_parameters_viewer_editor_ui = None


class VariableTableHandler(object):

    def __init__(self, grand_parent=None):
        self.grand_parent = grand_parent

    def right_click(self, position=None):
        menu = QMenu(self.grand_parent)

        _activate = menu.addAction("Activate Selection")
        _deactivate = menu.addAction("Deactivate Selection")
        menu.addSeparator()
        _lock = menu.addAction("Lock Selection")
        _unlock = menu.addAction("Unlock Selection")
        menu.addSeparator()
        _fixed = menu.addAction("Fixed Selection")
        _unfixed = menu.addAction("Unfixed Selection")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == _lock:
            self.lock_selection()
        elif action == _unlock:
            self.unlock_selection()
        elif action == _activate:
            self.activate_selection()
        elif action == _deactivate:
            self.deactivate_selection()
        elif action == _fixed:
            self.fixed_selection()
        elif action == _unfixed:
            self.unfixed_selection()

    def set_fixed_status_of_selection(self, state=True):
        selection = self.grand_parent.fitting_set_variables_ui.ui.variable_table.selectedRanges()
        table_dictionary = self.grand_parent.march_table_dictionary
        nbr_row = self.grand_parent.fitting_set_variables_ui.nbr_row
        o_handler = SetFittingVariablesHandler(grand_parent=self.grand_parent)
        variable_selected = o_handler.get_variable_selected()

        for _select in selection:
            _left_column = _select.leftColumn()
            _right_column = _select.rightColumn()
            _top_row = _select.topRow()
            _bottom_row = _select.bottomRow()
            for _row in np.arange(_top_row, _bottom_row + 1):
                for _col in np.arange(_left_column, _right_column + 1):
                    _index = _row + _col * nbr_row
                    table_dictionary[str(_index)][variable_selected]['fixed'] = state

            # remove selection markers
            self.grand_parent.fitting_set_variables_ui.ui.variable_table.setRangeSelected(_select, False)

        self.grand_parent.march_table_dictionary = table_dictionary
        self.grand_parent.fitting_set_variables_ui.update_table()

    def fixed_selection(self):
        self.set_fixed_status_of_selection(state=True)

    def unfixed_selection(self):
        self.set_fixed_status_of_selection(state=False)

    def activate_selection(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.change_state_of_bins(name='active', state=True)
        self.update_fitting_ui(name='active')
        self.update_advanced_selection_ui(name='active')
        self.grand_parent.fitting_ui.update_bragg_edge_plot()
        QApplication.restoreOverrideCursor()

    def deactivate_selection(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.change_state_of_bins(name='active', state=False)
        self.update_fitting_ui(name='active')
        self.update_advanced_selection_ui(name='active')
        self.grand_parent.fitting_ui.update_bragg_edge_plot()
        QApplication.restoreOverrideCursor()

    def lock_selection(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.change_state_of_bins(name='lock', state=True)
        self.update_fitting_ui(name='lock')
        self.update_advanced_selection_ui(name='lock')
        self.grand_parent.fitting_ui.update_bragg_edge_plot()
        QApplication.restoreOverrideCursor()

    def unlock_selection(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        self.change_state_of_bins(name='lock', state=False)
        self.update_fitting_ui(name='lock')
        self.update_advanced_selection_ui(name='lock')
        self.grand_parent.fitting_ui.update_bragg_edge_plot()
        QApplication.restoreOverrideCursor()

    def change_state_of_bins(self, name='lock', state=True):
        selection = self.grand_parent.fitting_set_variables_ui.ui.variable_table.selectedRanges()
        table_dictionary = self.grand_parent.march_table_dictionary
        nbr_row = self.grand_parent.fitting_set_variables_ui.nbr_row

        for _select in selection:
            _left_column = _select.leftColumn()
            _right_column = _select.rightColumn()
            _top_row = _select.topRow()
            _bottom_row = _select.bottomRow()
            for _row in np.arange(_top_row, _bottom_row + 1):
                for _col in np.arange(_left_column, _right_column + 1):
                    _index = _row + _col * nbr_row
                    table_dictionary[str(_index)][name] = state

            # remove selection markers
            self.grand_parent.fitting_set_variables_ui.ui.variable_table.setRangeSelected(_select, False)

        self.grand_parent.march_table_dictionary = table_dictionary
        self.grand_parent.fitting_set_variables_ui.update_table()

    def update_fitting_ui(self, name='active'):
        o_event = EventHandler(parent=self.parent,
                               grand_parent=self.grand_parent)
        if name == 'lock':
            o_event.update_image_view_lock()
        elif name == 'active':
            o_event.update_image_view_selection()

        o_filling_table = FillingTableHandler(grand_parent=self.grand_parent)
        self.grand_parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()

        self.grand_parent.fitting_ui.ui.value_table.blockSignals(False)

    def update_advanced_selection_ui(self, name='active'):
        if self.grand_parent.advanced_selection_ui:
            if name == 'lock':
                self.grand_parent.advanced_selection_ui.update_lock_table()
            elif name == 'active':
                self.grand_parent.advanced_selection_ui.update_selected_table()
