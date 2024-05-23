import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
"""
not in use
"""
@EnneadTab.ERROR_HANDLE.try_catch_error
def convert_camera():
    import webbrowser
    webbrowser.open("https://www.youtube.com/watch?v=by2tRODdwRw")
    return

    
    all_views = rs.NamedViews()
    if all_views is None: return


    filepath = r"I:\2135\0_3D\00_3D Resources\Python\render_coordinate.txt"
    with open(filepath) as f:
        lines = f.readlines()
    pts = map(lambda x: float(x.replace("\n","")), lines)

    target_orgin = rs.AddPoint(pts[0],pts[1], pts[2])

    target_x_pt = rs.AddPoint(pts[3],pts[4], pts[5])
    target_array = [target_orgin, target_x_pt]



    source_orgin = rs.AddPoint([0,0,0])
    source_x_pt = rs.AddPoint([100,0,0])
    source_array = [source_orgin, source_x_pt]


    opts = ["Revit Coor-->Render Coor", "Render Coor-->Revit Coor"]
    res = rs.ListBox(opts, message = "Which re-location?", title = "Bilibili camera relocation", default = None)
    if res == opts[1]:
        source_array, target_array = target_array, source_array

    for view in all_views:
        print(view)
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

        """
        rs.DeleteObject(current_cam)
        rs.DeleteObject(current_cam_target)
        rs.DeleteObject(temp_cam_target_pt)
        rs.DeleteObject(temp_cam_target_pt)
        """



    rs.DeleteObject(target_orgin)
    rs.DeleteObject(target_x_pt)
    rs.DeleteObject(source_orgin)
    rs.DeleteObject(source_x_pt)

if __name__ == "__main__":
    convert_camera()
