from ibeatles.all_steps.event_handler import EventHandler as TopEventHandler
from ibeatles.step1.data_handler import DataHandler
from ibeatles.step1.plot import Step1Plot
from ibeatles.step1.gui_handler import Step1GuiHandler


class EventHandler(TopEventHandler):

    def import_button_clicked(self):
        self.parent.loading_flag = True
        o_load = DataHandler(parent=self.parent,
                             data_type=self.data_type)
        _folder = o_load.select_folder()
        o_load.import_files_from_folder(folder=_folder)
        o_load.import_time_spectra()

        if self.parent.data_metadata[self.data_type]['data']:

            self.parent.select_load_data_row(data_type='sample', row=0)
            self.parent.retrieve_general_infos(data_type='sample')
            self.parent.retrieve_selected_row_infos(data_type='sample')
            o_plot = Step1Plot(parent=self.parent, data_type='sample')
            o_plot.display_bragg_edge(mouse_selection=False)
            o_gui = Step1GuiHandler(parent=self.parent)
            o_gui.check_time_spectra_widgets()
            self.parent.check_files_error()
