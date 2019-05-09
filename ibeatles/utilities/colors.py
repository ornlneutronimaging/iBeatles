from PyQt5 import QtCore
import numpy as np

roi_group_color = [QtCore.Qt.blue,
                   QtCore.Qt.darkRed,
                   QtCore.Qt.green,
                   QtCore.Qt.darkYellow]

pen_color = {'0': (62, 13, 244),  # blue
             '1': (139, 10, 19),  # dark red
             '2': (36, 244, 31),  # green
             '3': (209, 230, 27)}  # dark yellow


def set_alpha_value(lines=[], transparency=50):
    new_a = np.int((np.float(transparency) / 100.) * 255)

    new_lines = []
    for _line in lines:
        [r, g, b, a, w] = _line
        _new_line = (r, g, b, new_a, w)
        new_lines.append(_new_line)

    lines = np.array(new_lines,
                     dtype=[('red', np.ubyte), ('green', np.ubyte),
                            ('blue', np.ubyte), ('alpha', np.ubyte),
                            ('width', float)])
    return lines
