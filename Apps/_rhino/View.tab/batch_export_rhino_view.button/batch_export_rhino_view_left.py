
__title__ = "BatchExportRhinoView"
__doc__ = "This button does BatchExportRhinoView when left click"

import rhinoscriptsyntax as rs
from EnneadTab import ERROR_HANDLE, LOG
from EnneadTab.RHINO import RHINO_FORMS

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def batch_export_rhino_view():
    res = rs.PropertyListBox(["Width", "Height",  "Format"],
                             ["1200", "700",  "png"])
    if not res:
        return
    width = int(res[0])
    height = int(res[1])
    format = res[2]
    

    folder = rs.BrowseForFolder("Select a folder to save the images")
    if not folder:
        return
    
    all_views = rs.NamedViews()
    selected_views = RHINO_FORMS.select_from_list(sorted(all_views, reverse=True), message="Select Views to Export", button_names=["Export"])
    if not selected_views:
        return

    for view in selected_views:
        print("Exporting view [{}]".format(view))
        rs.RestoreNamedView(view, view=None, restore_bitmap=False)
        file_path = "{}\\{}.{}".format(folder, view, format)
        rs.Command("!_-ViewCaptureToFile _Width {} _Height {} \"{}\" -enter -enter".format(width, height, file_path))
    
if __name__ == "__main__":
    batch_export_rhino_view()
