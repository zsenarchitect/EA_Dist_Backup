import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
import scriptcontext

@EnneadTab.ERROR_HANDLE.try_catch_error
def isolate_edit_group_restore():
    objs = rs.NormalObjects()
    #print objs
    
    rs.AddObjectsToGroup(objs, rs.AddGroup())

    # rs.Command("_Group", False)
    rs.UnlockObjects(rs.LockedObjects())




if __name__=="__main__":
    isolate_edit_group_restore()
