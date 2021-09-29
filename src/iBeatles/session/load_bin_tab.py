import numpy as np


class LoadBin:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def all(self):
        session_dict = self.session_dict

        self.parent.binning_roi = session_dict['bin']['roi']

        binning_line_view = session_dict['bin']['binning line view']
        self.parent.binning_line_view['pos'] = np.array(binning_line_view['pos'])
        self.parent.binning_line_view['adj'] = np.array(binning_line_view['adj'])

        line_color = tuple(binning_line_view['line color'])
        lines = np.array([line_color for n in np.arange(len(self.parent.binning_line_view['pos']))],
                         dtype=[('red', np.ubyte), ('green', np.ubyte),
                                ('blue', np.ubyte), ('alpha', np.ubyte),
                                ('width', float)])
        self.parent.binning_line_view['pen'] = lines
