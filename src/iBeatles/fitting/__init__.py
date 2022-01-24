class KropffTabSelected:
    high_tof = "high_tof"
    low_tof = "low_tof"
    bragg_peak = "bragg_peak"


class FittingTabSelected:
    march_dollase = "march_dollase"
    kropff = "kropff"


class KropffThresholdFinder:
    sliding_average = "sliding_average"
    error_function = "error_function"
    change_point = "change_point"


selected_color = {'pen': (0, 0, 0, 30),
                  'brush': (0, 255, 0, 150)}

lock_color = {'pen': (0, 0, 0, 30),
              'brush': (255, 0, 0, 240)}