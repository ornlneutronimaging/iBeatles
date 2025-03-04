from qtpy.QtWidgets import QDialog
import warnings
from src.ibeatles import load_ui
from src.ibeatles import DataType
from src.ibeatles.utilities.status_message_config import (
    StatusMessageStatus,
    show_status_message,
)
from src.ibeatles.tools.tof_combine.utilities.get import Get

warnings.filterwarnings("ignore")


class TofCombineExportLauncher(QDialog):
    def __init__(self, parent=None, grand_parent=None):
        self.parent = parent
        self.grand_parent = grand_parent
        QDialog.__init__(self, parent=parent)
        self.ui = load_ui("ui_tof_combine_export.ui", baseinstance=self)

    def ok_clicked(self):
        o_get = Get(parent=self)
        data_type_selected = o_get.combine_export_mode()
        self.close()
        output_folder = self.parent.combine_run(data_type_selected=data_type_selected)
        if output_folder:
            self.parent.reload_run_in_main_ui(
                data_type_selected=data_type_selected, output_folder=output_folder
            )
            self.parent.close()

            message = f"TOF combined exported to {output_folder}"
            if not (data_type_selected == DataType.none):
                message += f" and loaded back in {data_type_selected}"
            message += "!"
            status = StatusMessageStatus.ready

        else:
            message = "User cancel export process!"
            status = StatusMessageStatus.warning

        show_status_message(
            parent=self.grand_parent, message=message, status=status, duration_s=10
        )
