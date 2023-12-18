import os

root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
refresh_image = os.path.join(root, "icons/refresh.png")
settings_image = os.path.join(root, "icons/plotSettings.png")
combine_image = os.path.join(root, "icons/combine.png")
bin_image = os.path.join(root, "icons/bin.png")
auto_image = os.path.join(root, "icons/auto.png")
manual_image = os.path.join(root, "icons/manual.png")
more_infos_image = os.path.join(root, "icons/more_infos.png")
stats_table_image = os.path.join(root, "icons/stats_table.png")
stats_plot_image = os.path.join(root, "icons/stats_plot.png")

ANGSTROMS = u"\u212B"
LAMBDA = u"\u03BB"
MICRO = u"\u00B5"
SUB_0 = u"\u2080"
DELTA = u"\u0394"


class SessionKeys:

    list_working_folders_status = 'list_working_folders_status'
    list_working_folders = 'list_working_folders'
    combine_algorithm = 'combine_algorithm'
    combine_roi = 'combine_roi'
    combine_roi_item_id = 'combine_roi_item_id'
    combine_image_view = 'combine_image_view'
