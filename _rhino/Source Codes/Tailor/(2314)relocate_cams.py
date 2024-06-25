import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys


sys.path.append("..\lib")
import EnneadTab


sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)




@EnneadTab.ERROR_HANDLE.try_catch_error
def relocate_cams():
    line = rs.GetObject("pick line representing cam relocation")
    
    if not line: return
    end_pt, start_pt = rs.CurveEndPoint(line), rs.CurveStartPoint(line)
    
    
    all_views = rs.NamedViews()
    source_orgin = end_pt
    source_x_pt = rs.PointAdd(end_pt, Rhino.Geometry.Point3d(1,0,0))
    source_array = [source_orgin, source_x_pt]
    
    target_orgin = start_pt
    target_x_pt = rs.PointAdd(start_pt, Rhino.Geometry.Point3d(1,0,0))
    target_array = [target_orgin, target_x_pt]
    
    
    for view in all_views:
        print (view)
        rs.RestoreNamedView(view, view = None, restore_bitmap = False)
        #current_cam = rs.ViewCamera(view = view, camera_location = None)
        current_cam, current_cam_target = rs.ViewCameraTarget(view = view, camera = None, target = None)

        temp_cam_pt = rs.AddPoint( current_cam )
        temp_cam_target_pt = rs.AddPoint( current_cam_target )

        new_cam = rs.OrientObject(temp_cam_pt, source_array, target_array)
        new_cam_target = rs.OrientObject(temp_cam_target_pt, source_array, target_array)
        rs.ViewCameraTarget(view = view, camera = new_cam, target = new_cam_target)

        rs.AddNamedView( view, view )#first view is the view name to override

        rs.DeleteObject(temp_cam_pt)
        rs.DeleteObject(temp_cam_target_pt)






######################  main code below   #########
if __name__ == "__main__":

    relocate_cams()


