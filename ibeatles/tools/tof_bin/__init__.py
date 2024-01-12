from ibeatles.session import SessionSubKeys

TO_MICROS_UNITS = 1e6
TO_ANGSTROMS_UNITS = 1e10


class BinAutoMode:

    log = 'log'
    linear = 'linear'


class BinMode:
    """list of mode to bin the data"""

    auto = 'auto'
    manual = 'manual'
    settings = 'settings'


class BinAlgorithm:
    """list of algorithm used to bin the images"""

    mean = 'mean'
    median = 'median'


class StatisticsName:

    mean = 'mean'
    median = 'median'
    std = 'std'
    min = 'min'
    max = 'max'


class StatisticsRegion:

    full = 'full'
    roi = 'roi'


session = {SessionSubKeys.top_folder: None,  # the base folder to start looking at images folder to combine
           SessionSubKeys.list_working_folders: None,  # list of working folders
           SessionSubKeys.list_working_folders_status: None,  # list of working folders status [True, True, False..]
           SessionSubKeys.log_buffer_size: 500,   # max size of the log file
           SessionSubKeys.version: "0.0.1",   # version of that config
           SessionSubKeys.distance_source_detector: 19.855,
           SessionSubKeys.detector_offset: 9600,
           SessionSubKeys.sample_position: 0,    # in the combine tab
           SessionSubKeys.bin_mode: BinMode.auto,   # 'auto' or 'manual',
           }
