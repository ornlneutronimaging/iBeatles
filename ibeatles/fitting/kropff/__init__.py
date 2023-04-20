from qtpy import QtGui

LOCK_ROW_BACKGROUND = QtGui.QColor(75, 150, 150)
UNLOCK_ROW_BACKGROUND = QtGui.QColor(255, 255, 255)
REJECTED_ROW_BACKGROUND = QtGui.QColor(255, 255, 150)

ERROR_TOLERANCE = 100


class FittingKropffBraggPeakColumns:

    l_hkl_value = 2
    tau_value = 3
    sigma_value = 4
    l_hkl_error = 5
    tau_error = 6
    sigma_error = 7


class FittingKropffHighLambdaColumns:

    a0 = 2
    b0 = 3


class FittingKropffLowLambdaColumns:

    ahkl = 2
    bhkl = 3


class FittingRegions:

    high_lambda = "high_lambda"
    low_lambda = "low_lambda"
    bragg_peak = "bragg_peak"


class SessionSubKeys:

    table_dictionary = "table dictionary"
    high_tof = "high tof"
    low_tof = "low tof"
    bragg_peak = "bragg peak"
    a0 = "a0"
    b0 = "b0"
    graph = "graph"
    ahkl = "ahkl"
    bhkl = "bhkl"
    lambda_hkl = "lambda_hkl"
    tau = "tau"
    sigma = "sigma"
    table_selection = "table selection"
    automatic_bragg_peak_threshold_finder = "automatic bragg peak threshold finder"
    kropff_bragg_peak_good_fit_conditions = "kropff bragg peak good fit conditions"
    l_hkl = "l_hkl"
    l_hkl_error = "l_hkl_error"
    state = "state"
    value = "value"
    t_error = "t_error"
    sigma_error = "sigma_error"
    kropff_lambda_settings = "kropff lambda settings"
    fix = "fix"
    range = "range"
    bragg_peak_row_rejections_conditions = "bragg peak row conditions"
    less_than = "less_than"
    more_than = "more_than"

