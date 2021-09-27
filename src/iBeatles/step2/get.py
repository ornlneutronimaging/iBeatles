import numpy as np

from . import RegionType


class Get:

    def __init__(self, parent=None):
        self.parent = parent

    def table_number_row(self):
        return self.parent.ui.normalization_tableWidget.rowCount()

    def roi_table_row(self, row=-1):
        if row == -1:
            return []

        # use flag
        _flag_widget = self.parent.ui.normalization_tableWidget.cellWidget(row, 0)
        if _flag_widget is None:
            raise ValueError
        flag = _flag_widget.isChecked()

        # x0
        _item = self.parent.ui.normalization_tableWidget.item(row, 1)
        if _item is None:
            raise ValueError
        x0 = str(_item.text())

        # y0
        _item = self.parent.ui.normalization_tableWidget.item(row, 2)
        if _item is None:
            raise ValueError
        y0 = str(_item.text())

        # width
        _item = self.parent.ui.normalization_tableWidget.item(row, 3)
        if _item is None:
            raise ValueError
        width = str(_item.text())

        # height
        _item = self.parent.ui.normalization_tableWidget.item(row, 4)
        if _item is None:
            raise ValueError
        height = str(_item.text())

        # region type
        _text_widget = self.parent.ui.normalization_tableWidget.cellWidget(row, 5)
        region_type = _text_widget.currentText()

        return [flag, x0, y0, width, height, region_type]

    def status_of_run_normalization_button(self):
        """Conditions to validate the run_normalization button are:
         - have ob loaded
         - if no ob, have at least one ENABLED Background ROI
         """
        data = self.parent.data_metadata['sample']['data']
        if not data:
            return False

        ob = self.parent.data_metadata['ob']['data']
        if not ob:
            number_row = self.table_number_row()
            for _row in np.arange(number_row):
                _roi = self.roi_table_row(row=_row)
                [status, _, _, _, _, region_type] = _roi
                if (status is True) and (region_type == RegionType.background):
                    return True

        if ob:
            return True

        return False
