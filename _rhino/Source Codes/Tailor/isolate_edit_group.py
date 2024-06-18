import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
import scriptcontext

@EnneadTab.ERROR_HANDLE.try_catch_error
def isolate_edit_group():
    ids = rs.SelectedObjects(include_lights = True, include_grips = False)
    if not ids: return


    rs.Command("_Ungroup", False)

    invert_objs = rs.InvertSelectedObjects(include_lights = True)
    rs.LockObjects(invert_objs)



    rs.UnselectObjects(ids)




if __name__=="__main__":
    isolate_edit_group()
