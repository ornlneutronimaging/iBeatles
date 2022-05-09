from qtpy import QtGui

LOCK_ROW_BACKGROUND = QtGui.QColor(75, 150, 150)
UNLOCK_ROW_BACKGROUND = QtGui.QColor(255, 255, 255)


class FittingKropffBraggPeakColumns:

    l_hkl_error = 5
    tau_error = 6
    sigma_error = 7


class FittingRegions:

    high_lambda = "high_lambda"
    low_lambda = "low_lambda"
    bragg_peak = "bragg_peak"
