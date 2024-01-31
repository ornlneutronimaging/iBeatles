from qtpy.QtWidgets import QMainWindow, QMenu, QApplication
from qtpy import QtGui, QtCore
import numpy as np
import logging

from src.ibeatles.utilities.bins import create_list_of_bins_from_selection, create_list_of_surrounding_bins, \
    convert_bins_to_keys
from src.ibeatles import load_ui

from src.ibeatles.fitting.filling_table_handler import FillingTableHandler
from src.ibeatles.fitting.kropff.fitting_parameters_viewer_editor_handler import FittingParametersViewerEditorHandler
from src.ibeatles.fitting.kropff import SessionSubKeys
from src.ibeatles.utilities.table_handler import TableHandler
from src.ibeatles.utilities.array_utilities import calculate_median
from src.ibeatles.fitting.kropff.get import Get


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

        self.kropff_table_dictionary = self.grand_parent.kropff_table_dictionary

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

    def fill_table(self):
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        o_get = Get(parent=self)
        variable_selected = o_get.variable_selected()
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
        o_get = Get(parent=self)
        variable_selected = o_get.variable_selected()
        o_handler = FittingParametersViewerEditorHandler(grand_parent=self.grand_parent,
                                                         parent=self)
        o_handler.populate_table_with_variable(variable=variable_selected)

        # o_filling_table = FillingTableHandler(grand_parent=self.grand_parent,
        #                                       parent=self.parent)
        # self.grand_parent.fitting_ui.ui.value_table.blockSignals(True)
        # o_filling_table.fill_table()
        # self.grand_parent.fitting_ui.ui.value_table.blockSignals(False)
        QApplication.restoreOverrideCursor()

    def apply_new_value_to_selection(self):
        o_get = Get(parent=self)
        variable_selected = o_get.variable_selected()
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
        o_variable = VariableTableHandler(grand_grand_parent=self.grand_parent,
                                          grand_parent=self.parent,
                                          parent=self,
                                          )
        o_variable.right_click(position=position)

    def variable_table_cell_changed(self, row, column):
        o_handler = FittingParametersViewerEditorHandler(parent=self,
                                                         grand_parent=self.grand_parent)
        o_handler.variable_cell_manual_changed(row=row, column=column)

    def save_and_quit_clicked(self):
        logging.info("Saving fitting parameters back into fitting tab!")
        self.grand_parent.kropff_table_dictionary = self.kropff_table_dictionary
        o_fill = FillingTableHandler(parent=self.parent,
                                     grand_parent=self.grand_parent)
        o_fill.fill_kropff_bragg_peak_table()
        self.close()

    def closeEvent(self, event=None):
        self.grand_parent.kropff_fitting_parameters_viewer_editor_ui = None


