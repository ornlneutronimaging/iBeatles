import logging

from ..all_steps.event_handler import EventHandler as TopEventHandler
from ..step1.data_handler import DataHandler
from ..step1.plot import Step1Plot
from ..step2.initialization import Initialization as Step2Initialization
from ..step1.gui_handler import Step1GuiHandler

from ..utilities.retrieve_data_infos import RetrieveGeneralDataInfos

from .. import DataType


class EventHandler(TopEventHandler):

    def import_button_clicked(self):
        logging.info(f"{self.data_type} import button clicked")

        self.parent.loading_flag = True
        o_load = DataHandler(parent=self.parent,
                             data_type=self.data_type)
        _folder = o_load.select_folder()
        o_load.import_files_from_folder(folder=_folder, extension=".tif")
        o_load.import_time_spectra()

        if self.parent.data_metadata[self.data_type]['data']:

            self.parent.select_load_data_row(data_type=self.data_type, row=0)
            self.parent.retrieve_general_infos(data_type=self.data_type)