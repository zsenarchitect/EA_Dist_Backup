import Rhino # pyright: ignore
import rhinoscriptsyntax as rs
import scriptcontext as sc

import sys
sys.path.append("..\lib")
import EnneadTab

def sqmm_to_sqm(area):
    return float('{:.2f}'.format(area / 1000000))

@EnneadTab.ERROR_HANDLE.try_catch_error
def stone_face_size_check():
    trash_geo = []
    # copy objs in layer "stone" that is not block, copy into trash
    checked_layers = filter(lambda x: "Generic Models_SF Stone Panel_Solid" in x, rs.LayerNames())
    for layer in checked_layers:
        print(layer)
        trash_geo.extend(rs.CopyObjects(rs.ObjectsByLayer(layer)))


    # get all block copy as trash,  explode all block, mark as trash

    #block_collection = rs.ObjectsByType(8)

    block_collection = []
    all_block_names = rs.BlockNames( sort = False )
    for block_name in all_block_names:
        block = rs. BlockInstances(block_name)
        block_collection.extend(block)


    block_collection_trash = rs.CopyObjects(block_collection)



    for block in block_collection_trash:
        exposed_objs = rs.ExplodeBlockInstance(block, explode_nested_instances = True)
        trash_geo.extend(filter(lambda x: rs.ObjectLayer(x) in checked_layers, exposed_objs))
        rs.DeleteObjects(filter(lambda x: rs.ObjectLayer(x) not in checked_layers, exposed_objs))

    #for object in trash, explode polysrf and get largest, or read surface, add text dot of area. If is is bigger than 1.5sqm, set obj color as red and not delete
    dot_collection = []
    
    red_srfs = []
    for obj in trash_geo:
        if rs.IsPolysurface(obj):
            faces = rs.ExplodePolysurfaces(obj, delete_input = True)
            faces.sort(key = lambda x: rs.Area(x), reverse = True)
            primary_face = faces.pop(0)

            rs.DeleteObjects(faces)
        elif rs.IsSurface(obj):
            primary_face = obj
        else:
            primary_face = None
            print("strange obkject: {}".format(rs.ObjectType(obj)))
            point = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(obj)
            dot = rs.AddTextDot("mesh require manual check: ", point)
            dot_collection.append(dot)
            continue


        if sqmm_to_sqm(rs.Area(primary_face)) > 1.5:
            point = EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(primary_face)
            dot = rs.AddTextDot(sqmm_to_sqm(rs.Area(primary_face)), point)
            dot_collection.append(dot)
            rs.ObjectColor(primary_face, color = rs.CreateColor([255, 0, 0]))
            red_srfs.append(primary_face)
        else:
            rs.DeleteObject(primary_face)


    # group all text dots, groups all red srf
    rs.AddObjectsToGroup(dot_collection, rs.AddGroup())
    rs.AddObjectsToGroup(red_srfs, rs.AddGroup())

    if not rs.IsLayer("Stone area check"):
        rs.AddLayer(name  = "Stone area check")
    rs.ObjectLayer(dot_collection + red_srfs, "Stone area check")

    #  delete all trash
    rs.DeleteObjects(trash_geo)



######################  main code below   #########
if __name__ == "__main__":
    rs.EnableRedraw(False)
    stone_face_size_check()

