from qtpy.QtWidgets import QTableWidgetItem, QHBoxLayout, QMainWindow
from qtpy.QtGui import QColor
from qtpy import QtCore
import numpy as np

from .. import load_ui
from src.iBeatles.step6.initialization import Initialization
from src.iBeatles.utilities.status_message_config import StatusMessageStatus, show_status_message


class StrainMappingLauncher(object):

    def __init__(self, parent=None):
        self.parent = parent

        if self.parent.fitting_ui is None:
            show_status_message(parent=self.parent,
                                message="Strain Mapping requiere to first launch the fitting window!",
                                status=StatusMessageStatus.error,
                                duration_s=10)
        else:
            strain_mapping_window = StrainMappingWindow(parent=parent)
            strain_mapping_window.show()
            self.parent.strain_mapping_ui = strain_mapping_window


class StrainMappingWindow(QMainWindow):
    colorscale_nbr_row = 15
    colorscale_cell_size = {'width': 50,
                            'height': 30}

    def __init__(self, parent=None):

        self.parent = parent
        QMainWindow.__init__(self, parent=parent)
        self.ui = load_ui('ui_strainMapping.ui', baseinstance=self)
        self.setWindowTitle("6. Strain Mapping")

        o_init = Initialization(parent=self, grand_parent=self.parent)
        o_init.all()

    def fitting_algorithm_changed(self):
        print("fitting_algorithm_changed")

    def parameters_to_display_changed(self):
        print("parameters_to_display_changed")

    def d0_to_use_changed(self):
        print("d0_to_use_changed")

    def transparency_slider_changed(self, new_value):
        print("transparency changed")

    def export_clicked(self):
        print("export clicked")














    def display_images_and_selection(self):
        self.display_images()
        self.display_selections()

    def get_min_max(self, table=[], item='strain_mapping'):
        if item == 'strain_mapping':
            item = 'd_spacing'

        min_value = 1e6
        max_value = -1e6
        # is_first_value = True
        for _index in table:
            _entry = table[_index]

            value = _entry[item]['val']
            if min_value > value:
                min_value = value
            elif max_value < value:
                max_value = value

        return [min_value, max_value]

    def clear_colorscale_table(self, item='strain_mapping', table_ui=None):
        nbr_row = table_ui.rowCount()
        for _row in np.arange(nbr_row):
            table_ui.removeRow(0)

    def initialize_colorscale_table(self, min_value=0,
                                    max_value=0,
                                    item='strain_mapping'):

        if item == 'strain_mapping':
            _table_ui = self.ui.strain_mapping_colorbar
        elif item == 'sigma':
            _table_ui = self.ui.alpha_colorbar
        else:
            _table_ui = self.ui.sigma_colorbar

        self.clear_colorscale_table(item=item, table_ui=_table_ui)

        nbr_row = self.colorscale_nbr_row
        step = (float(max_value) - float(min_value)) / (nbr_row - 1)
        mid_point = np.int(nbr_row / 2)
        _row = 0

        if min_value == max_value:
            nbr_row = 1

        if np.isnan(step):
            nbr_row = 1

        for _index in np.arange(nbr_row - 1, -1, -1):
            _table_ui.insertRow(_row)
            _table_ui.setRowHeight(_row, self.colorscale_cell_size['height'])
            _table_ui.setColumnWidth(_row, self.colorscale_cell_size['width'])
            if np.isnan(step):
                _value = np.NaN
            else:
                _value = min_value + _index * step
            _color = self.get_color_for_this_value(min_value=min_value,
                                                   max_value=max_value,
                                                   value=_value)

            if np.isnan(_value):
                _item = QTableWidgetItem("nan")
            else:
                _item = QTableWidgetItem("{:04.2f}".format(_value))
            _item.setBackgroundColor(_color)
            _item.setTextAlignment(QtCore.Qt.AlignRight)
            if (_row < mid_point) and (nbr_row != 1):
                # font should be changd from black to white
                _foreground_color = QColor(255, 255, 255, alpha=255)
                _item.setTextColor(_foreground_color)

            _table_ui.setItem(_row, 0, _item)
            _row += 1

    def get_color_for_this_value(self, min_value=0, max_value=1, value=0):
        if np.isnan(value):
            return QColor(255, 255, 255, alpha=100)  # white
        elif max_value == min_value:
            return QColor(250, 0, 0, alpha=255)  # red

        _ratio = (1 - (float(value) - float(min_value)) / (float(max_value) - float(min_value)))
        return QColor(0, _ratio * 255, 0, alpha=255)

    def display_selections(self, item='strain_mapping'):

        # strain mapping
        table_dictionary = self.parent.table_dictionary

        [min_value, max_value] = self.get_min_max(table=table_dictionary,
                                                  item=item)

        print("min_value: {} and max_value: {}".format(min_value, max_value))

        self.initialize_colorscale_table(min_value=min_value,
                                         max_value=max_value,
                                         item=item)

        for _index in table_dictionary:
            _entry = table_dictionary[_index]
            x0 = _entry['bin_coordinates']['x0']
            x1 = _entry['bin_coordinates']['x1']
            y0 = _entry['bin_coordinates']['y0']
            y1 = _entry['bin_coordinates']['y1']

            rect = pg.QtGui.QGraphicsRectItem(x0, y0, x1 - x0, y1 - y0)
            rect.setPen(pg.mkPen(None))
            rect.setBrush(pg.mkBrush('r'))
            self.ui.strain_mapping_image.addItem(rect)
            return

    def display_images(self):
        _data = self.parent.data_metadata['normalized']['data_live_selection']
        if not _data == []:
            self.ui.strain_mapping_image.setImage(_data)
            self.ui.sigma_image.setImage(_data)
            self.ui.alpha_image.setImage(_data)

    def set_tab_widgets(self):
        image_view = pg.ImageView()
        image_view.ui.roiBtn.hide()
        image_view.ui.menuBtn.hide()
        hori_layout = QHBoxLayout()
        hori_layout.addWidget(image_view)

        return {'layout': hori_layout,
                'image_view': image_view,
                }

    def init_labels(self):
        self.ui.d0_label.setText(u"d<sub>0</sub>")
        self.ui.d0_units_label.setText(u"\u212B")

    def closeEvent(self, event=None):
        if self.parent.strain_mapping_ui:
            self.parent.strain_mapping_ui.close()
        self.parent.strain_mapping_ui = None
