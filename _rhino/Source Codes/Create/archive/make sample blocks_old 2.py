import sys
sys.path.append("..\lib")
import EnneadTab
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino # pyright: ignore
#from math import sin, cos

@EnneadTab.ERROR_HANDLE.try_catch_error
def make_sample_blocks():
    #rs.TextOut( str(rs.GroupNames()))

    #get curve
    base_crv = rs.GetObject(message = "pick base crv, open or closed. If the facade is not facing the direction you like, flip the base crv direction.", filter = rs.filter.curve, preselect = True)

    # add block to doc, here use propety box
    res = rs.PropertyListBox(items = ["Width", "Depth", "Height"], values = [1500, 200, 4500], message = "Enter sample block dimension similar to your spacing, unit in Rhino unit.", title = "EnneadTab")
    print(res)
    #\nThis should best approximate the division to be used on facade layout.\n\tWidth = horitiontal division spacing\n\tDepth = from FOG to back of mullion\n\tHeight = vertical division spacving

    W, D, H = [float(x) for x in res]

    block_name = "EA_layout block_{} x {} x {}".format(W, D, H)
    block_name, insert_pt, ref_pt = create_block(block_name, W, D, H)
    temp_block = rs.InsertBlock(block_name, insert_pt)
    directional_ref = [0,1,0]
    block_reference = [insert_pt, ref_pt, directional_ref]


    crv_segs = rs.ExplodeCurves(base_crv)

    #temporartyly set project osnap on to prevent flipping on X axis base line
    original_project_osnap_status = rs.ProjectOsnaps()
    rs.ProjectOsnaps(enable = True)

    collection = []
    print(crv_segs)
    for seg in crv_segs:
        count = rs.CurveLength(seg) / W
        pts_on_seg = rs.DivideCurve(seg, count, create_points = False)

        
        for i in range(len(pts_on_seg) - 1):
            x0 = pts_on_seg[i]
            print(x0)
            x1 = pts_on_seg[i + 1]
            param = rs.CurveClosestPoint(seg, x0)
            tangent = rs.CurveTangent(seg, param)
            print("tagent = {}".format(tangent))
            side_vector = rs.VectorRotate(tangent, 90, [0,0,1])
            print("side vector tagent = {}".format(side_vector))
            directional_ref_temp = x0 + side_vector 
            #rs.AddPoint(directional_ref_temp)
            target_reference = [x0, x1, directional_ref_temp]
            print("target_reference = {}".format(target_reference))
            #target_reference = [x0, x1]
            temp_placed_block = rs.OrientObject( temp_block, block_reference, target_reference, flags = 1 + 2)
            scale_factor = rs.Distance(x0, x1)/W
            #angle = rs.VectorAngle(tangent, [1,0,0])
            #print angle
            #scale_x = abs(scale_factor * cos(angle))
            #scale_y = abs(scale_factor * sin(angle))
            #scale_x = rs.VectorDotProduct(scale_factor * tangent, [1,0,0])
            #scale_y = rs.VectorDotProduct(scale_factor * tangent, [0,1,0])
            #scale = [scale_x, scale_y, 1]
            #print scale
            scale = [scale_factor, scale_factor, 1]
            #print scale
            temp_placed_block = rs.ScaleObject(temp_placed_block, rs.BlockInstanceInsertPoint(temp_placed_block), scale)
            collection.append(temp_placed_block)
        rs.DeleteObject(seg)

    #restore proejct osnap setting
    rs.ProjectOsnaps(enable = original_project_osnap_status)

    rs.DeleteObject(temp_block)
    rs.EnableRedraw(enable = False)
    map(lambda x: set_vertical_scale(x, H), collection)
    unique_group_name = get_unique_group_name(block_name)
    print("final unique group name = {}".format(unique_group_name))
    rs.AddGroup(group_name = unique_group_name)
    rs.AddObjectsToGroup(collection, unique_group_name)

def get_unique_group_name(initial_name):
    all_group_names = rs.GroupNames()
    if all_group_names is None:
        return initial_name
    #print "####"
    for name in all_group_names:
        #print name
        pass
    #print "***"
    #print initial_name
    final_name = initial_name
    while True:
        if final_name not in all_group_names:
            return final_name
        #print "appending _new to name"
        final_name += "_new"
    pass


def set_vertical_scale(block_instance, prefered_H):
    return
    box_corners = rs.BoundingBox(block_instance)
    current_H = box_corners[7][2] - box_corners[0][2]
    scale_factor = prefered_H /current_H
    rs.ScaleObject( block_instance, rs.BlockInstanceInsertPoint(block_instance), (1,1,scale_factor) )



def create_block(name, W, D, H):

    pt0 = [0,0,0]
    pt1 = [W, D, H]
    pts = [pt0, pt1]
    ref_pt_coord = [W, 0, 0]

    box_corners = rs.BoundingBox(pts)
    box = rs.AddBox(box_corners)
    insert_pt = rs.AddPoint(pt0)
    ref_pt = rs.AddPoint(ref_pt_coord)
    ref_line_start_pt = [W/2, 0, 0]
    ref_line_end_pt = [W/2, -W, 0]

    ref_line = rs.AddLine(ref_line_start_pt, ref_line_end_pt)
    block_contents = [box, insert_pt, ref_pt, ref_line]
    block_name = rs.AddBlock(block_contents, insert_pt, name = name, delete_input = True)
    return block_name, pt0, ref_pt_coord


if __name__ == "__main__":
    make_sample_blocks()
