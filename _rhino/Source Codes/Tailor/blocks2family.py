import Rhino # pyright: ignore
from rhinoscript.block import IsBlockInstance
import rhinoscriptsyntax as rs
import scriptcontext as sc
import os
import clr # pyright: ignore

import sys
sys.path.append("..\lib")
from EnneadTab import  DATA_FILE, ERROR_HANDLE, ENVIRONMENT, FOLDER, NOTIFICATION

sys.path.append(ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)

"""this is created fpor project 2108 OBO for Paula;s team"""


KEY_PREFIX = "BLOCKS2FAMILY"
@ERROR_HANDLE.try_catch_error
def blocks2family():
    
    # pick blocks
    blocks = rs.GetObjects("pick blocks to transfer", rs.filter.instance)
    if not blocks:
        return

    for block_name in rs.BlockNames():
        rs.RenameBlock(block_name, block_name.replace("/", ""))
    for block_id in blocks:

        for key in rs.GetUserText(block_id):
            if key == "Facade direction":
                value = rs.GetUserText(block_id, key)
                rs.SetUserText(block_id, key)
                rs.SetUserText(block_id, "Orientation", value)

            if key == "Building ID":
                value = rs.GetUserText(block_id, key)
                rs.SetUserText(block_id, key)
                rs.SetUserText(block_id, "Bldg_Id", value)



    rs.EnableRedraw(False)

    # purge old data folders
    for folder in os.listdir(FOLDER.get_EA_local_dump_folder()):
        if folder.startswith(KEY_PREFIX):
            if os.path.isdir(FOLDER.get_EA_dump_folder_file(folder)):
                FOLDER.purge_folder(FOLDER.get_EA_dump_folder_file(folder))
            else:
                os.remove(FOLDER.get_EA_dump_folder_file(folder))


    

    # make dict , block name as key, block ids from blocks as value
    block_dict = {}
    for block in blocks:
        block_instance_name =  rs.BlockInstanceName(block) 
        if block_instance_name not in block_dict:
            block_dict[block_instance_name] = []
        block_dict[block_instance_name].append(block)
        
        
    

    for block_name, block_ids in block_dict.items():

        process_block_name(block_name, block_ids)



    NOTIFICATION.messenger("Done exporting, now go to Revit and get in blocks as family.")



def process_block_name(block_name,block_ids):

    # create temp folder with geo files per layer and a json dict
    working_folder = FOLDER.get_EA_dump_folder_file(KEY_PREFIX + "_" + block_name)
    if not os.path.isdir(working_folder):
        os.makedirs(working_folder)


    
    area = export_sample_block(block_name, working_folder)

    # the json dict looks like this:
    # key = block id
    # info = dict of  () transform, other user data dict)
    temp_block = rs.InsertBlock(block_name, [0,0,0])
    contents = rs.ExplodeBlockInstance(temp_block)
    children_block = []
    for content in contents:
        if rs.IsBlockInstance(content):
            children_block.append(rs.BlockInstanceName(content))
        rs.DeleteObject(content)

    children_block.sort()
    


    
    with DATA_FILE.update_data("{}_{}.json".format(KEY_PREFIX, block_name)) as data_file:

        for block_id in block_ids:
            rs.SetUserText(block_id, "Projected_Area", area)
            rs.SetUserText(block_id, "Nest_Tiles", ",".join(children_block))
            
            data_file[str(block_id)] = {
                "transform_data": get_transform(block_id),
                "user_data": {key:rs.GetUserText(block_id, key) for key in rs.GetUserText(block_id)}
                }


def detail_matrix(xform):
    OUT = []
    for i in range(4):
        
        OUT.append( (xform[i,0], xform[i,1], xform[i,2], xform[i,3]) )
    return OUT

    
def get_transform(block):
    transform = rs.BlockInstanceXform(block)

    translation = clr.StrongBox[Rhino.Geometry.Vector3d](Rhino.Geometry.Vector3d(0,0,0))
    rotation = clr.StrongBox[Rhino.Geometry.Transform](rs.XformIdentity())
    othor = clr.StrongBox[Rhino.Geometry.Transform](rs.XformIdentity())
    diagono = clr.StrongBox[Rhino.Geometry.Vector3d](Rhino.Geometry.Vector3d(0,0,0))
    transform.DecomposeAffine(translation, rotation, othor, diagono )

    similarity = transform.IsSimilarity (0.001)
    if str(similarity) == "OrientationReversing":
        is_reflection = True
    elif str(similarity) == "OrientationPreserving":
        is_reflection = False
    else:
        is_reflection = False

    angle_x = clr.StrongBox[float](0.0)
    angle_y = clr.StrongBox[float](0.0)
    angle_z = clr.StrongBox[float](0.0)

    rotation.GetYawPitchRoll (angle_z, angle_y, angle_x)

    rotate_tuple = (float(angle_x), 
                    float(angle_y),
                    float(angle_z))
    return {
        "transform":detail_matrix(transform), 
        "rotation":rotate_tuple, 
        "is_reflection":is_reflection
        }

     
def export_sample_block(block_name, output_folder):
    #  the geo files use the new sample blockinstance at origin, exploded nesting

    
    temp_block = rs.InsertBlock(block_name, (0,0,0))
    block_objs = rs.ExplodeBlockInstance(temp_block, explode_nested_instances=True)
    block_objs = [obj for obj in block_objs if rs.IsObject(obj)]
    if not block_objs:
        return
    
    bbox = rs.BoundingBox(block_objs)
    min = bbox[0]
    max = bbox[6]
    area = (max[0] - min[0]) * (max[1] - min[1])
    area = abs(area) / 1000000# convert from sqmm to sqm


    layer_dict = {}
    for obj in block_objs:
        layer = rs.ObjectLayer(obj)
        if layer not in layer_dict:
            layer_dict[layer] = []
        layer_dict[layer].append(obj)

    for layer, objs in layer_dict.items():
        
        rs.UnselectAllObjects()
        rs.SelectObjects(objs)


        file_name_naked = layer.replace("::", "_").replace("/", "-").replace("\\", "-").replace(":", "-").replace("*", "-").replace("?", "-").replace("<", "-").replace(">", "-").replace("|", "-")
        file = "{}.3dm".format(file_name_naked)
        filepath = "{}\{}".format(output_folder, file)
        # print (filepath)
        rs.Command("!_-Export \"{}\" -Enter -Enter".format(filepath), echo = False)

        file = "{}.dwg".format(file_name_naked)
        filepath = "{}\{}".format(output_folder, file)
        rs.Command("!_-Export \"{}\" Scheme  \"2007 Solids\" -Enter -Enter".format(filepath), echo = False)
        try:
            rs.DeleteObjects(objs)
        except:
            pass

    return area

######################  main code below   #########
if __name__ == "__main__":

    blocks2family()




