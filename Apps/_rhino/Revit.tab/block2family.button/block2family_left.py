__title__ = "Block2Family"
__doc__ = "Convert rhino blocks to revit families and place them in project. This tool different from standard Rhino2Revit because you do not need to manage family creation and it can batch process."
__is_popular__ = True
import Rhino # pyright: ignore
import rhinoscriptsyntax as rs # pyright: ignore
import scriptcontext as sc # pyright: ignore
import os
import shutil
import clr # pyright: ignore
from EnneadTab import ERROR_HANDLE, LOG, DATA_FILE, NOTIFICATION, FOLDER, ENVIRONMENT

B2F_KEY_PREFIX = "BLOCKS2FAMILY"

import os
import sys
current_dir = os.path.dirname(__file__)
shape2revit_dir = os.path.abspath(os.path.join(current_dir, '..', 'shape2revit.button'))
if shape2revit_dir not in sys.path:
    sys.path.insert(0, shape2revit_dir)
import shape2revit_left as S2R

@LOG.log(__file__, __title__)
@ERROR_HANDLE.try_catch_error()
def block2family(blocks = None):

    blocks = blocks or rs.GetObjects("pick blocks to transfer", rs.filter.instance)
    if not blocks:
        return

    for block_name in rs.BlockNames():
        rs.RenameBlock(block_name, block_name.replace("/", ""))
    # for block_id in blocks:

    #     for key in rs.GetUserText(block_id):
    #         if key == "Facade direction":
    #             value = rs.GetUserText(block_id, key)
    #             rs.SetUserText(block_id, key)
    #             rs.SetUserText(block_id, "Orientation", value)

    #         if key == "Building ID":
    #             value = rs.GetUserText(block_id, key)
    #             rs.SetUserText(block_id, key)
    #             rs.SetUserText(block_id, "Bldg_Id", value)



    rs.EnableRedraw(False)

    # purge old data folders
    for folder in os.listdir(FOLDER.DUMP_FOLDER):
        if folder.startswith(B2F_KEY_PREFIX):
            full_path = os.path.join(FOLDER.DUMP_FOLDER, folder)
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)


    

    # make dict , block name as key, block ids from blocks as value
    block_dict = {}
    for block in blocks:
        block_instance_name =  rs.BlockInstanceName(block) 
        if block_instance_name not in block_dict:
            block_dict[block_instance_name] = []
        block_dict[block_instance_name].append(block)
        
        
    
    rs.StatusBarProgressMeterShow(label = "Total Blocks to process <{}> ".format(len(blocks)), lower = 0, upper = len(blocks), embed_label = True, show_percent = True)
    for i, (block_name, block_ids) in enumerate(block_dict.items()):
        rs.StatusBarProgressMeterUpdate(position = len(block_ids), absolute = True)
        process_block_name(block_name, block_ids)
    rs.StatusBarProgressMeterHide()


    NOTIFICATION.messenger("Done exporting, now go to Revit and get in blocks as family.")



def process_block_name(block_name,block_ids):

    # Check for illegal Windows filename characters
    illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    for char in illegal_chars:
        if char in block_name:
            NOTIFICATION.messenger("Block name contains illegal character '{}'.\nPlease rename block to use valid filename characters and try again.".format(char))
            return
            
    working_folder = FOLDER.get_local_dump_folder_folder(B2F_KEY_PREFIX + "_" + block_name)
    
    if not os.path.isdir(working_folder):
        os.makedirs(working_folder)


    
    area, width, height = export_sample_block(block_name, working_folder)

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
    


    
    with DATA_FILE.update_data("{}_{}".format(B2F_KEY_PREFIX, block_name)) as data:
        geo_data = {}
        for block_id in block_ids:
            rs.SetUserText(block_id, "Projected_Area", area)
            rs.SetUserText(block_id, "Panel_Width", width)
            rs.SetUserText(block_id, "Panel_Height", height)

            if S2R.S2F_PREFIX in rs.BlockInstanceName(block_id):
                key = rs.BlockInstanceName(block_id).replace(S2R.S2F_PREFIX, "")
            else:
                key = str(block_id)
            geo_data[key] = {
                "transform_data": get_transform(block_id),
                "user_data": {key:rs.GetUserText(block_id, key) for key in rs.GetUserText(block_id)}
                }
        
        data["unit"] = rs.UnitSystemName(abbreviate=True)    
        # ft, in, m, mm

        
        data["geo_data"] = geo_data


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
    
    # convert from any unit to sqft
    area = abs(area)# * rs.UnitScale(9)*rs.UnitScale(9)
    width = (max[0] - min[0])# * rs.UnitScale(9)
    height = (max[1] - min[1])# * rs.UnitScale(9)


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


    return area, width, height


if __name__ == "__main__":
    block2family()
