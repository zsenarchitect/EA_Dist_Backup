import rhinoscriptsyntax as rs
import scriptcontext as sc
import Rhino # pyright: ignore
#from math import sin, cos
import sys
sys.path.append("..\lib")
import EnneadTab


@EnneadTab.ERROR_HANDLE.try_catch_error
def seating_arrange(base_crv, spacing, gap):
    #rs.TextOut( str(rs.GroupNames()))

    #get curve
    if base_crv is None:
        base_crv = rs.GetObject(message = "pick base crv, open or closed. If the facade is not facing the direction you like, flip the base crv direction.", filter = rs.filter.curve, preselect = True)

    # add block to doc, here use propety box
    if spacing is None or gap is None:
        default_spacing = EnneadTab.DATA_FILE.get_sticky_longterm("SEATING_SPACING", 1200)
        default_gap = EnneadTab.DATA_FILE.get_sticky_longterm("SEATING_GAP", 200)


        res = rs.PropertyListBox(items = ["Spacing", "Gap"], values = [default_spacing, default_gap], message = "Enter sample block dimension similar to your seating spacing, unit in Rhino unit.", title = "EnneadTab")

        #\nThis should best approximate the division to be used on facade layout.\n\tWidth = horitiontal division spacing\n\tDepth = from FOG to back of mullion\n\tHeight = vertical division spacving
        S, G = float(res[0]), float(res[1])
    else:
        S, G = spacing, gap


    W, H = S - G, 1000

    EnneadTab.DATA_FILE.set_sticky_longterm("SEATING_SPACING", S)
    EnneadTab.DATA_FILE.set_sticky_longterm("SEATING_GAP", G)


    block_name = "EA_layout seating block_{}".format(W)
    block_name, insert_pt, ref_pt = create_seating(block_name, W, H)
    temp_block = rs.InsertBlock(block_name, insert_pt)
    directional_ref = [0,1,0]
    block_reference = [insert_pt, ref_pt, directional_ref]


    crv_segs = rs.ExplodeCurves(base_crv)

    #temporartyly set project osnap on to prevent flipping on X axis base line
    #original_project_osnap_status = rs.ProjectOsnaps()
    #rs.ProjectOsnaps(enable = True)

    collection = []
    #print crv_segs
    for seg in crv_segs:
        count = rs.CurveLength(seg) / S
        pts_on_seg = rs.DivideCurve(seg, count, create_points = False)
        if rs.IsCurveClosed(seg):
            pts_on_seg.append(pts_on_seg[0])


        for i in range(len(pts_on_seg)):
            x0 = pts_on_seg[i]
            #print x0

            param = rs.CurveClosestPoint(seg, x0)
            tangent = rs.CurveTangent(seg, param)
            """
            above step is actually slightly dangerours, becasue on curve segment the location tangent is actually not the block layout local X direction. But futunealty, the directional ref temp pt used later is only used to determine the up side orientation instead of actual local Y reference for the new block. So it is all safe.
            """


            #print "tagent = {}".format(tangent)
            side_vector = rs.VectorRotate(tangent, 90, [0,0,1])
            #print "side vector tagent = {}".format(side_vector)
            directional_ref_temp = x0 + side_vector
            #rs.AddPoint(directional_ref_temp)
            target_reference = [x0, x0 + tangent, directional_ref_temp]
            #print "target_reference = {}".format(target_reference)
            #target_reference = [x0, x1]
            temp_placed_block = rs.OrientObject( temp_block, block_reference, target_reference, flags = 1 )
            """
            scale_factor = rs.Distance(x0, x1)/W
            #transform = rs.XformScale(scale_factor , x0)
            local_plane = Rhino.Geometry.Plane(x0, x1, directional_ref_temp)
            transform = Rhino.Geometry.Transform.Scale(local_plane, scale_factor, 1,1)
            print(transform)
            #rs.InsertBlock2(block_name, transform)
            #rs.TransformObject(temp_block, transform, copy=True)
            rs.TransformObject( temp_placed_block, transform, copy = False)
            """
            collection.append(temp_placed_block)
            continue

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
    #rs.ProjectOsnaps(enable = original_project_osnap_status)

    rs.DeleteObject(temp_block)
    rs.EnableRedraw(enable = False)
    #map(lambda x: set_vertical_scale(x, H), collection)
    unique_group_name = get_unique_group_name(block_name)
    print("final unique group name = {}".format(unique_group_name))
    rs.AddGroup(group_name = unique_group_name)
    rs.AddObjectsToGroup(collection, unique_group_name)

    return collection # if doing toggle display, there is no need to delete and group,this can save mermory.

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



def create_seating(name, W, H):

    pt0 = [0,0,0]
    pt2 = [-W/2,0,0]
    pt1 = [W/2, W, H]
    pts = [pt1, pt2]
    ref_pt_coord = [W/2 , 0, 0]

    box_corners = rs.BoundingBox(pts)
    box = rs.AddBox(box_corners)
    dot = rs.AddText("Sample Panel\n<{}>\nReplace block with better design.".format(name),
                    EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(box),
                    height = 0.5,
                    font = "Arial",
                    font_style = 0,
                    justification = 2 + 131072 )
    #dot = rs.AddTextDot("Sample Panel <{}>\nReplace Me".format(name), EnneadTab.RHINO.RHINO_OBJ_DATA.get_center(box))
    insert_pt = rs.AddPoint(pt0)
    ref_pt = rs.AddPoint(ref_pt_coord)
    ref_line_start_pt = pt0
    ref_line_end_pt = [0, -W, 0]

    ref_line = rs.AddLine(ref_line_start_pt, ref_line_end_pt)
    block_contents = [box, insert_pt, ref_pt, ref_line, dot]
    block_name = rs.AddBlock(block_contents, insert_pt, name = name, delete_input = True)
    return block_name, pt0, ref_pt_coord


if __name__ == "__main__":
    rs.EnableRedraw(enable = False)
    seating_arrange(base_crv = None, spacing = None, gap = None)
