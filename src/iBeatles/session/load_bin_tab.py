class LoadBin:

    def __init__(self, parent=None):
        self.parent = parent
        self.session_dict = parent.session_dict

    def all(self):
        session_dict = self.session_dict

        self.parent.binning_roi = session_dict['bin']['roi']

        binning_line_view = session_dict['bin']['binning line view']
        self.parent.binning_line_view['pos'] = binning_line_view['pos']
        self.parent.binning_line_view['adj'] = binning_line_view['adj']
        self.parent.binning_line_view['pen'] = binning_line_view['pen']
