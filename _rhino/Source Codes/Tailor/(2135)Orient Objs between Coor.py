import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs


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

    Ids = rs.GetObjects("Select model to rotate", preselect = True)
    if Ids is None: return
    opts = ["Revit Internal Coor-->Render Coor", 
            "Render Coor-->Revit Internal Coor", 
            "Revit Internal Coor-->Survey Coor", 
            "Survey Coor-->Revit Internal Coor", 
            "Render Coor-->Survey Coor", 
            "Survey Coor-->Render Coor"
            ]
    res = rs.ListBox(opts, message = "Which re-location?", title = "Bilibili objects relocation", default = None)
    
    
    first_opt, second_opt = res.split("-->")
    
    
    rs.EnableRedraw(enable = False)

    source_array, added_pts_0 = get_reference_array(first_opt)
    target_array, added_pts_1 = get_reference_array(second_opt)
    
    for Id in Ids:
        rs.OrientObject(Id, source_array, target_array)


    rs.DeleteObjects(added_pts_0)
    rs.DeleteObjects(added_pts_1)
    rs.SelectObjects(Ids)
    rs.ZoomSelected()


if __name__ == "__main__":
    orient()
