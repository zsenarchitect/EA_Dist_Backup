
__title__ = "UniformTransformGeos"
__doc__ = "Apply same rotational transformation for the blocks or geometries. Helpful when you have to reorient many directional blocks, such as changing the direction of cars on street."



import rhinoscriptsyntax as rs
from EnneadTab import LOG, ERROR_HANDLE
from EnneadTab.RHINO import RHINO_OBJ_DATA


@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def uniform_transform_geos():
    ids = rs.GetObjects("Select block instances or objs to rotate",  preselect=True)

    if not ids:
        return





    option_list = ["Rotation"]
    value_list = [180]
    res = rs.PropertyListBox(option_list,
                            value_list,
                            message= "How much angle to rotate each block around insert point?",
                            title="EnneadTab Uniformly Transform")

    if res is None:
        return

    if ids is None: return
    vec = rs.VectorCreate([0,0,1], [0,0,0])
        
    rs.EnableRedraw(False)

    for i, id in enumerate(ids):
        if rs.IsBlockInstance(id):
            pt = rs.BlockInstanceInsertPoint(id)
        else:
            pt = RHINO_OBJ_DATA.get_center(id)

        ang = float(res[0])
        rs.RotateObject(id, pt,ang,vec)


if __name__ == "__main__":
    uniform_transform_geos()