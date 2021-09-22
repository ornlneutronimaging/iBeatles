import logging

from ..all_steps.event_handler import EventHandler as TopEventHandler
from ..step1.data_handler import DataHandler
from ..step1.plot import Step1Plot
from ..step1.gui_handler import Step1GuiHandler

from ..utilities.retrieve_data_infos import RetrieveSelectedFileDataInfos

from .. import DataType


class EventHandler(TopEventHandler):

    def import_button_clicked(self):
        logging.info(f"{self.data_type} import button clicked")

        self.parent.loading_flag = True
        o_load = DataHandler(parent=self.parent,
                             data_type=self.data_type)
        _folder = o_load.select_folder()
        o_load.import_files_from_folder(folder=_folder)
        o_load.import_time_spectra()

        if self.parent.data_metadata[self.data_type]['data']:

            self.parent.select_load_data_row(data_type=self.data_type, row=0)
            self.parent.retrieve_general_infos(data_type=self.data_type)
            self.parent.retrieve_selected_row_infos(data_type=self.data_type)
            o_plot = Step1Plot(parent=self.parent, data_type=self.data_type)
            o_plot.display_bragg_edge(mouse_selection=False)
            o_gui = Step1GuiHandler(parent=self.parent, data_type=self.data_type)
            o_gui.check_time_spectra_widgets()
            o_gui.check_ob_widgets()
            self.parent.check_files_error()

        else:
            logging.info(f"Import button clicked ... operation canceled!")

    def sample_list_selection_changed(self):
        if not self.parent.loading_flag:
            o_retrieve_data_infos = RetrieveSelectedFileDataInfos(parent=self.parent, data_type=DataType.sample)
            o_retrieve_data_infos.update()
            self.parent.roi_image_view_changed(mouse_selection=False)
        else:
            self.parent.loading_flag = False
