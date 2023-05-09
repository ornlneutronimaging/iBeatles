class SessionKeys:

    material = "material"
    instrument = "instrument"
    bin = "bin"
    fitting = "fitting"
    settings = "settings"
    reduction = "reduction"


class MaterialMode:

    pre_defined = "pre_defined"
    custom_method1 = "custom method 1"
    custom_method2 = "custom method 2"


class SessionSubKeys:

    # instrument
    distance_source_detector = "distance source detector"
    detector_value = "detector value"
    beam_index = "beam index"

    # general
    list_files = "list files"
    current_folder = 'current folder'
    list_files_selected = 'list files selected'
    list_rois = 'list rois'

    # sample
    time_spectra_filename = "time spectra filename"

    # ob
    image_view_state = 'image view state'
    image_view_histogram = 'image view histogram'

    # material
    pre_defined_selected_element = "selected element in the pre-defined mode"
    material_mode = MaterialMode.pre_defined
    pre_defined = "pre_defined"
    custom_method1 = "custom method 1"
    custom_method2 = "custom method 2"

    lattice = "lattice"
    crystal_structure = "crystal structure"
    index = "index"
    name = "name"
    user_defined = "user_defined"

    # bin
    state = "state"
    roi = "roi"
    binning_line_view = 'binning line view'

    # fitting
    ui_accessed = "ui_accessed"
    x_axis = "x_axis"
    transparency = "transparency"
    ui = "ui"
    lambda_range_index = "lambda range index"
    march_dollase = "march dollase"
    kropff = "kropff"

    # settings
    log_buffer_size = "log buffer size"
    config_version = "config version"

    # reduction
    activate = "activate"
    dimension = "dimension"
    size = "size"
    type = "type"
    process_order = "process order"
