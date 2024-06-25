import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs


def get_selected_views():
    all_views = rs.NamedViews()
    availible_view_names = [[x, False] for x in all_views]
    try:
        availible_view_names.sort(key = lambda x: x[0].lower())
    except:
        pass
    availible_view_names.insert(0, ["<Check me to process all views, ignore selection below>", False])
    res = rs.CheckListBox(items = availible_view_names,
                            message = "select views to transfer orientation",
                            title = "view selecter")
    if not res:
        return 
    picked_view_name = []
    for name, status in res:
        if "Check me" in name and status:
            return all_views
            
        if status:
            picked_view_name.append(name)
    return picked_view_name
    
    
def get_reference_array(opt):
    if "revit" in opt.lower():
        return get_reference_array_of_world()
    if "render" in opt.lower():
        filepath = r"I:\2135\0_3D\00_3D Resources\Python\render_coordinate.txt"
        return get_reference_array_from_file(filepath)
    if "survey" in opt.lower():
        filepath = r"I:\2135\0_3D\00_3D Resources\Python\survey_coordinate.txt"
        return get_reference_array_from_file(filepath)


def get_reference_array_from_file(filepath):
    # filepath = r"I:\2135\0_3D\00_3D Resources\Python\render_coordinate.txt"
    with open(filepath) as f:
        lines = f.readlines()
    pts = map(lambda x: float(x.replace("\n","")), lines)

    target_orgin = rs.AddPoint(pts[0],pts[1], pts[2])
    target_x_pt = rs.AddPoint(pts[3],pts[4], pts[5])

    target_array = [target_orgin, target_x_pt]
    return target_array, [target_orgin, target_x_pt]


def get_reference_array_of_world():
    source_orgin = rs.AddPoint([0,0,0])
    source_x_pt = rs.AddPoint([100,0,0])
    source_array = [source_orgin, source_x_pt]
    return source_array, [source_orgin, source_x_pt]


@EnneadTab.ERROR_HANDLE.try_catch_error
def orient():

    
    all_views = get_selected_views()
    #all_views = rs.NamedViews()
    if all_views is None: return

    opts = ["Revit Internal Coor-->Render Coor",
            "Render Coor-->Revit Internal Coor",
            "Revit Internal Coor-->Survey Coor",
            "Survey Coor-->Revit Internal Coor",
            "Render Coor-->Survey Coor",
            "Survey Coor-->Render Coor"
            ]
    res = rs.ListBox(opts, message = "Which re-location?", title = "Bilibili camera relocation", default = None)


    first_opt, second_opt = res.split("-->")


    rs.EnableRedraw(enable = False)

    source_array, added_pts_0 = get_reference_array(first_opt)
    target_array, added_pts_1 = get_reference_array(second_opt)

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



    rs.DeleteObjects(added_pts_0)
    rs.DeleteObjects(added_pts_1)



if __name__ == "__main__":
    orient()
