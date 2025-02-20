__title__ = "BatchExportRhinoView"
__doc__ = """Exports multiple Rhino views in batch.

Allows selection of multiple views for automated export.
Supports customizable resolution and format settings.
"""
__is_popular__ = True
import rhinoscriptsyntax as rs
from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION
from EnneadTab.RHINO import RHINO_FORMS

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def batch_export_rhino_view():
    default_width = DATA_FILE.get_sticky("batch_export_view_default_width", 1200)
    default_height = DATA_FILE.get_sticky("batch_export_view_default_height", 700)
    default_format = DATA_FILE.get_sticky("batch_export_view_default_format", "png")
    res = rs.PropertyListBox(["Width", "Height",  "Format"],
                             [str(default_width), str(default_height), default_format],
                             message="Set the default width, height and format for the exported images.",
                             title="EnneadTab Batch Export Rhino View")
    if not res:
        return
    try:
        width = int(res[0])
        height = int(res[1])
    except:
        NOTIFICATION.messenger("Invalid input for width or height")
        return
    format = res[2]

    DATA_FILE.set_sticky("batch_export_view_default_width", width)
    DATA_FILE.set_sticky("batch_export_view_default_height", height)
    DATA_FILE.set_sticky("batch_export_view_default_format", format)

    folder = rs.BrowseForFolder(message="Select a folder to save the images")
    if not folder:
        return
    
    all_views = rs.NamedViews()
    selected_views = RHINO_FORMS.select_from_list(sorted(all_views, reverse=True), 
                                                  message="Select Views to Export.  Use Control/Shift to select multiple views.", 
                                                  button_names=["Export"])
    if not selected_views:
        return

    for view in selected_views:
        print("Exporting view [{}]".format(view))
        rs.RestoreNamedView(view, view=None, restore_bitmap=False)
        file_path = "{}\\{}.{}".format(folder, view, format)
        rs.Command("!_-ViewCaptureToFile _Width {} _Height {} \"{}\" -enter -enter".format(width, height, file_path))


    NOTIFICATION.duck_pop("All views exported.")
if __name__ == "__main__":
    batch_export_rhino_view()
