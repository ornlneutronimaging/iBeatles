from qtpy.QtWidgets import QMainWindow, QApplication
from qtpy import QtCore
import numpy as np
import logging

from .. import load_ui
from .. import DataType

from .fitting_handler import FittingHandler
from .value_table_handler import ValueTableHandler
from .selected_bin_handler import SelectedBinsHandler
from ..table_dictionary.table_dictionary_handler import TableDictionaryHandler
from .filling_table_handler import FillingTableHandler
from src.iBeatles.fitting.march_dollase.fitting_initialization_handler import FittingInitializationHandler
from src.iBeatles.fitting.march_dollase.create_fitting_story_launcher import CreateFittingStoryLauncher
from .initialization import Initialization
from .event_handler import EventHandler
from src.iBeatles.fitting.kropff.event_handler import EventHandler as KropffHandler
from src.iBeatles.fitting.kropff.kropff_automatic_settings_launcher import KropffAutomaticSettingsLauncher
from src.iBeatles.fitting.march_dollase.event_handler import EventHandler as MarchDollaseEventHandler


class FittingLauncher(object):

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.fitting_ui is None:
            fitting_window = FittingWindow(parent=parent)
            fitting_window.show()
            self.parent.fitting_ui = fitting_window
            o_fitting = FittingHandler(grand_parent=self.parent,
                                       parent=self.parent.fitting_ui)
            o_fitting.display_image()
            o_fitting.display_roi()
            o_fitting.fill_table()

            fitting_window.fitting_main_tab_widget_changed()
        else:
            self.parent.fitting_ui.setFocus()
            self.parent.fitting_ui.activateWindow()


