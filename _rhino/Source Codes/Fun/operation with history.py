
import sys
sys.path.append("..\lib")
import EnneadTab
"""Script to mirror objects in X and Y around the active CPlane origin
If not active, history recording is enabled for the operation, then set back
to its original state. Script by Mitch Heynick 06.09.19"""

import rhinoscriptsyntax as rs
import Rhino # pyright: ignore.ApplicationSettings.HistorySettings as hs
import scriptcontext as sc


@EnneadTab.ERROR_HANDLE.try_catch_error
def QuadMirror():
    objs=rs.GetObjects("Select objects to quad mirror",preselect=True)
    if not objs: return
    hist=hs.RecordingEnabled
    hs.RecordingEnabled=True
    
    plane=rs.ViewCPlane()
    rs.EnableRedraw(False)
    xform_x=rs.XformMirror(plane.Origin,plane.XAxis)
    xform_y=rs.XformMirror(plane.Origin,plane.YAxis)
    x_copy=[sc.doc.Objects.TransformWithHistory(obj,xform_x) for obj in objs]
    if x_copy:
        objs+=x_copy
        y_copy=[sc.doc.Objects.TransformWithHistory(obj,xform_y) for obj in objs]
        if y_copy:
            objs+=y_copy
            rs.SelectObjects(objs)
    hs.RecordingEnabled=hist
    
if __name__ == "__main__":
    QuadMirror()