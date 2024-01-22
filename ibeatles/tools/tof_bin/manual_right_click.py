from qtpy import QtGui
from qtpy.QtWidgets import QMenu
import logging

from ibeatles.utilities.table_handler import TableHandler
# from maverick.load.load_bin_table import LoadBinTable


class ManualRightClick:

    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("maverick")

    def manual_table_right_click(self):
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        last_row = o_table.row_count()

        menu = QMenu(self.parent)

        row_selected = o_table.get_row_selected()
        remove_bin = -1
        # clean_sort = None
        # load_table = menu.addAction("Import table ...")

        if last_row > 0:
            menu.addSeparator()
            remove_bin = menu.addAction("Remove selected bin")
            # clean_sort = menu.addAction("Sort and remove duplicates")

        action = menu.exec_(QtGui.QCursor.pos())
        if action == remove_bin:
            self.remove_selected_bin()
            self.parent.update_statistics()
        # elif action == load_table:
        #     self.load_manual_bin_table()
        # elif action == clean_sort:
        #     self.sort_and_remove_duplicates()

        else:
            pass

    # def load_manual_bin_table(self):
    #     o_load = LoadBinTable(parent=self.parent)
    #     o_load.run()

    def remove_selected_bin(self):
        """
        remove from the manual table the bin selected
        """
        o_table = TableHandler(table_ui=self.parent.ui.bin_manual_tableWidget)
        row_selected = o_table.get_row_selected()
        item_to_remove = self.parent.list_of_manual_bins_item[row_selected]
        self.parent.bin_profile_view.removeItem(item_to_remove)
        self.parent.list_of_manual_bins_item.pop(row_selected)
        o_table.remove_row(row=row_selected)
        self.logger.info(f"User manually removed row: {row_selected}")