class FittingWindow(QMainWindow):

    fitting_lr = None
    is_ready_to_fit = False

    data = []
    # there_is_a_roi = False
    bragg_edge_active_button_status = True  # to make sure active/lock button worked correctly

    list_bins_selected_item = []
    list_bins_locked_item = []

    image_view = None
    bragg_edge_plot = None
    line_view = None

    line_view_fitting = None  # roi selected in binning window
    all_bins_button = None
    indi_bins_button = None

    header_value_tables_match = {0: [0],
                                 1: [1],
                                 2: [2],
                                 3: [3],
                                 4: [4],
                                 5: [5, 6],
                                 6: [7, 8],
                                 7: [9, 10],
                                 8: [11, 12],
                                 9: [13, 14],
                                 10: [15, 16],
                                 11: [17, 18],
                                 12: [19, 20]}

    para_cell_width = 130
    header_table_columns_width = [30, 30, 50, 50, 100,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width,
                                  para_cell_width]
    fitting_table_columns_width = [header_table_columns_width[0],
                                   header_table_columns_width[1],
                                   header_table_columns_width[2],
                                   header_table_columns_width[3],
                                   header_table_columns_width[4],
                                   np.int(header_table_columns_width[5] / 2),
                                   np.int(header_table_columns_width[5] / 2),
                                   np.int(header_table_columns_width[6] / 2),
                                   np.int(header_table_columns_width[6] / 2),
                                   np.int(header_table_columns_width[7] / 2),
                                   np.int(header_table_columns_width[7] / 2),
                                   np.int(header_table_columns_width[8] / 2),
                                   np.int(header_table_columns_width[8] / 2),
                                   np.int(header_table_columns_width[9] / 2),
                                   np.int(header_table_columns_width[9] / 2),
                                   np.int(header_table_columns_width[10] / 2),
                                   np.int(header_table_columns_width[10] / 2),
                                   np.int(header_table_columns_width[11] / 2),
                                   np.int(header_table_columns_width[11] / 2),
                                   np.int(header_table_columns_width[12] / 2),
                                   np.int(header_table_columns_width[12] / 2)]

    # status of alpha and sigma initialization
    sigma_alpha_initialized = False
    initialization_table = {'d_spacing': np.NaN,
                            'alpha': np.NaN,
                            'sigma': np.NaN,
                            'a1': np.NaN,
                            'a2': np.NaN,
                            'a5': np.NaN,
                            'a6': np.NaN}

    bragg_edge_data = {'x_axis': [],
                       'y_axis': []}

    kropff_automatic_threshold_finder_algorithm = None
    kropff_threshold_current_item = None

    def __init__(self, parent=None):

        logging.info("Launching fitting tab!")
        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_fittingWindow.ui', baseinstance=self)
        self.setWindowTitle("5. Fitting")

        o_init = Initialization(parent=self,
                                grand_parent=self.parent)
        o_init.run_all()

        self.check_status_widgets()
        self.parent.data_metadata[DataType.fitting]['ui_accessed'] = True

        x_axis = self.parent.normalized_lambda_bragg_edge_x_axis
        self.bragg_edge_data['x_axis'] = x_axis

    def re_fill_table(self):
        o_fitting = FittingHandler(parent=self,
                                   grand_parent=self.parent)
        o_fitting.fill_table()

    def fitting_main_tab_widget_changed(self, index_tab=-1):
        if index_tab == -1:
            index_tab = self.ui.tabWidget.currentIndex()

        o_fitting = FittingHandler(grand_parent=self.parent,
                                   parent=self)
        o_fitting.display_locked_active_bins()
        if index_tab == 1:
            self.bragg_edge_linear_region_changed()
            o_event = KropffHandler(parent=self,
                                    grand_parent=self.parent)
            o_event.display_bragg_peak_threshold()

        o_fitting_window_event = EventHandler(parent=self,
                                              grand_parent=self.parent)
        o_fitting_window_event.check_widgets()

    # general fitting events

    def mouse_moved_in_image_view(self):
        self.image_view.setFocus(True)

    def hkl_list_changed(self, hkl):
        o_event = EventHandler(parent=self,
                               grand_parent=self.parent)
        o_event.hkl_list_changed(hkl)

    def slider_changed(self):
        o_fitting_handler = FittingHandler(parent=self,
                                           grand_parent=self.parent)
        o_fitting_handler.display_roi()

    def update_bragg_edge_plot(self, update_selection=True):
        o_bin_handler = SelectedBinsHandler(parent=self, grand_parent=self.parent)
        o_bin_handler.update_bragg_edge_plot()
        if update_selection:
            self.bragg_edge_linear_region_changing()
        self.check_state_of_step3_button()

    def bragg_edge_linear_region_changing(self):
        self.is_ready_to_fit = False
        o_event = EventHandler(parent=self,
                               grand_parent=self.parent)
        o_event.bragg_edge_region_changed()
        self.check_status_widgets()

    def bragg_edge_linear_region_changed(self):
        o_table = TableDictionaryHandler(parent=self,
                                         grand_parent=self.parent)
        o_table.clear_y_axis_and_x_axis_from_kropff_table_dictionary()
        self.is_ready_to_fit = False
        o_event = EventHandler(parent=self,
                               grand_parent=self.parent)
        o_event.bragg_edge_region_changed()
        self.check_status_widgets()
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        QApplication.processEvents()
        self.update_kropff_fitting_plot()
        QApplication.restoreOverrideCursor()
        QApplication.processEvents()

    def min_or_max_lambda_manually_changed(self):
        o_event = EventHandler(parent=self,
                               grand_parent=self.parent)
        o_event.min_or_max_lambda_manually_changed()


    def create_fitting_story_checked(self):
        CreateFittingStoryLauncher(parent=self,
                                   grand_parent=self.parent)

    # March-Dollase
    def column_value_table_clicked(self, column):
        o_event = MarchDollaseEventHandler(parent=self,
                                           grand_parent=self.parent)
        o_event.column_value_table_clicked(column)

    def column_header_table_clicked(self, column):
        o_event = MarchDollaseEventHandler(parent=self,
                                           grand_parent=self.parent)
        o_event.column_header_table_clicked(column)

    def resizing_header_table(self, index_column, old_size, new_size):
        o_event = MarchDollaseEventHandler(parent=self,
                                           grand_parent=self.parent)
        o_event.resizing_header_table(index_column, new_size)

    def resizing_value_table(self, index_column, old_size, new_size):
        o_event = MarchDollaseEventHandler(parent=self,
                                           grand_parent=self.parent)
        o_event.resizing_value_table(index_column, new_size)

    def active_button_pressed(self):
        self.parent.display_active_row_flag = True
        self.update_bragg_edge_plot()

    def lock_button_pressed(self):
        self.parent.display_active_row_flag = False
        self.update_bragg_edge_plot()

    def check_status_widgets(self):
        self.check_state_of_step3_button()
        self.check_state_of_step4_button()

    def check_state_of_step3_button(self):
        o_event = MarchDollaseEventHandler(parent=self,
                                           grand_parent=self.parent)
        o_event.check_state_of_step3_button()

    def check_state_of_step4_button(self):
        o_event = MarchDollaseEventHandler(parent=self,
                                           grand_parent=self.parent)
        o_event.check_state_of_step4_button()

    def active_button_state_changed(self, status, row_clicked):
        o_event = MarchDollaseEventHandler(parent=self,
                                           grand_parent=self.parent)
        o_event.active_button_state_changed(row_clicked)

    def mirror_state_of_widgets(self, column=2, row_clicked=0):
        o_event = MarchDollaseEventHandler(parent=self,
                                           grand_parent=self.parent)
        o_event.mirror_state_of_widgets(column=column, row_clicked=row_clicked)

    def lock_button_state_changed(self, status, row_clicked):
        o_event = MarchDollaseEventHandler(parent=self,
                                           grand_parent=self.parent)
        o_event.lock_button_state_changed(status, row_clicked)

    def value_table_right_click(self, position):
        o_table_handler = ValueTableHandler(grand_parent=self.parent, parent=self)
        o_table_handler.right_click(position=position)

    def check_advanced_table_status(self):
        self.is_ready_to_fit = False
        button_status = self.ui.advanced_table_checkBox.isChecked()
        self.advanced_table_clicked(button_status)
        self.check_status_widgets()

    def advanced_table_clicked(self, status):
        self.is_ready_to_fit = False
        QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        o_table_handler = FillingTableHandler(grand_parent=self.parent,
                                              parent=self)
        o_table_handler.set_mode(advanced_mode=status)
        self.check_status_widgets()
        QApplication.restoreOverrideCursor()

    def update_table(self):
        o_filling_table = FillingTableHandler(grand_parent=self.parent,
                                              parent=self)
        self.parent.fitting_ui.ui.value_table.blockSignals(True)
        o_filling_table.fill_table()
        self.parent.fitting_ui.ui.value_table.blockSignals(False)

    def initialize_all_parameters_button_clicked(self):
        o_initialization = FittingInitializationHandler(parent=self,
                                                        grand_parent=self.parent)
        o_initialization.run()

    def initialize_all_parameters_step2(self):
        o_initialization = FittingInitializationHandler(parent=self,
                                                        grand_parent=self.parent)
        o_initialization.finished_up_initialization()

        # activate or not step4 (yes if we were able to initialize correctly all variables)
        self.ui.step4_button.setEnabled(o_initialization.all_variables_initialized)
        self.ui.step4_label.setEnabled(o_initialization.all_variables_initialized)

        self.update_bragg_edge_plot()

    # kropff

    def kropff_check_widgets_helper(self):
        """highlight in green the next button to use"""
        o_event = KropffHandler(parent=self,
                                grand_parent=self.parent)
        o_event.check_widgets_helper()

    def kropff_high_low_bragg_peak_tabs_changed(self, tab_index):
        self.update_kropff_fitting_plot()
        self.update_selected_bins_plot()
        o_event = KropffHandler(parent=self,
                                grand_parent=self.parent)
        o_event.display_bragg_peak_threshold()

    def kropff_automatic_bragg_peak_threshold_finder_clicked(self):
        o_event = KropffHandler(parent=self,
                                grand_parent=self.parent)
        o_event.kropff_automatic_bragg_peak_threshold_finder_clicked()

    def kropff_automatic_bragg_peak_threshold_finder_settings_clicked(self):
        o_kropff = KropffAutomaticSettingsLauncher(parent=self)
        o_kropff.show()

    def kropff_parameters_changed(self):
        o_kropff = KropffHandler(parent=self,
                                 grand_parent=self.parent)
        o_kropff.parameters_changed()

    def update_selected_bins_plot(self):
        o_kropff = SelectedBinsHandler(parent=self, grand_parent=self.parent)
        o_kropff.update_bins_selected()
        o_kropff.update_bragg_edge_plot()

    def update_kropff_fitting_plot(self):
        o_kropff = KropffHandler(parent=self, grand_parent=self.parent)
        o_kropff.update_fitting_plot()
        o_kropff.update_bragg_edge_threshold()

    def kropff_parameters_changed_with_string(self, string):
        self.kropff_parameters_changed()

    def kropff_high_tof_table_selection_changed(self):
        self.update_bragg_edge_plot()
        self.update_kropff_fitting_plot()
        self.update_selected_bins_plot()
        o_event = KropffHandler(parent=self,
                                grand_parent=self.parent)
        o_event.display_bragg_peak_threshold()

    def kropff_low_tof_table_selection_changed(self):
        self.update_bragg_edge_plot()
        self.update_kropff_fitting_plot()
        self.update_selected_bins_plot()
        o_event = KropffHandler(parent=self,
                                grand_parent=self.parent)
        o_event.display_bragg_peak_threshold()

    def kropff_bragg_peak_table_selection_changed(self):
        self.update_selected_bins_plot()
        self.update_bragg_edge_plot()
        self.update_kropff_fitting_plot()
        o_event = KropffHandler(parent=self,
                                grand_parent=self.parent)
        o_event.display_bragg_peak_threshold()

    def kropff_bragg_edge_threshold_changed(self):
        o_event = KropffHandler(parent=self,
                                grand_parent=self.parent)
        o_event.kropff_bragg_edge_threshold_changed()

    def kropff_threshold_width_slider_changed(self, new_value):
        self.ui.kropff_threshold_width_value.setText(str(new_value))

    def kropff_fit_all_regions(self):
        o_event = KropffHandler(parent=self,
                                grand_parent=self.parent)
        o_event.fit_regions()

    # general settings

    def windows_settings(self):
        self.parent.session_dict[DataType.fitting]['ui']['splitter_2'] = self.ui.splitter_2.sizes()
        self.parent.session_dict[DataType.fitting]['ui']['splitter'] = self.ui.splitter.sizes()
        self.parent.session_dict[DataType.fitting]['ui']['splitter_3'] = self.ui.splitter_3.sizes()

    def save_all_parameters(self):
        self.kropff_parameters_changed()
        self.windows_settings()

    def closeEvent(self, event=None):
        self.save_all_parameters()
        if self.parent.advanced_selection_ui:
            self.parent.advanced_selection_ui.close()
        if self.parent.fitting_set_variables_ui:
            self.parent.fitting_set_variables_ui.close()
        self.parent.fitting_ui = None
