import numpy as np
import pyqtgraph as pg

from ibeatles.tof_combine.utilities import CombineAlgorithm
from ibeatles.tof_combine.utilities.get import Get
from ibeatles.tof_combine import SessionKeys as TofCombineSessionKeys


class Combine:

    def __init__(self, parent=None):
        self.parent = parent

    def run(self):
        o_get = Get(parent=self.parent)
        combine_algorithm = o_get.combine_algorithm()
        list_array_to_combine = o_get.list_array_to_combine()

        if list_array_to_combine is None:
            self.parent.combine_image_view.clear()
            self.parent.combine_image_view.removeItem(self.parent.combine_roi_item_id)
            self.parent.combine_data = None

        else:
            # combine using algorithm defined
            [nbr_folder_to_combine, nbr_files, width, height] = np.shape(list_array_to_combine)

            if nbr_folder_to_combine > 1:
                if combine_algorithm == CombineAlgorithm.mean:
                    combine_arrays = np.mean(list_array_to_combine, axis=0)
                elif combine_algorithm == CombineAlgorithm.median:
                    combine_arrays = np.median(list_array_to_combine, axis=0)
                else:
                    raise NotImplementedError("Algorithm not implemented!")
            else:
                combine_arrays = list_array_to_combine[0]

            combine_arrays = np.squeeze(combine_arrays)

            self.parent.combine_data = combine_arrays
            integrated_arrays = np.mean(combine_arrays, axis=0)
            integrated_arrays = np.transpose(integrated_arrays)
            self.parent.live_combine_image = integrated_arrays
            # display integrated
            self.parent.combine_image_view.setImage(integrated_arrays)

            # initialize ROI if first time, otherwise use same region
            [x0, y0, width, height] = self.parent.session[TofCombineSessionKeys.combine_roi]
            if self.parent.combine_roi_item_id:
                self.parent.combine_image_view.removeItem(self.parent.combine_roi_item_id)

            roi_item = pg.ROI([x0, y0],
                              [width, height])
            roi_item.addScaleHandle([1, 1], [0, 0])
            self.parent.combine_image_view.addItem(roi_item)
            roi_item.sigRegionChanged.connect(self.parent.combine_roi_changed)
            self.parent.combine_roi_item_id = roi_item
