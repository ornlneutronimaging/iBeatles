import os

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
refresh_image = os.path.join(root, "icons/refresh.png")
settings_image = os.path.join(root, "icons/plotSettings.png")
combine_image = os.path.join(root, "icons/combine.png")
bin_image = os.path.join(root, "icons/bin.png")
auto_image = os.path.join(root, "icons/auto.png")
manual_image = os.path.join(root, "icons/manual.png")
more_infos_image = os.path.join(root, "icons/more_infos.png")
stats_table_image = os.path.join(root, "icons/stats_table.png")
stats_plot_image = os.path.join(root, "icons/stats_plot.png")

ANGSTROMS = "\u212b"
LAMBDA = "\u03bb"
MICRO = "\u00b5"
SUB_0 = "\u2080"
DELTA = "\u0394"


class SessionKeys:
    list_folders_status = "list_folders_status"
    list_folders = "list_folders"
    top_folder = "top_folder"

    combine_algorithm = "combine_algorithm"
    combine_roi = "combine_roi"
    combine_roi_item_id = "combine_roi_item_id"
    combine_image_view = "combine_image_view"

    # data folder
    folder = "folder"
    data = "data"
    list_files = "list_files"
    nbr_files = "nbr_files"
    use = "use"
