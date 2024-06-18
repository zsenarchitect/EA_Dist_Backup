import rhinoscriptsyntax as rs
import os
from scriptcontext import doc
import sys
sys.path.append("..\lib")

import EA_UTILITY as EA
import EnneadTab


@EnneadTab.ERROR_HANDLE.try_catch_error
def export_by_group(extension = "3dm"):
    EnneadTab.RHINO.RHINO_CLEANUP.purge_group()
    all_groups = rs.GroupNames()
    
    selected_groups = EnneadTab.RHINO.RHINO_FORMS.select_from_list(all_groups, message = "Select Groups that will go out.", multi_select = True)
    if selected_groups is None:
        return


    target_main_folder = rs.BrowseForFolder( folder = None, message = "Select an output folder", title = "Select an output folder")

    try:
        doc_name = doc.Name.split(".3dm")[0]
    except:
        doc_name = "Untitled"
    EA_export_folder = "{}\EnneadTab Export By Group from {}".format(target_main_folder, doc_name)
    if not os.path.exists(EA_export_folder):
        os.makedirs(EA_export_folder)


    rs.EnableRedraw(False)
    

    for i, group in enumerate(selected_groups):
        rs.UnselectAllObjects()
        raw_objs = rs.ObjectsByGroup(group, select = False)
        filter = rs.filter.textdot
        anno_dots = [obj for obj in raw_objs if rs.ObjectType(obj)== filter]
        if len(anno_dots) == 0:
            continue
        export_name = rs.TextDotText(anno_dots[0])
        rs.SelectObjects(raw_objs)
        filepath = "{}\{}.{}".format(EA_export_folder, export_name, extension)
        #rs.Command("!_-Export \"{}\" _Pause -SaveSmall = -Yes -Enter -Enter".format(filepath))
        rs.Command("!_-Export \"{}\" -Enter -Enter".format(filepath))
        
    #rs.Command("!_Undo")



    EnneadTab.NOTIFICATION.toast(sub_text = "", main_text = "All groups exported!")
    rs.MessageBox(message = "All group processed", buttons= 0 | 48, title = "Export by Layer")



#####
if __name__ == "__main__":
    export_by_group(extension = "dwg")
