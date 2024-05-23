import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
"""
not in use
"""
@EnneadTab.ERROR_HANDLE.try_catch_error
def orient():
    import webbrowser
    webbrowser.open("https://www.youtube.com/watch?v=by2tRODdwRw")
    return

    
    Ids = rs.GetObjects("Select model to rotate", preselect = True)
    if Ids is None: return

    rs.EnableRedraw(enable = False)
    filepath = r"I:\2135\0_3D\00_3D Resources\Python\render_coordinate.txt"
    with open(filepath) as f:
        lines = f.readlines()
    pts = map(lambda x: float(x.replace("\n","")), lines)

    target_orgin = rs.AddPoint(pts[0],pts[1], pts[2])

    target_x_pt = rs.AddPoint(pts[3],pts[4], pts[5])
    target_array = [target_orgin, target_x_pt]



#    target_orgin = rs.AddPoint(1000,2000,0)
#    target_x_vector = rs.VectorCreate([100,100,0], [0,0,0])
#    target_x_pt = rs.CopyObject(target_orgin , target_x_vector)
#    target_array = [target_orgin, target_x_pt]


    source_orgin = rs.AddPoint([0,0,0])
    source_x_pt = rs.AddPoint([100,0,0])
    source_array = [source_orgin, source_x_pt]


    opts = ["Revit Coor-->Render Coor", "Render Coor-->Revit Coor"]
    res = rs.ListBox(opts, message = "Which re-location?", title = "Bilibili objects relocation", default = None)
    if res == opts[1]:
        source_array, target_array = target_array, source_array

    for Id in Ids:
        rs.OrientObject(Id, source_array, target_array)


    rs.DeleteObject(target_orgin)
    rs.DeleteObject(target_x_pt)
    rs.DeleteObject(source_orgin)
    rs.DeleteObject(source_x_pt)

if __name__ == "__main__":


    orient()
