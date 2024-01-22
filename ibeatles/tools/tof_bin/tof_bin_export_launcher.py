from qtpy.QtWidgets import QDialog

import warnings
warnings.filterwarnings("ignore")

from ibeatles import load_ui
from ibeatles import DataType
from ibeatles.utilities.status_message_config import StatusMessageStatus, show_status_message
from ibeatles.tools.tof_combine.utilities.get import Get


class TofBinExportLauncher(QDialog):

    def __init__(self, parent=None, top_parent=None):
        self.parent = parent
        self.top_parent = top_parent
        QDialog.__init__(self, parent=parent)
        self.ui = load_ui('ui_tof_bin_export.ui', baseinstance=self)

    def ok_clicked(self):
        print("ok clicked!")
        # o_get = Get(parent=self)
        # data_type_selected = o_get.combine_export_mode()
        # self.close()
        # output_folder = self.parent.combine_run(data_type_selected=data_type_selected)
        # if output_folder:
        #     self.parent.reload_run_in_main_ui(data_type_selected=data_type_selected,
        #                                       output_folder=output_folder)
        #     self.parent.close()
        #
        #     message = f"TOF combined exported to {output_folder}"
        #     if not (data_type_selected == DataType.none):
        #         message += f" and loaded back in {data_type_selected}"
        #     message += "!"
        #     status = StatusMessageStatus.ready
        #
        # else:
        #     message = "User cancel export process!"
        #     status = StatusMessageStatus.warning
        #
        # show_status_message(parent=self.grand_parent,
        #                     message=message,
        #                     status=status,
        #                     duration_s=10)
