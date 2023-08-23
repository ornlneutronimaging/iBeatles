from qtpy.QtWidgets import QMainWindow, QMenu, QApplication
from qtpy import QtGui, QtCore
import numpy as np

from ibeatles.fitting.fitting_handler import FittingHandler
from ibeatles.fitting.filling_table_handler import FillingTableHandler
from ibeatles.fitting.kropff.fitting_parameters_viewer_editor_handler import FittingParametersViewerEditorHandler
from ibeatles import load_ui
from ibeatles.fitting.march_dollase.event_handler import EventHandler
from ibeatles.fitting.kropff import SessionSubKeys


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
        self.setWindowTitle("Check/Set Variables")

        self.kropff_fitting_table = self.grand_parent.kropff_table_dictionary

        self.init_widgets()
        self.init_table()
        self.fill_table()

    def eventFilter(self, object, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.update_table()
        return False

    def init_table(self):
        fitting_selection = self.grand_parent.fitting_selection

        # print(fitting_selection)
        nbr_row = fitting_selection['nbr_row']
        nbr_column = fitting_selection['nbr_column']

        self.nbr_column = nbr_column
        self.nbr_row = nbr_row

        # selection table
        self.ui.variable_table.setColumnCount(nbr_column)
        self.ui.variable_table.setRowCount(nbr_row)

        # set size of cells
        value = int(self.ui.advanced_selection_cell_size_slider.value())
        self.selection_cell_size_changed(value)

    def init_widgets(self):
        self.ui.lambda_hkl_button.setText(u'\u03BB\u2095\u2096\u2097')
        self.ui.tau_button.setText(u'\u03c4')
        self.ui.sigma_button.setText(u'\u03c3')
        # self.ui.fixed_label.setStyleSheet("background-color: green")
        # self.ui.locked_label.setStyleSheet("background-color: green")
        # self.ui.active_label.setStyleSheet("background-color: green")

    def fill_table(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        variable_selected = self.get_variable_selected()
        o_handler = FittingParametersViewerEditorHandler(grand_parent=self.grand_parent,
                                                         parent=self)
        o_handler.populate_table_with_variable(variable=variable_selected)
        QApplication.restoreOverrideCursor()

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
        o_handler = FittingParametersViewerEditorHandler(grand_parent=self.grand_parent,
                                                         parent=self)
        o_handler.populate_table_with_variable(variable=variable_selected)

        # o_filling_table = FillingTableHandler(grand_parent=self.grand_parent,
        #                                       parent=self.parent)
        # self.grand_parent.fitting_ui.ui.value_table.blockSignals(True)
        # o_filling_table.fill_table()
        # self.grand_parent.fitting_ui.ui.value_table.blockSignals(False)
        QApplication.restoreOverrideCursor()

    def get_variable_selected(self):
        """
        returns the button checked at the top of the window
        """
        if self.ui.lambda_hkl_button.isChecked():
            return SessionSubKeys.lambda_hkl
        elif self.ui.sigma_button.isChecked():
            return SessionSubKeys.sigma
        elif self.ui.tau_button.isChecked():
            return SessionSubKeys.tau
        else:
            raise NotImplementedError("variable requested not supported!")

    def apply_new_value_to_selection(self):
        variable_selected = self.get_variable_selected()
        selection = self.grand_parent.fitting_set_variables_ui.ui.variable_table.selectedRanges()
        o_handler = FittingParametersViewerEditorHandler(grand_parent=self.grand_parent)
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

    def save_and_quit_clicked(self):
        print("save and qui application")
        self.close()

    def closeEvent(self, event=None):
        self.grand_parent.kropff_fitting_parameters_viewer_editor_ui = None


class VariableTableHandler:

    def __init__(self, grand_parent=None):
        self.grand_parent = grand_parent

    def right_click(self, position=None):
        menu = QMenu(self.grand_parent)

        _lock = menu.addAction("Lock Selection")
        _unlock = menu.addAction("Unlock Selection")
        menu.addSeparator()
        _median = menu.addAction("Replace by median of surrounding pixels")

        action = menu.exec_(QtGui.QCursor.pos())

        if action == _lock:
            self.lock_selection()
        elif action == _unlock:
            self.unlock_selection()
        elif action == _median:
            self.replace_by_median_of_surrounding_pixels()

    def replace_by_median_of_surrounding_pixels(self):
        print("in replace by median of surrounding pixels!")
        #FIXME

    def set_fixed_status_of_selection(self, state=True):
        selection = self.grand_parent.fitting_set_variables_ui.ui.variable_table.selectedRanges()
        table_dictionary = self.grand_parent.march_table_dictionary
        nbr_row = self.grand_parent.fitting_set_variables_ui.nbr_row
        o_handler = FittingParametersViewerEditorHandler(grand_parent=self.grand_parent)
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

    # def activate_selection(self):
    #     QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
    #     self.change_state_of_bins(name='active', state=True)
    #     self.update_fitting_ui(name='active')
    #     self.update_advanced_selection_ui(name='active')
    #     self.grand_parent.fitting_ui.update_bragg_edge_plot()
    #     QApplication.restoreOverrideCursor()
    #
    # def deactivate_selection(self):
    #     QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
    #     self.change_state_of_bins(name='active', state=False)
    #     self.update_fitting_ui(name='active')
    #     self.update_advanced_selection_ui(name='active')
    #     self.grand_parent.fitting_ui.update_bragg_edge_plot()
    #     QApplication.restoreOverrideCursor()

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