class VariableTableHandler:

    nbr_row = None
    nbr_column = None

    def __init__(self, grand_grand_parent=None, grand_parent=None, parent=None):
        self.grand_grand_parent = grand_grand_parent
        self.grand_parent = grand_parent
        self.parent = parent

        self.nbr_column = self.parent.nbr_column
        self.nbr_row = self.parent.nbr_row

    def right_click(self, position=None):
        menu = QMenu(self.grand_parent)

        # checking selection and if any, enabled buttons
        o_table = TableHandler(table_ui=self.parent.ui.variable_table)
        current_selection = o_table.get_selection()

        state_button = True if len(current_selection) > 0 else False

        _lock = menu.addAction("Lock Selection")
        _lock.setEnabled(state_button)
        _unlock = menu.addAction("Unlock and replace by median of surrounding pixels")
        _unlock.setEnabled(state_button)

        action = menu.exec_(QtGui.QCursor.pos())

        if action == _lock:
            self.lock_selection()
        elif action == _unlock:
            self.unlock_selection()
            self.replace_by_median_of_surrounding_pixels()

    def replace_by_median_of_surrounding_pixels(self):
        """
        replace all the pixels selected by the median of the surrounding pixels and
        automatically lock that cell
        """
        o_table = TableHandler(table_ui=self.parent.ui.variable_table)
        all_selection = o_table.get_selection()

        table_dictionary = self.parent.kropff_table_dictionary

        logging.info("replace by median of surrounding pixels")

        for _selection in all_selection:
            top_row = _selection.topRow()
            bottom_row = _selection.bottomRow()
            left_column = _selection.leftColumn()
            right_column = _selection.rightColumn()

            # make individual list of bins to work on
            list_bins = create_list_of_bins_from_selection(top_row=top_row,
                                                           bottom_row=bottom_row,
                                                           left_column=left_column,
                                                           right_column=right_column)

            logging.info(f"-> list_bins: {list_bins}")
            for central_bin in list_bins:

                [central_key] = convert_bins_to_keys(list_of_bins=[central_bin],
                                                     full_bin_height=self.nbr_row)

                if self.parent.kropff_table_dictionary[central_key][SessionSubKeys.lock]:
                    logging.info(f"-> bin #{central_key} is locked and won't be modified!")
                    # we don't do anything if the cell is locked !
                    continue

                surrounding_bins = create_list_of_surrounding_bins(central_bin=central_bin,
                                                                   full_bin_width=self.nbr_column,
                                                                   full_bin_height=self.nbr_row)

                surrounding_keys = convert_bins_to_keys(list_of_bins=surrounding_bins,
                                                        full_bin_height=self.nbr_row)

                list_lambda_value = []
                list_tau_value = []
                list_sigma_value = []

                list_lambda_error = []
                list_tau_error = []
                list_sigma_error = []

                for _key in surrounding_keys:

                    list_lambda_value.append(table_dictionary[_key][SessionSubKeys.lambda_hkl]['val'])
                    list_tau_value.append(table_dictionary[_key][SessionSubKeys.tau]['val'])
                    list_sigma_value.append(table_dictionary[_key][SessionSubKeys.sigma]['val'])

                    list_lambda_error.append(table_dictionary[_key][SessionSubKeys.lambda_hkl]['err'])
                    list_tau_error.append(table_dictionary[_key][SessionSubKeys.tau]['err'])
                    list_sigma_error.append(table_dictionary[_key][SessionSubKeys.sigma]['err'])

                new_lambda_value = calculate_median(array_of_value=list_lambda_value)
                new_lambda_error = calculate_median(array_of_value=list_lambda_error)

                new_tau_value = calculate_median(array_of_value=list_tau_value)
                new_tau_error = calculate_median(array_of_value=list_tau_error)

                new_sigma_value = calculate_median(array_of_value=list_sigma_value)
                new_sigma_error = calculate_median(array_of_value=list_sigma_error)

                self.parent.kropff_table_dictionary[central_key][SessionSubKeys.lambda_hkl]['val'] = new_lambda_value
                self.parent.kropff_table_dictionary[central_key][SessionSubKeys.lambda_hkl]['err'] = new_lambda_error

                self.parent.kropff_table_dictionary[central_key][SessionSubKeys.tau]['val'] = new_tau_value
                self.parent.kropff_table_dictionary[central_key][SessionSubKeys.tau]['err'] = new_tau_error

                self.parent.kropff_table_dictionary[central_key][SessionSubKeys.sigma]['val'] = new_sigma_value
                self.parent.kropff_table_dictionary[central_key][SessionSubKeys.sigma]['err'] = new_sigma_error

                self.parent.kropff_table_dictionary[central_key][SessionSubKeys.lock] = True

        # refresh table
        self.parent.update_table()

        # clear selection
        o_table = TableHandler(table_ui=self.parent.ui.variable_table)
        o_table.select_everything(False)

    def set_fixed_status_of_selection(self, state=True):
        selection = self.grand_parent.fitting_set_variables_ui.ui.variable_table.selectedRanges()
        table_dictionary = self.grand_parent.march_table_dictionary
        nbr_row = self.grand_parent.fitting_set_variables_ui.nbr_row

        o_get = Get(parent=self.parent)
        variable_selected = o_get.variable_selected()

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

    def lock_selection(self):
        self.change_state_of_bins(name='lock', state=True)
        self.parent.update_table()
        # o_table = TableHandler(table_ui=self.parent.ui.variable_table)
        # o_table.select_everything(False)

    def unlock_selection(self):
        self.change_state_of_bins(name='lock', state=False)
        self.parent.update_table()
        # o_table = TableHandler(table_ui=self.parent.ui.variable_table)
        # o_table.select_everything(False)

    def change_state_of_bins(self, name='lock', state=True):

        o_table = TableHandler(table_ui=self.parent.ui.variable_table)
        all_selection = o_table.get_selection()
        # table_dictionary = self.parent.kropff_table_dictionary
        logging.info("Changing lock state of selection")

        for _selection in all_selection:

            top_row = _selection.topRow()
            bottom_row = _selection.bottomRow()
            left_column = _selection.leftColumn()
            right_column = _selection.rightColumn()

            # make individual list of bins to work on
            list_bins = create_list_of_bins_from_selection(top_row=top_row,
                                                           bottom_row=bottom_row,
                                                           left_column=left_column,
                                                           right_column=right_column)

            list_keys = convert_bins_to_keys(list_of_bins=list_bins,
                                             full_bin_height=self.nbr_row)

            for _key in list_keys:
                self.parent.kropff_table_dictionary[_key][SessionSubKeys.lock] = state
