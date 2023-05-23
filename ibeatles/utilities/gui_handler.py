from qtpy.QtWidgets import QApplication
import numpy as np

from ibeatles import DataType, XAxisMode
from ibeatles.session import MaterialMode
from ibeatles.utilities.table_handler import TableHandler


class GuiHandler:

    def __init__(self, parent=None):
        self.parent = parent

    def get_active_tab(self):
        """return either 'sample', 'ob', 'normalization' or 'normalized' """
        top_tab_index = self.parent.ui.tabWidget.currentIndex()

        if top_tab_index == 1:
            return DataType.normalization
        if top_tab_index == 2:
            return DataType.normalized
        if top_tab_index == 0:
            load_data_tab_index = self.parent.ui.load_data_tab.currentIndex()
            if load_data_tab_index == 0:
                return DataType.sample
            if load_data_tab_index == 1:
                return DataType.ob

    def get_material_active_tab(self):
        """
        return either MaterialMode.pre_defined, MaterialMode.custom_method1 or MaterialMode.custom_method2
        """
        top_tab_index = self.parent.ui.material_top_tabWidget.currentIndex()
        if top_tab_index == 0:  # pre-defined
            return MaterialMode.pre_defined

        custom_tab_index = self.parent.ui.material_custom_tabWidget.currentIndex()
        if custom_tab_index == 0:  # method 1
            return MaterialMode.custom_method1

        return MaterialMode.custom_method2

    def set_material_active_tab(self, active_tab_mode=MaterialMode.pre_defined):

        if active_tab_mode == MaterialMode.pre_defined:
            self.parent.ui.material_top_tabWidget.setCurrentIndex(0)
        else:
            self.parent.ui.material_top_tabWidget.setCurrentIndex(1)
            if active_tab_mode == MaterialMode.custom_method1:
                self.parent.ui.material_custom_tabWidget.setCurrentIndex(0)
            else:
                self.parent.ui.material_custom_tabWidget.setCurrentIndex(1)

    @staticmethod
    def collect_table_data(table_ui=None):
        """
        return as a dictionary the content of a tableWidget where the top key is the row number, and
        the under-keys are the names of the columns
        """
        if table_ui is None:
            return None

        o_table = TableHandler(table_ui=table_ui)
        column_names = o_table.get_column_names()
        nbr_column = len(column_names)
        nbr_row = o_table.row_count()

        table = {}
        for _row in np.arange(nbr_row):
            _row_entry = {}
            for _col in np.arange(nbr_column):
                _row_entry[str(column_names[_col])] = o_table.get_item_str_from_cell(row=_row, column=_col)
            table[int(_row)] = _row_entry

        return table, column_names

    @staticmethod
    def fill_table_data(table_ui=None, table_dict=None, column_names=None):
        o_table = TableHandler(table_ui=table_ui)
        o_table.remove_all_rows()
        table_ui.blockSignals(True)
        for _row in table_dict.keys():
            o_table.insert_empty_row(row=int(_row))
            for _col_key in table_dict[_row].keys():
                _col = column_names.index(_col_key)
                _val = table_dict[_row][_col_key]
                if _val is None:
                    _val = ""
                o_table.insert_item(row=int(_row),
                                    column=int(_col),
                                    value=_val)
        table_ui.blockSignals(False)

    def enable_xaxis_button(self, tof_flag=True):
        list_button_ui = self.parent.xaxis_button_ui
        active_type = self.get_active_tab()

        if tof_flag:
            for _key in list_button_ui[active_type]:
                list_button_ui[active_type][_key].setEnabled(True)
        else:
            list_button_ui[active_type]['tof'].setEnabled(False)
            list_button_ui[active_type]['lambda'].setEnabled(False)
            list_button_ui[active_type]['file_index'].setChecked(True)

    def get_xaxis_checked(self, data_type=DataType.sample):
        return self.parent.data_metadata[data_type]['xaxis']

    def xaxis_label(self):
        o_gui = GuiHandler(parent=self.parent)
        data_type = o_gui.get_active_tab()
        button = self.get_xaxis_checked(data_type=data_type)

        if button == 'file_index':
            label = 'File Index'
        elif button == 'tof':
            label = u'TOF (\u00B5s)'
        else:
            label = u'\u03BB (\u212B)'

        if data_type == 'sample':
            plot_ui = self.parent.ui.bragg_edge_plot
        elif data_type == 'ob':
            plot_ui = self.parent.ui.ob_bragg_edge_plot
        else:
            plot_ui = self.parent.ui.normalized_bragg_edge_plot

        plot_ui.setLabel('bottom', label)

    def get_text(self, ui=None):
        if ui is None:
            return ''
        return str(ui.text())

    def get_index_selected(self, ui=None):
        if ui is None:
            return -1
        return ui.currentIndex()

    def set_text(self, value='', ui=None):
        if ui is None:
            return
        ui.setText(value)

    def set_index_selected(self, index=-1, ui=None):
        if ui is None:
            return
        ui.setCurrentIndex(index)

    def get_text_selected(self, ui=None):
        if ui is None:
            return ''
        return str(ui.currentText())

    def get_step2_xaxis_checked(self):
        return self.parent.data_metadata[DataType.normalization]['xaxis']

    def update_bragg_peak_scrollbar(self, xaxis_mode=XAxisMode.file_index_mode, force_hide_widgets=False):

        list_label_ui = [self.parent.hkl_scrollbar_ui['label'][key] for key in self.parent.hkl_scrollbar_ui['label'].keys()]
        list_widget_ui = [self.parent.hkl_scrollbar_ui['widget'][key] for key in
                          self.parent.hkl_scrollbar_ui['widget'].keys()]

        list_ui = [*list_label_ui, *list_widget_ui]

        for _ui in list_ui:
            _ui.blockSignals(True)

        if force_hide_widgets:
            for _ui in list_ui:
                _ui.setEnabled(False)
            return

        if xaxis_mode in (XAxisMode.file_index_mode, XAxisMode.tof_mode):
            is_enable = False
        else:
            is_enable = True

        for _ui in list_ui:
            _ui.setEnabled(is_enable)

        for _ui in list_ui:
            _ui.blockSignals(False)
